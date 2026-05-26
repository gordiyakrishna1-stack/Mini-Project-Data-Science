"""Plotly Dash application for trend analysis and outbreak prediction."""

from pathlib import Path
import pandas as pd
import numpy as np
import dash
from dash import dcc, html, Input, Output
import dash_table
import plotly.express as px
import xgboost as xgb
from sklearn.preprocessing import LabelEncoder, MinMaxScaler
from tensorflow.keras.models import load_model

from config import OUTPUT_DIR

WAREHOUSE_DIR = OUTPUT_DIR / "warehouse"
GOLD_DIR = WAREHOUSE_DIR / "gold"
SILVER_DIR = WAREHOUSE_DIR / "silver"
MODEL_DIR = WAREHOUSE_DIR / "models"


def load_gold_fact():
    fact_path = GOLD_DIR / "Fact_Cases.csv"
    if not fact_path.exists():
        raise FileNotFoundError(f"Gold fact table not found: {fact_path}. Run gold_aggregate.py first.")
    return pd.read_csv(fact_path)


def load_silver_data():
    silver_files = list(SILVER_DIR.glob("*_silver.csv"))
    if not silver_files:
        raise FileNotFoundError("Silver data not found. Run silver_transform.py first.")
    return pd.read_csv(silver_files[0])


def get_lstm_forecast(disease: str, df_silver: pd.DataFrame):
    model_path = MODEL_DIR / f"lstm_{disease.lower().replace(' ', '_')}_model.h5"
    if not model_path.exists():
        return None, None

    df = df_silver.copy()
    df = df[df['Disease'].str.strip().str.title() == disease.title()]
    df = df.sort_values(['Year', 'Month'])
    monthly = df.groupby(['Year', 'Month'])['Reported_Cases'].sum().reset_index()
    if monthly.empty:
        return None, None

    cases = monthly['Reported_Cases'].astype(float).values.reshape(-1, 1)
    scaler = MinMaxScaler()
    cases_scaled = scaler.fit_transform(cases)

    model = load_model(model_path)
    look_back = model.input_shape[1]
    if len(cases_scaled) < look_back:
        return None, monthly

    sequence = cases_scaled[-look_back:].reshape(1, look_back, 1)
    forecast_scaled = model.predict(sequence, verbose=0)
    forecast = scaler.inverse_transform(forecast_scaled)[0, 0]
    return float(forecast), monthly


def prepare_risk_features(df: pd.DataFrame):
    df = df.copy()
    for col in ['Disease', 'Province', 'Season', 'Gender', 'Age_Group']:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().str.title()

    feature_cols = [
        'Disease', 'Province', 'Season', 'Gender', 'Age_Group',
        'Reported_Cases', 'Deaths', 'Recovered', 'Hospitalized', 'ICU_Admission',
        'Vaccinated', 'CFR', 'Recovery_Rate', 'Hospitalization_Rate', 'Year', 'Month'
    ]

    df = df.dropna(subset=feature_cols)
    X = pd.DataFrame()
    for col in feature_cols:
        if col in ['Disease', 'Province', 'Season', 'Gender', 'Age_Group']:
            le = LabelEncoder()
            X[col + '_enc'] = le.fit_transform(df[col])
        else:
            X[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    return X, df


def get_xgboost_predictions(df_silver: pd.DataFrame):
    model_path = MODEL_DIR / "xgboost_risk_model.json"
    if not model_path.exists():
        return None

    X, df = prepare_risk_features(df_silver)
    if X.empty:
        return None

    model = xgb.Booster()
    model.load_model(str(model_path))
    dmatrix = xgb.DMatrix(X)
    y_pred = np.argmax(model.predict(dmatrix), axis=1)
    df = df.reset_index(drop=True)
    df['Risk_Label'] = y_pred
    df['Risk_Label_Text'] = df['Risk_Label'].map({0: 'Low', 1: 'Medium', 2: 'High'})
    return df


def create_app(df_gold: pd.DataFrame, df_silver: pd.DataFrame):
    df_gold['Month_Year'] = df_gold['Month'].astype(str).str.zfill(2) + '-' + df_gold['Year'].astype(str)
    df_gold['Month_Year'] = pd.to_datetime(df_gold['Month_Year'], format='%m-%Y')
    disease_options = [{'label': str(x), 'value': str(x)} for x in sorted(df_silver['Disease'].dropna().unique())]

    risk_predictions = get_xgboost_predictions(df_silver)
    if risk_predictions is not None:
        risk_by_province = risk_predictions.groupby(['Province_ID', 'Risk_Label_Text']).size().reset_index(name='Count')
        risk_by_province = risk_by_province.sort_values(['Province_ID', 'Risk_Label_Text'])
        risk_table_data = risk_predictions.sort_values(['Risk_Label', 'Reported_Cases'], ascending=[False, False]).head(20)
    else:
        risk_by_province = pd.DataFrame(columns=['Province_ID', 'Risk_Label_Text', 'Count'])
        risk_table_data = pd.DataFrame(columns=['Disease', 'Province', 'Reported_Cases', 'CFR', 'Risk_Label_Text'])

    app = dash.Dash(__name__)
    app.layout = html.Div([
        html.H1('Epidemiological Dashboard — Trend Analysis & Outbreak Prediction'),
        html.P('Select a disease to view trend analysis, next-month forecasts, and outbreak risk insights.', style={'color': '#4d4d4d'}),

        html.Div(id='kpi-cards', style={
            'display': 'grid',
            'gridTemplateColumns': 'repeat(auto-fit, minmax(220px, 1fr))',
            'gap': '18px',
            'marginTop': '24px'
        }),

        html.Div([
            html.Div([
                html.Label('Choose Disease for Trend & Forecast:', style={'fontWeight': '700', 'marginBottom': '6px'}),
                dcc.Dropdown(id='disease-dropdown', options=disease_options, value=disease_options[0]['value'] if disease_options else None, clearable=False, style={'width': '100%'})
            ], style={'width': '100%', 'maxWidth': '420px'})
        ], style={'marginTop': '24px', 'marginBottom': '18px'}),

        dcc.Tabs(id='tabs', value='tab-trend', children=[
            dcc.Tab(label='Trend Analysis', value='tab-trend'),
            dcc.Tab(label='Outbreak Prediction', value='tab-risk'),
            dcc.Tab(label='Model Summary', value='tab-summary')
        ]),

        html.Div(id='tab-content', style={'marginTop': '22px'})
    ], style={'margin': '2rem', 'fontFamily': 'Segoe UI, Arial, sans-serif', 'backgroundColor': '#f7f8fb'})

    @app.callback(
        Output('kpi-cards', 'children'),
        Input('disease-dropdown', 'value')
    )
    def update_kpis(selected_disease):
        total_cases = int(df_gold['Reported_Cases'].sum())
        total_deaths = int(df_gold['Deaths'].sum())
        total_recovered = int(df_gold['Recovered'].sum())
        vaccinated_pct = (df_silver['Vaccinated'].sum() / max(len(df_silver), 1)) * 100
        high_risk_count = int(risk_predictions[risk_predictions['Risk_Label_Text'] == 'High'].shape[0]) if risk_predictions is not None else 0
        top_risk_province = 'N/A'
        if risk_predictions is not None and not risk_predictions.empty:
            top_risk_province_list = risk_predictions[risk_predictions['Risk_Label_Text'] == 'High'].groupby('Province').size().nlargest(1).index.tolist()
            top_risk_province = top_risk_province_list[0] if top_risk_province_list else 'N/A'

        # LSTM forecast for selected disease
        forecast, _ = get_lstm_forecast(selected_disease, df_silver)
        forecast_val = f"{forecast:.0f}" if forecast is not None else "N/A"

        cards = [
            {'label': 'Total Cases', 'value': f'{total_cases:,}', 'icon': '📈'},
            {'label': 'Total Deaths', 'value': f'{total_deaths:,}', 'icon': '💀'},
            {'label': 'Total Recovered', 'value': f'{total_recovered:,}', 'icon': '✅'},
            {'label': 'Vaccinated Records', 'value': f'{vaccinated_pct:.1f}%', 'icon': '💉'},
            {'label': 'LSTM Next-Month Forecast', 'value': forecast_val, 'icon': '🔮'},
            {'label': 'High Outbreak Alerts', 'value': f'{high_risk_count:,}', 'icon': '🚨'},
            {'label': 'Top Risk Province', 'value': top_risk_province, 'icon': '📍'}
        ]

        return [
            html.Div([
                html.Div(card['icon'], style={'fontSize': '1.8rem', 'marginBottom': '8px'}),
                html.Div(card['label'], style={'fontSize': '0.95rem', 'color': '#5e5e5e', 'marginBottom': '10px'}),
                html.Div(card['value'], style={'fontSize': '1.9rem', 'fontWeight': '700', 'color': '#1f2937'})
            ], style={
                'background': 'white',
                'padding': '22px',
                'borderRadius': '16px',
                'boxShadow': '0 18px 36px rgba(15, 23, 42, 0.08)',
                'minHeight': '140px'
            })
            for card in cards
        ]

    @app.callback(
        Output('tab-content', 'children'),
        Input('tabs', 'value'),
        Input('disease-dropdown', 'value')
    )
    def render_tab(tab, selected_disease):
        if tab == 'tab-trend':
            monthly = df_gold.groupby(['Month_Year', 'Disease_ID'])['Reported_Cases'].sum().reset_index()
            trend_fig = px.line(
                monthly.sort_values('Month_Year'),
                x='Month_Year', y='Reported_Cases', color='Disease_ID', title='Monthly Case Trend by Disease ID', markers=True
            )
            trend_fig.update_layout(legend_title_text='Disease ID', hovermode='x unified', plot_bgcolor='#ffffff')

            forecast, monthly_series = get_lstm_forecast(selected_disease, df_silver)
            forecast_text = html.Div([
                html.P('Live LSTM forecast not available. Run train_lstm.py to generate the forecast model.', style={'marginBottom': '0', 'color': '#4a5568'})
            ])
            forecast_fig = None
            if forecast is not None and monthly_series is not None:
                monthly_series['Month_Year'] = monthly_series['Month'].astype(str).str.zfill(2) + '-' + monthly_series['Year'].astype(str)
                monthly_series['Month_Year'] = pd.to_datetime(monthly_series['Month_Year'], format='%m-%Y')
                forecast_fig = px.line(
                    monthly_series,
                    x='Month_Year', y='Reported_Cases', title=f'{selected_disease} Case Trend with Next-Month Forecast', markers=True
                )
                forecast_fig.add_scatter(
                    x=[monthly_series['Month_Year'].max() + pd.DateOffset(months=1)],
                    y=[forecast],
                    mode='markers+text',
                    name='Forecast',
                    text=[f'Forecast: {forecast:.0f}'],
                    textposition='top center'
                )
                forecast_text = html.Div([
                    html.P(f'Next-month forecast for {selected_disease}: {forecast:.0f} reported cases.', style={'fontWeight': '700', 'marginBottom': '6px'}),
                    html.P('Forecast generated by the trained LSTM model using historical monthly case patterns.', style={'color': '#4a5568'})
                ])

            selected_df = df_silver[df_silver['Disease'].str.strip().str.title() == selected_disease.title()]
            season_fig = None
            if not selected_df.empty and 'Season' in selected_df.columns:
                season_fig = px.bar(
                    selected_df.groupby('Season')['Reported_Cases'].sum().reset_index().sort_values('Reported_Cases', ascending=False),
                    x='Season', y='Reported_Cases', title=f'Seasonal Case Distribution for {selected_disease}', color='Season'
                )

            return html.Div([
                html.H2('Trend Analysis'),
                html.Div([dcc.Graph(id='trend-graph', figure=trend_fig)], style={'marginBottom': '2rem'}),
                html.Div([
                    html.Div([
                        html.H3('Forecast Summary', style={'marginBottom': '12px'}),
                        forecast_text
                    ], style={'background': '#ffffff', 'padding': '22px', 'borderRadius': '16px', 'border': '1px solid #e2e8f0'})
                ], style={'marginBottom': '2rem'}),
                html.Div([
                    dcc.Graph(id='forecast-graph', figure=forecast_fig) if forecast_fig is not None else html.Div(),
                    dcc.Graph(id='season-graph', figure=season_fig) if season_fig is not None else html.Div()
                ])
            ], style={'padding': '0 8px'})

        if tab == 'tab-risk':
            if risk_predictions is None:
                return html.Div([
                    html.H2('Outbreak Prediction'),
                    html.P('XGBoost risk model not found. Run train_xgboost.py first.', style={'fontSize': '1rem', 'color': '#333'})
                ])

            risk_fig = px.bar(
                risk_by_province,
                x='Province', y='Count', color='Risk_Label_Text',
                title='Predicted Outbreak Risk Distribution by Province',
                labels={'Province': 'Province', 'Count': 'Record Count', 'Risk_Label_Text': 'Risk Level'}
            )
            risk_fig.update_layout(legend_title_text='Risk Level', hovermode='x unified', plot_bgcolor='#ffffff')

            top_alerts = risk_predictions[risk_predictions['Risk_Label_Text'] == 'High']
            alert_summary = top_alerts.groupby(['Province', 'Disease']).size().reset_index(name='HighRiskCases')
            alert_summary = alert_summary.sort_values('HighRiskCases', ascending=False).head(8)

            return html.Div([
                html.H2('Outbreak Prediction'),
                html.Div([
                    html.Div([
                        html.H3('Live Prediction Alerts', style={'marginBottom': '12px'}),
                        html.P(f"High-risk records flagged: {len(top_alerts):,}", style={'fontSize': '1rem', 'marginBottom': '8px'}),
                        html.P('Review province-disease combinations with elevated outbreak risk and prioritize monitoring.', style={'color': '#555'}),
                        html.Ul([
                            html.Li(f"{row.Province} ({row.Disease}): {row.HighRiskCases} high-risk cases") for _, row in alert_summary.iterrows()
                        ], style={'color': '#b91c1c', 'fontWeight': '600', 'marginTop': '10px'})
                    ], style={'padding': '22px', 'background': '#fff5f3', 'borderRadius': '16px', 'border': '1px solid #fed7d7'})
                ], style={'marginBottom': '2rem'}),
                dcc.Graph(id='risk-graph', figure=risk_fig),
                html.H3('Top High-Risk Province/Disease Combinations', style={'marginTop': '2rem'}),
                dash_table.DataTable(
                    columns=[{'name': col, 'id': col} for col in alert_summary.columns],
                    data=alert_summary.to_dict('records'),
                    page_size=8,
                    style_table={'overflowX': 'auto'},
                    style_header={'backgroundColor': '#f3f4f6', 'fontWeight': '600'},
                    style_cell={'textAlign': 'left', 'padding': '8px'}
                ),
                html.H3('Detailed Risk Predictions', style={'marginTop': '2rem'}),
                dash_table.DataTable(
                    columns=[{'name': col, 'id': col} for col in risk_table_data.columns],
                    data=risk_table_data.to_dict('records'),
                    page_size=10,
                    style_table={'overflowX': 'auto'},
                    style_header={'backgroundColor': '#f3f4f6', 'fontWeight': '600'},
                    style_cell={'textAlign': 'left', 'padding': '8px'}
                )
            ], style={'padding': '0 8px'})

        if tab == 'tab-summary':
            lstm_models = list(MODEL_DIR.glob('lstm_*_model.h5'))
            xgb_model = MODEL_DIR / 'xgboost_risk_model.json'
            model_files = [
                {'Model': 'LSTM Forecast', 'Status': 'Ready' if lstm_models else 'Missing', 'Path': str(lstm_models[0]) if lstm_models else 'Missing'},
                {'Model': 'XGBoost Risk', 'Status': 'Ready' if xgb_model.exists() else 'Missing', 'Path': str(xgb_model)}
            ]

            return html.Div([
                html.H2('Model Training & Forecasting Summary'),
                html.P('Review the trained machine learning models used for outbreak risk classification and next-month trend forecasting.', style={'color': '#4a5568'}),
                dash_table.DataTable(
                    columns=[{'name': col, 'id': col} for col in model_files[0].keys()],
                    data=model_files,
                    style_table={'overflowX': 'auto'},
                    style_header={'backgroundColor': '#f3f4f6', 'fontWeight': '600'},
                    style_cell={'textAlign': 'left', 'padding': '10px'}
                ),
                html.Div([
                    html.H3('Training & Deployment Notes', style={'marginTop': '1.8rem'}),
                    html.Ul([
                        html.Li('Run train_lstm.py to generate the next-month case forecast model.'),
                        html.Li('Run train_xgboost.py to generate the outbreak risk prediction model.'),
                        html.Li('Run model_training_sheet.py after training to export performance metrics and compare models.'),
                        html.Li('If a model is missing, review the logs and the corresponding training script output files.')
                    ], style={'color': '#333', 'lineHeight': '1.7'})
                ], style={'padding': '22px', 'backgroundColor': '#ffffff', 'borderRadius': '16px', 'border': '1px solid #e2e8f0'})
            ], style={'padding': '0 8px'})

        return html.Div()

    return app


if __name__ == '__main__':
    df_gold = load_gold_fact()
    df_silver = load_silver_data()
    app = create_app(df_gold, df_silver)
    app.run_server(debug=True, port=8050)
