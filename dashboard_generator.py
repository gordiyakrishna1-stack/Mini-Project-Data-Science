"""
Interactive Dashboard Generator Module
Creates HTML dashboards with interactive Plotly visualizations
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime
from pathlib import Path
from config import OUTPUT_DIR, VERBOSE

WAREHOUSE_DIR = OUTPUT_DIR / "warehouse"


class DashboardGenerator:
    """Generates interactive HTML dashboards with Plotly"""
    
    def __init__(self, df):
        self.df = df
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.color_palette = px.colors.qualitative.Set2
        
    def create_disease_dashboard(self):
        """Create interactive disease analysis dashboard"""
        print("\nGenerating disease analysis dashboard...")
        
        # Prepare data
        disease_stats = []
        for disease in self.df['Disease'].unique():
            disease_df = self.df[self.df['Disease'] == disease]
            disease_stats.append({
                'Disease': disease,
                'Cases': disease_df['Reported_Cases'].sum(),
                'Deaths': disease_df['Deaths'].sum(),
                'Recovered': disease_df['Recovered'].sum(),
                'Hospitalized': disease_df['Hospitalized'].sum(),
                'CFR': (disease_df['Deaths'].sum() / (disease_df['Reported_Cases'].sum() + 1) * 100)
            })
        
        disease_df = pd.DataFrame(disease_stats).sort_values('CFR', ascending=False)
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=("Case Fatality Rate by Disease", "Total Cases by Disease",
                          "Deaths by Disease", "Recovery Rate by Disease"),
            specs=[[{"type": "bar"}, {"type": "bar"}],
                   [{"type": "bar"}, {"type": "bar"}]]
        )
        
        # CFR plot
        fig.add_trace(
            go.Bar(x=disease_df['Disease'], y=disease_df['CFR'], 
                   marker_color='#e74c3c', name='CFR %', hovertemplate='%{x}<br>CFR: %{y:.2f}%'),
            row=1, col=1
        )
        
        # Cases plot
        fig.add_trace(
            go.Bar(x=disease_df['Disease'], y=disease_df['Cases'], 
                   marker_color='#3498db', name='Cases', hovertemplate='%{x}<br>Cases: %{y:,}'),
            row=1, col=2
        )
        
        # Deaths plot
        fig.add_trace(
            go.Bar(x=disease_df['Disease'], y=disease_df['Deaths'], 
                   marker_color='#c0392b', name='Deaths', hovertemplate='%{x}<br>Deaths: %{y:,}'),
            row=2, col=1
        )
        
        # Recovery rate
        disease_df['Recovery%'] = (disease_df['Recovered'] / disease_df['Cases'] * 100)
        fig.add_trace(
            go.Bar(x=disease_df['Disease'], y=disease_df['Recovery%'], 
                   marker_color='#27ae60', name='Recovery %', hovertemplate='%{x}<br>Recovery: %{y:.2f}%'),
            row=2, col=2
        )
        
        fig.update_layout(
            height=800,
            title_text="<b>Disease Analysis Dashboard</b>",
            showlegend=False,
            hovermode='x unified',
            template='plotly_white'
        )
        
        # Save
        html_file = OUTPUT_DIR / 'dashboard_disease_analysis.html'
        fig.write_html(str(html_file))
        
        if VERBOSE:
            print(f"✓ Disease dashboard saved: {html_file}")
        
        return html_file
    
    def create_geographic_dashboard(self):
        """Create interactive geographic analysis dashboard"""
        print("Generating geographic analysis dashboard...")
        
        # Aggregate by province
        prov_stats = []
        for prov in self.df['Province'].unique():
            prov_df = self.df[self.df['Province'] == prov]
            prov_stats.append({
                'Province': prov,
                'Cases': prov_df['Reported_Cases'].sum(),
                'Deaths': prov_df['Deaths'].sum(),
                'Urban': len(prov_df[prov_df['Urban_Rural'] == 'Urban']),
                'Rural': len(prov_df[prov_df['Urban_Rural'] == 'Rural']),
                'CFR': (prov_df['Deaths'].sum() / (prov_df['Reported_Cases'].sum() + 1) * 100)
            })
        
        prov_df_stats = pd.DataFrame(prov_stats).sort_values('Cases', ascending=False)
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=("Top 15 Provinces by Case Burden", "CFR by Province",
                          "Urban vs Rural Cases", "Deaths by Province"),
            specs=[[{"type": "bar"}, {"type": "scatter"}],
                   [{"type": "bar"}, {"type": "bar"}]]
        )
        
        top_prov = prov_df_stats.head(15)
        
        # Top provinces
        fig.add_trace(
            go.Bar(x=top_prov['Province'], y=top_prov['Cases'],
                   marker_color='#3498db', name='Cases', hovertemplate='%{x}<br>Cases: %{y:,}'),
            row=1, col=1
        )
        
        # CFR scatter
        fig.add_trace(
            go.Scatter(x=prov_df_stats['Province'], y=prov_df_stats['CFR'],
                      mode='markers', marker=dict(size=10, color='#e74c3c'),
                      name='CFR %', hovertemplate='%{x}<br>CFR: %{y:.2f}%'),
            row=1, col=2
        )
        
        # Urban vs Rural
        fig.add_trace(
            go.Bar(x=top_prov['Province'], y=top_prov['Urban'],
                   marker_color='#f39c12', name='Urban',
                   hovertemplate='%{x}<br>Urban: %{y:,}'),
            row=2, col=1
        )
        
        fig.add_trace(
            go.Bar(x=top_prov['Province'], y=top_prov['Rural'],
                   marker_color='#27ae60', name='Rural',
                   hovertemplate='%{x}<br>Rural: %{y:,}'),
            row=2, col=1
        )
        
        # Deaths by province
        fig.add_trace(
            go.Bar(x=top_prov['Province'], y=top_prov['Deaths'],
                   marker_color='#c0392b', name='Deaths',
                   hovertemplate='%{x}<br>Deaths: %{y:,}'),
            row=2, col=2
        )
        
        fig.update_layout(
            height=800,
            title_text="<b>Geographic Analysis Dashboard</b>",
            hovermode='x unified',
            template='plotly_white'
        )
        
        # Save
        html_file = OUTPUT_DIR / 'dashboard_geographic_analysis.html'
        fig.write_html(str(html_file))
        
        if VERBOSE:
            print(f"✓ Geographic dashboard saved: {html_file}")
        
        return html_file
    
    def create_demographic_dashboard(self):
        """Create interactive demographic analysis dashboard"""
        print("Generating demographic analysis dashboard...")
        
        # Prepare demographic data
        demo_data = []
        for age_group in ['0-14', '15-24', '25-44', '45-64', '65+']:
            for gender in ['Male', 'Female']:
                subset_df = self.df[(self.df['Age_Group'] == age_group) & (self.df['Gender'] == gender)]
                if len(subset_df) > 0:
                    demo_data.append({
                        'Age_Group': age_group,
                        'Gender': gender,
                        'Cases': subset_df['Reported_Cases'].sum(),
                        'Deaths': subset_df['Deaths'].sum(),
                        'CFR': (subset_df['Deaths'].sum() / (subset_df['Reported_Cases'].sum() + 1) * 100)
                    })
        
        demo_df = pd.DataFrame(demo_data)
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=("Cases by Age Group and Gender", "Deaths by Age Group",
                          "CFR by Age Group", "Mortality Rate by Gender"),
            specs=[[{"type": "bar"}, {"type": "bar"}],
                   [{"type": "scatter"}, {"type": "bar"}]]
        )
        
        # Cases by age and gender
        for gender in ['Male', 'Female']:
            gender_data = demo_df[demo_df['Gender'] == gender]
            color = '#FF69B4' if gender == 'Female' else '#4169E1'
            fig.add_trace(
                go.Bar(x=gender_data['Age_Group'], y=gender_data['Cases'],
                       marker_color=color, name=gender,
                       hovertemplate='%{x}<br>' + gender + ': %{y:,}'),
                row=1, col=1
            )
        
        # Deaths by age group
        death_by_age = demo_df.groupby('Age_Group')['Deaths'].sum().reset_index()
        fig.add_trace(
            go.Bar(x=death_by_age['Age_Group'], y=death_by_age['Deaths'],
                   marker_color='#c0392b', name='Deaths',
                   hovertemplate='%{x}<br>Deaths: %{y:,}'),
            row=1, col=2
        )
        
        # CFR by age group
        cfr_by_age = demo_df.groupby('Age_Group')['CFR'].mean().reset_index()
        fig.add_trace(
            go.Scatter(x=cfr_by_age['Age_Group'], y=cfr_by_age['CFR'],
                      mode='lines+markers', marker=dict(size=10, color='#e74c3c'),
                      name='CFR', hovertemplate='%{x}<br>CFR: %{y:.2f}%'),
            row=2, col=1
        )
        
        # Mortality by gender
        gender_mort = demo_df.groupby('Gender')['Deaths'].sum().reset_index()
        fig.add_trace(
            go.Bar(x=gender_mort['Gender'], y=gender_mort['Deaths'],
                   marker_color=['#FF69B4', '#4169E1'],
                   name='Deaths by Gender',
                   hovertemplate='%{x}<br>Deaths: %{y:,}'),
            row=2, col=2
        )
        
        fig.update_layout(
            height=800,
            title_text="<b>Demographic Analysis Dashboard</b>",
            showlegend=True,
            hovermode='x unified',
            template='plotly_white'
        )
        
        # Save
        html_file = OUTPUT_DIR / 'dashboard_demographic_analysis.html'
        fig.write_html(str(html_file))
        
        if VERBOSE:
            print(f"✓ Demographic dashboard saved: {html_file}")
        
        return html_file
    
    def create_temporal_dashboard(self):
        """Create interactive temporal analysis dashboard"""
        print("Generating temporal analysis dashboard...")
        
        # Aggregate by month and year
        temporal_data = []
        for year in sorted(self.df['Year'].unique()):
            for month in sorted(self.df[self.df['Year'] == year]['Month'].unique()):
                period_df = self.df[(self.df['Year'] == year) & (self.df['Month'] == month)]
                temporal_data.append({
                    'Date': f'{year}-{int(month):02d}',
                    'Cases': period_df['Reported_Cases'].sum(),
                    'Deaths': period_df['Deaths'].sum(),
                    'Year': year,
                    'Month': int(month)
                })
        
        temporal_df = pd.DataFrame(temporal_data).sort_values(['Year', 'Month'])
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=("Monthly Case Trends (2018-2022)", "Monthly Death Trends (2018-2022)"),
            specs=[[{"secondary_y": True}],
                   [{"secondary_y": True}]]
        )
        
        # Cases line
        fig.add_trace(
            go.Scatter(x=temporal_df['Date'], y=temporal_df['Cases'],
                      mode='lines+markers', name='Cases',
                      marker_color='#3498db', hovertemplate='%{x}<br>Cases: %{y:,}'),
            row=1, col=1, secondary_y=False
        )
        
        # Deaths line
        fig.add_trace(
            go.Scatter(x=temporal_df['Date'], y=temporal_df['Deaths'],
                      mode='lines+markers', name='Deaths',
                      marker_color='#c0392b', hovertemplate='%{x}<br>Deaths: %{y:,}'),
            row=1, col=1, secondary_y=True
        )
        
        # Yearly comparison
        yearly_data = []
        for year in sorted(self.df['Year'].unique()):
            year_df = self.df[self.df['Year'] == year]
            yearly_data.append({
                'Year': str(year),
                'Cases': year_df['Reported_Cases'].sum(),
                'Deaths': year_df['Deaths'].sum()
            })
        
        yearly_df = pd.DataFrame(yearly_data)
        
        fig.add_trace(
            go.Bar(x=yearly_df['Year'], y=yearly_df['Cases'],
                   marker_color='#3498db', name='Yearly Cases',
                   hovertemplate='%{x}<br>Cases: %{y:,}'),
            row=2, col=1, secondary_y=False
        )
        
        fig.add_trace(
            go.Bar(x=yearly_df['Year'], y=yearly_df['Deaths'],
                   marker_color='#c0392b', name='Yearly Deaths',
                   hovertemplate='%{x}<br>Deaths: %{y:,}'),
            row=2, col=1, secondary_y=True
        )
        
        fig.update_yaxes(title_text="Cases", row=1, col=1, secondary_y=False)
        fig.update_yaxes(title_text="Deaths", row=1, col=1, secondary_y=True)
        
        fig.update_layout(
            height=800,
            title_text="<b>Temporal Analysis Dashboard</b>",
            hovermode='x unified',
            template='plotly_white'
        )
        
        # Save
        html_file = OUTPUT_DIR / 'dashboard_temporal_analysis.html'
        fig.write_html(str(html_file))
        
        if VERBOSE:
            print(f"✓ Temporal dashboard saved: {html_file}")
        
        return html_file
    
    def create_vaccination_dashboard(self):
        """Create interactive vaccination analysis dashboard"""
        print("Generating vaccination analysis dashboard...")
        
        # Vaccination analysis
        vaccinated_df = self.df[self.df['Vaccinated'] == 1]
        unvaccinated_df = self.df[self.df['Vaccinated'] == 0]
        
        vac_stats = {
            'Status': ['Vaccinated', 'Unvaccinated'],
            'Cases': [vaccinated_df['Reported_Cases'].sum(), unvaccinated_df['Reported_Cases'].sum()],
            'Deaths': [vaccinated_df['Deaths'].sum(), unvaccinated_df['Deaths'].sum()],
            'Recovered': [vaccinated_df['Recovered'].sum(), unvaccinated_df['Recovered'].sum()],
            'Hospitalized': [vaccinated_df['Hospitalized'].sum(), unvaccinated_df['Hospitalized'].sum()]
        }
        
        vac_df = pd.DataFrame(vac_stats)
        vac_df['CFR'] = (vac_df['Deaths'] / (vac_df['Cases'] + 1) * 100)
        vac_df['Recovery%'] = (vac_df['Recovered'] / (vac_df['Cases'] + 1) * 100)
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=("Cases: Vaccinated vs Unvaccinated", "Deaths Comparison",
                          "CFR Comparison", "Recovery Rate Comparison"),
            specs=[[{"type": "pie"}, {"type": "bar"}],
                   [{"type": "bar"}, {"type": "bar"}]]
        )
        
        # Pie chart for cases
        fig.add_trace(
            go.Pie(labels=vac_df['Status'], values=vac_df['Cases'],
                   marker=dict(colors=['#2ecc71', '#e74c3c']),
                   name='Cases'),
            row=1, col=1
        )
        
        # Deaths comparison
        fig.add_trace(
            go.Bar(x=vac_df['Status'], y=vac_df['Deaths'],
                   marker_color=['#2ecc71', '#e74c3c'],
                   name='Deaths', hovertemplate='%{x}<br>Deaths: %{y:,}'),
            row=1, col=2
        )
        
        # CFR comparison
        fig.add_trace(
            go.Bar(x=vac_df['Status'], y=vac_df['CFR'],
                   marker_color=['#2ecc71', '#e74c3c'],
                   name='CFR %', hovertemplate='%{x}<br>CFR: %{y:.2f}%'),
            row=2, col=1
        )
        
        # Recovery rate comparison
        fig.add_trace(
            go.Bar(x=vac_df['Status'], y=vac_df['Recovery%'],
                   marker_color=['#2ecc71', '#e74c3c'],
                   name='Recovery %', hovertemplate='%{x}<br>Recovery: %{y:.2f}%'),
            row=2, col=2
        )
        
        fig.update_layout(
            height=800,
            title_text="<b>Vaccination Impact Dashboard</b>",
            showlegend=False,
            template='plotly_white'
        )
        
        # Save
        html_file = OUTPUT_DIR / 'dashboard_vaccination_impact.html'
        fig.write_html(str(html_file))
        
        if VERBOSE:
            print(f"✓ Vaccination dashboard saved: {html_file}")
        
        return html_file
    
    def create_master_dashboard(self):
        """Create comprehensive master dashboard with all data"""
        print("Generating master dashboard...")
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Chinese Disease Analysis - Master Dashboard</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .header h1 {{
            margin: 0;
            font-size: 32px;
        }}
        .header p {{
            margin: 10px 0 0 0;
            font-size: 14px;
            opacity: 0.9;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            border-left: 4px solid #667eea;
        }}
        .stat-card h3 {{
            margin: 0 0 10px 0;
            color: #666;
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        .stat-card .value {{
            font-size: 28px;
            font-weight: bold;
            color: #333;
        }}
        .stat-card .unit {{
            font-size: 12px;
            color: #999;
            margin-top: 5px;
        }}
        .dashboard-section {{
            background: white;
            padding: 20px;
            margin-bottom: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .dashboard-section h2 {{
            color: #333;
            margin-top: 0;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }}
        .dashboard-links {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
        }}
        .dashboard-link {{
            background: #667eea;
            color: white;
            padding: 15px;
            border-radius: 6px;
            text-decoration: none;
            text-align: center;
            transition: all 0.3s;
            font-weight: bold;
        }}
        .dashboard-link:hover {{
            background: #764ba2;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }}
        .footer {{
            text-align: center;
            color: #999;
            font-size: 12px;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 Chinese Disease Data Analysis</h1>
        <p>Interactive Epidemiological Analysis Dashboard • 2018-2022</p>
        <p>Generated: {self.timestamp}</p>
    </div>
    
    <div class="stats-grid">
        <div class="stat-card">
            <h3>Total Cases</h3>
            <div class="value">{self.df['Reported_Cases'].sum():,}</div>
            <div class="unit">cases</div>
        </div>
        <div class="stat-card">
            <h3>Total Deaths</h3>
            <div class="value">{self.df['Deaths'].sum():,}</div>
            <div class="unit">deaths</div>
        </div>
        <div class="stat-card">
            <h3>Case Fatality Rate</h3>
            <div class="value">{(self.df['Deaths'].sum() / self.df['Reported_Cases'].sum() * 100):.2f}%</div>
            <div class="unit">CFR</div>
        </div>
        <div class="stat-card">
            <h3>Total Recovered</h3>
            <div class="value">{self.df['Recovered'].sum():,}</div>
            <div class="unit">recovered</div>
        </div>
        <div class="stat-card">
            <h3>Total Hospitalized</h3>
            <div class="value">{self.df['Hospitalized'].sum():,}</div>
            <div class="unit">hospitalized</div>
        </div>
        <div class="stat-card">
            <h3>Diseases Analyzed</h3>
            <div class="value">{self.df['Disease'].nunique()}</div>
            <div class="unit">unique diseases</div>
        </div>
        <div class="stat-card">
            <h3>Provinces Covered</h3>
            <div class="value">{self.df['Province'].nunique()}</div>
            <div class="unit">provinces</div>
        </div>
        <div class="stat-card">
            <h3>Vaccination Coverage</h3>
            <div class="value">{(self.df['Vaccinated'].sum() / len(self.df) * 100):.2f}%</div>
            <div class="unit">vaccinated</div>
        </div>
    </div>
    
    <div class="dashboard-section">
        <h2>📈 Available Interactive Dashboards</h2>
        <p>Click on any dashboard below to explore detailed interactive visualizations:</p>
        <div class="dashboard-links">
            <a href="dashboard_disease_analysis.html" class="dashboard-link">
                🦠 Disease Analysis
            </a>
            <a href="dashboard_geographic_analysis.html" class="dashboard-link">
                🗺️ Geographic Analysis
            </a>
            <a href="dashboard_demographic_analysis.html" class="dashboard-link">
                👥 Demographic Analysis
            </a>
            <a href="dashboard_temporal_analysis.html" class="dashboard-link">
                📅 Temporal Analysis
            </a>
            <a href="dashboard_vaccination_impact.html" class="dashboard-link">
                💉 Vaccination Impact
            </a>
            <a href="dashboard_warehouse_data.html" class="dashboard-link">
                🏗️ Warehouse Downloads
            </a>
        </div>
    </div>
    
    <div class="dashboard-section">
        <h2>📊 Dashboard Usage</h2>
        <ul>
            <li><strong>Disease Analysis:</strong> Compare diseases by CFR, cases, deaths, and recovery rates</li>
            <li><strong>Geographic Analysis:</strong> Explore provincial case burden, CFR, and urban-rural distribution</li>
            <li><strong>Demographic Analysis:</strong> Analyze cases and mortality by age group and gender</li>
            <li><strong>Temporal Analysis:</strong> View disease trends from 2018-2022 with monthly granularity</li>
            <li><strong>Vaccination Impact:</strong> Compare outcomes between vaccinated and unvaccinated populations</li>
        </ul>
    </div>
    
    <div class="dashboard-section">
        <h2>🔍 Features</h2>
        <ul>
            <li>✅ Interactive hover tooltips for detailed information</li>
            <li>✅ Click to show/hide specific data series</li>
            <li>✅ Zoom, pan, and download chart as PNG</li>
            <li>✅ Responsive design for desktop and tablet</li>
            <li>✅ Real-time calculations and aggregations</li>
            <li>✅ Color-coded visualizations for easy interpretation</li>
        </ul>
    </div>
    
    <div class="dashboard-section">
        <h2>🔧 Prediction & Model Insights</h2>
        <div class="dashboard-note">
            <p>To access outbreak prediction, trend forecasting, and model drill-down details, launch the interactive Dash application:</p>
            <p><code>python dash_app.py</code></p>
            <p>This app displays live LSTM forecasts, XGBoost risk scores, and a dedicated model training summary panel.</p>
        </div>
    </div>
    
    <div class="footer">
        <p>📊 Chinese Disease Analysis Dashboard</p>
        <p>© 2026 - Epidemiological Analysis Project</p>
        <p>Data Period: 2018-2022 | Total Records: {len(self.df):,}</p>
        <p>Last Updated: {self.timestamp}</p>
    </div>
</body>
</html>
"""

        html_file = OUTPUT_DIR / 'dashboard_master.html'
        with open(html_file, 'w') as f:
            f.write(html_content)
        
        if VERBOSE:
            print(f"✓ Master dashboard saved: {html_file}")
        
        return html_file
    
    def create_warehouse_dashboard(self):
        """Create interactive warehouse data and download page"""
        print("Generating warehouse download dashboard...")
        warehouse_path = WAREHOUSE_DIR
        links = []
        if warehouse_path.exists():
            bronze = warehouse_path / 'bronze'
            silver = warehouse_path / 'silver'
            gold = warehouse_path / 'gold'
            if bronze.exists():
                for item in sorted(bronze.iterdir()):
                    if item.is_file():
                        links.append(('Bronze', item.name, f'warehouse/bronze/{item.name}'))
            if silver.exists():
                for item in sorted(silver.iterdir()):
                    if item.is_file():
                        links.append(('Silver', item.name, f'warehouse/silver/{item.name}'))
            if gold.exists():
                for item in sorted(gold.iterdir()):
                    if item.is_file():
                        links.append(('Gold', item.name, f'warehouse/gold/{item.name}'))
            sqlite_file = warehouse_path / 'epidemic_warehouse.sqlite'
            if sqlite_file.exists():
                links.append(('Gold', sqlite_file.name, f'warehouse/{sqlite_file.name}'))
        else:
            print('⚠ Warehouse directory not found; no download links created.')

        rows = ''
        for layer, name, path in links:
            rows += f'<tr><td>{layer}</td><td>{name}</td><td><a href="{path}" target="_blank">Download</a></td></tr>\n'

        if not rows:
            rows = '<tr><td colspan="3">No warehouse files found. Run the ETL pipeline first.</td></tr>'

        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Warehouse Data Downloads</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f8f9fb; color: #333; }}
        .container {{ max-width: 1200px; margin: auto; }}
        .header {{ margin-bottom: 20px; }}
        h1 {{ color: #2c3e50; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
        th, td {{ padding: 12px 15px; border: 1px solid #ddd; }}
        th {{ background: #34495e; color: white; text-align: left; }}
        tr:nth-child(even) {{ background: #fbfbfb; }}
        a.button {{ display: inline-block; margin-right: 10px; margin-top: 10px; padding: 12px 18px; background: #3498db; color: white; text-decoration: none; border-radius: 6px; }}
        a.button:hover {{ background: #2980b9; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Warehouse Data Download Portal</h1>
            <p>Access Bronze, Silver, and Gold layer files directly from the dashboard.</p>
            <p>Click a file name to download the raw, cleansed, or analytic warehouse export.</p>
            <p><a class="button" href="dashboard_master.html">Back to Master Dashboard</a></p>
        </div>

        <table>
            <thead>
                <tr>
                    <th>Layer</th>
                    <th>File</th>
                    <th>Download</th>
                </tr>
            </thead>
            <tbody>
                {rows}
            </tbody>
        </table>
    </div>
</body>
</html>
"""

        html_file = OUTPUT_DIR / 'dashboard_warehouse_data.html'
        with open(html_file, 'w') as f:
            f.write(html_content)

        if VERBOSE:
            print(f"✓ Warehouse dashboard saved: {html_file}")

        return html_file

    def generate_all_dashboards(self):
        """Generate all interactive dashboards"""
        print("\n" + "="*100)
        print("GENERATING ALL INTERACTIVE DASHBOARDS")
        print("="*100)
        
        self.create_disease_dashboard()
        self.create_geographic_dashboard()
        self.create_demographic_dashboard()
        self.create_temporal_dashboard()
        self.create_vaccination_dashboard()
        self.create_master_dashboard()
        self.create_warehouse_dashboard()
        
        if VERBOSE:
            print("\n✓ ALL DASHBOARDS GENERATED SUCCESSFULLY")
            print(f"\nOpen 'dashboard_master.html' in a web browser to access all dashboards")
        
        return True
