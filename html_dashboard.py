"""
HTML Interactive Dashboard Generator
Creates beautiful Plotly dashboards for disease analysis visualization
Standalone script - runs independently without dependencies on other modules
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')
from pathlib import Path

# Configuration
PROJECT_ROOT = Path(__file__).parent.parent
DATA_FILE = PROJECT_ROOT / "data" / "china_disease_data_Cleaned.csv"
OUTPUT_DIR = PROJECT_ROOT / "outputs"
DASHBOARDS_DIR = OUTPUT_DIR / "dashboards"

# Create output directory
DASHBOARDS_DIR.mkdir(parents=True, exist_ok=True)

# Color palettes
COLOR_PALETTE = {
    'primary': '#FF6B6B',
    'secondary': '#4ECDC4',
    'tertiary': '#45B7D1',
    'accent': '#FFA07A',
    'success': '#2ecc71',
    'warning': '#f39c12',
    'danger': '#e74c3c',
    'info': '#3498db'
}

TEMPLATE = 'plotly_white'


class HTMLDashboardGenerator:
    """Generate interactive HTML dashboards with Plotly"""
    
    def __init__(self, csv_file):
        """Initialize with data file"""
        self.csv_file = csv_file
        self.df = None
        self.load_data()
    
    def load_data(self):
        """Load and prepare data"""
        try:
            self.df = pd.read_csv(self.csv_file)
            print(f"✓ Data loaded: {len(self.df)} rows, {len(self.df.columns)} columns")
            
            # Convert Yes/No to binary if needed
            yes_no_cols = [col for col in self.df.columns if 'Hospitalized' in col or 'Recovered' in col 
                          or 'Vaccinated' in col or 'Quarantined' in col or 'Lab_Confirmed' in col]
            for col in yes_no_cols:
                if self.df[col].dtype == 'object':
                    self.df[col] = (self.df[col] == 'Yes').astype(int)
            
            print(f"✓ Data prepared with {self.df.shape[0]} records")
            return True
        except Exception as e:
            print(f"✗ Error loading data: {e}")
            return False
    
    def create_overview_dashboard(self):
        """Create main overview dashboard"""
        print("\n📊 Creating Overview Dashboard...")
        
        # Calculate key metrics
        total_cases = self.df['Reported_Cases'].sum()
        total_deaths = self.df['Deaths'].sum()
        total_recovered = self.df['Recovered'].sum()
        cfr = (total_deaths / total_cases * 100) if total_cases > 0 else 0
        
        # Create figure with subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Cases by Province', 'Deaths by Province', 
                          'Case Trend Over Time', 'Recovery Rate Comparison'),
            specs=[[{"type": "bar"}, {"type": "bar"}],
                   [{"type": "scatter"}, {"type": "pie"}]]
        )
        
        # Top 10 provinces by cases
        cases_by_province = self.df.groupby('Province')['Reported_Cases'].sum().nlargest(10)
        fig.add_trace(
            go.Bar(x=cases_by_province.index, y=cases_by_province.values,
                   marker_color=COLOR_PALETTE['primary'], name='Cases',
                   hovertemplate='<b>%{x}</b><br>Cases: %{y:,}<extra></extra>'),
            row=1, col=1
        )
        
        # Top 10 provinces by deaths
        deaths_by_province = self.df.groupby('Province')['Deaths'].sum().nlargest(10)
        fig.add_trace(
            go.Bar(x=deaths_by_province.index, y=deaths_by_province.values,
                   marker_color=COLOR_PALETTE['danger'], name='Deaths',
                   hovertemplate='<b>%{x}</b><br>Deaths: %{y:,}<extra></extra>'),
            row=1, col=2
        )
        
        # Time series
        time_series = self.df.groupby('Year')['Reported_Cases'].sum()
        fig.add_trace(
            go.Scatter(x=time_series.index, y=time_series.values, mode='lines+markers',
                      line=dict(color=COLOR_PALETTE['secondary'], width=3),
                      marker=dict(size=8), name='Cases Over Time',
                      hovertemplate='<b>Year %{x}</b><br>Cases: %{y:,}<extra></extra>'),
            row=2, col=1
        )
        
        # Recovery stats
        recovery_data = {
            'Recovered': [total_recovered],
            'Deaths': [total_deaths],
            'Active': [total_cases - total_recovered - total_deaths]
        }
        recovery_df = pd.DataFrame(recovery_data).T
        fig.add_trace(
            go.Pie(labels=recovery_df.index, values=recovery_df[0],
                   marker=dict(colors=[COLOR_PALETTE['success'], COLOR_PALETTE['danger'], COLOR_PALETTE['warning']]),
                   hovertemplate='<b>%{label}</b><br>Count: %{value:,}<br>%{percent}<extra></extra>'),
            row=2, col=2
        )
        
        # Update layout
        fig.update_layout(
            template=TEMPLATE,
            title_text="<b>Chinese Disease Analysis - Overview Dashboard</b>",
            title_font_size=24,
            showlegend=True,
            height=900,
            hovermode='closest',
            font=dict(size=11),
        )
        
        fig.update_xaxes(title_text="Province", row=1, col=1)
        fig.update_xaxes(title_text="Province", row=1, col=2)
        fig.update_xaxes(title_text="Year", row=2, col=1)
        fig.update_yaxes(title_text="Cases", row=1, col=1)
        fig.update_yaxes(title_text="Deaths", row=1, col=2)
        fig.update_yaxes(title_text="Cases", row=2, col=1)
        
        # Save
        output_file = DASHBOARDS_DIR / "01_overview_dashboard.html"
        fig.write_html(str(output_file))
        print(f"✓ Saved: {output_file.name}")
    
    def create_disease_dashboard(self):
        """Create disease-specific dashboard"""
        print("\n🦠 Creating Disease Analysis Dashboard...")
        
        # Get top diseases
        top_diseases = self.df.groupby('Disease')['Reported_Cases'].sum().nlargest(8)
        
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Top Diseases by Cases', 'CFR by Disease', 
                          'Cases vs Deaths Scatter', 'Disease Distribution'),
            specs=[[{"type": "bar"}, {"type": "bar"}],
                   [{"type": "scatter"}, {"type": "pie"}]]
        )
        
        # Top diseases
        fig.add_trace(
            go.Bar(x=top_diseases.index, y=top_diseases.values,
                   marker_color=COLOR_PALETTE['secondary'],
                   hovertemplate='<b>%{x}</b><br>Cases: %{y:,}<extra></extra>'),
            row=1, col=1
        )
        
        # CFR by disease
        cfr_by_disease = self.df.groupby('Disease').apply(
            lambda x: (x['Deaths'].sum() / x['Reported_Cases'].sum() * 100) if x['Reported_Cases'].sum() > 0 else 0
        ).nlargest(8)
        
        fig.add_trace(
            go.Bar(x=cfr_by_disease.index, y=cfr_by_disease.values,
                   marker_color=COLOR_PALETTE['danger'],
                   hovertemplate='<b>%{x}</b><br>CFR: %{y:.2f}%<extra></extra>'),
            row=1, col=2
        )
        
        # Scatter: Cases vs Deaths
        scatter_data = self.df.groupby('Disease').agg({'Reported_Cases': 'sum', 'Deaths': 'sum'}).reset_index()
        fig.add_trace(
            go.Scatter(x=scatter_data['Reported_Cases'], y=scatter_data['Deaths'], mode='markers+text',
                      text=scatter_data['Disease'], textposition='top center',
                      marker=dict(size=15, color=COLOR_PALETTE['tertiary'], opacity=0.7),
                      hovertemplate='<b>%{text}</b><br>Cases: %{x:,}<br>Deaths: %{y:,}<extra></extra>'),
            row=2, col=1
        )
        
        # Disease distribution pie
        fig.add_trace(
            go.Pie(labels=top_diseases.index, values=top_diseases.values,
                   hovertemplate='<b>%{label}</b><br>Cases: %{value:,}<br>%{percent}<extra></extra>'),
            row=2, col=2
        )
        
        fig.update_layout(
            template=TEMPLATE,
            title_text="<b>Disease Analysis Dashboard</b>",
            title_font_size=24,
            showlegend=False,
            height=900,
            font=dict(size=11)
        )
        
        fig.update_xaxes(title_text="Disease", row=1, col=1)
        fig.update_xaxes(title_text="Disease", row=1, col=2)
        fig.update_xaxes(title_text="Cases", row=2, col=1)
        fig.update_yaxes(title_text="Cases", row=1, col=1)
        fig.update_yaxes(title_text="CFR (%)", row=1, col=2)
        fig.update_yaxes(title_text="Deaths", row=2, col=1)
        
        output_file = DASHBOARDS_DIR / "02_disease_dashboard.html"
        fig.write_html(str(output_file))
        print(f"✓ Saved: {output_file.name}")
    
    def create_geographic_dashboard(self):
        """Create geographic analysis dashboard"""
        print("\n🗺️  Creating Geographic Dashboard...")
        
        # Geographic aggregation
        geo_data = self.df.groupby('Province').agg({
            'Reported_Cases': 'sum',
            'Deaths': 'sum',
            'Recovered': 'sum'
        }).reset_index().sort_values('Reported_Cases', ascending=False).head(15)
        
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Top Provinces by Cases', 'Mortality Rate by Province',
                          'Cases vs Recovered', 'Healthcare Load'),
            specs=[[{"type": "bar"}, {"type": "bar"}],
                   [{"type": "scatter"}, {"type": "box"}]]
        )
        
        # Top provinces
        fig.add_trace(
            go.Bar(x=geo_data['Province'], y=geo_data['Reported_Cases'],
                   marker_color=COLOR_PALETTE['primary'],
                   hovertemplate='<b>%{x}</b><br>Cases: %{y:,}<extra></extra>'),
            row=1, col=1
        )
        
        # Mortality rate
        geo_data['Mortality_Rate'] = (geo_data['Deaths'] / geo_data['Reported_Cases'] * 100)
        fig.add_trace(
            go.Bar(x=geo_data['Province'], y=geo_data['Mortality_Rate'],
                   marker_color=COLOR_PALETTE['danger'],
                   hovertemplate='<b>%{x}</b><br>Mortality: %{y:.2f}%<extra></extra>'),
            row=1, col=2
        )
        
        # Scatter: Cases vs Recovered
        fig.add_trace(
            go.Scatter(x=geo_data['Reported_Cases'], y=geo_data['Recovered'], mode='markers',
                      marker=dict(size=12, color=COLOR_PALETTE['secondary'], opacity=0.7),
                      text=geo_data['Province'],
                      hovertemplate='<b>%{text}</b><br>Cases: %{x:,}<br>Recovered: %{y:,}<extra></extra>'),
            row=2, col=1
        )
        
        # Hospitalization by province
        hosp_data = self.df.groupby('Province')['Hospitalized'].sum().nlargest(10)
        fig.add_trace(
            go.Box(y=hosp_data.values, name='Hospitalizations',
                   marker_color=COLOR_PALETTE['warning']),
            row=2, col=2
        )
        
        fig.update_layout(
            template=TEMPLATE,
            title_text="<b>Geographic Analysis Dashboard</b>",
            title_font_size=24,
            showlegend=False,
            height=900,
            font=dict(size=11)
        )
        
        fig.update_xaxes(title_text="Province", row=1, col=1)
        fig.update_xaxes(title_text="Province", row=1, col=2)
        fig.update_xaxes(title_text="Cases", row=2, col=1)
        fig.update_yaxes(title_text="Cases", row=1, col=1)
        fig.update_yaxes(title_text="Mortality Rate (%)", row=1, col=2)
        fig.update_yaxes(title_text="Recovered", row=2, col=1)
        
        output_file = DASHBOARDS_DIR / "03_geographic_dashboard.html"
        fig.write_html(str(output_file))
        print(f"✓ Saved: {output_file.name}")
    
    def create_temporal_dashboard(self):
        """Create temporal analysis dashboard"""
        print("\n📅 Creating Temporal Dashboard...")
        
        # Create time aggregation
        temporal = self.df.groupby(['Year', 'Month']).agg({
            'Reported_Cases': 'sum',
            'Deaths': 'sum',
            'Recovered': 'sum'
        }).reset_index()
        temporal['Date'] = temporal['Year'].astype(str) + '-' + temporal['Month'].astype(str).str.zfill(2)
        
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Monthly Cases Trend', 'Monthly Deaths Trend',
                          'Year-over-Year Comparison', 'Recovery Rate Trend'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"type": "bar"}, {"type": "scatter"}]]
        )
        
        # Cases over time
        fig.add_trace(
            go.Scatter(x=temporal['Date'], y=temporal['Reported_Cases'], mode='lines+markers',
                      line=dict(color=COLOR_PALETTE['primary'], width=2),
                      name='Cases',
                      hovertemplate='<b>%{x}</b><br>Cases: %{y:,}<extra></extra>'),
            row=1, col=1
        )
        
        # Deaths over time
        fig.add_trace(
            go.Scatter(x=temporal['Date'], y=temporal['Deaths'], mode='lines+markers',
                      line=dict(color=COLOR_PALETTE['danger'], width=2),
                      name='Deaths',
                      hovertemplate='<b>%{x}</b><br>Deaths: %{y:,}<extra></extra>'),
            row=1, col=2
        )
        
        # Year comparison
        yearly = self.df.groupby('Year')['Reported_Cases'].sum()
        fig.add_trace(
            go.Bar(x=yearly.index, y=yearly.values,
                   marker_color=COLOR_PALETTE['tertiary'],
                   hovertemplate='<b>%{x}</b><br>Cases: %{y:,}<extra></extra>'),
            row=2, col=1
        )
        
        # Recovery rate
        temporal['Recovery_Rate'] = (temporal['Recovered'] / temporal['Reported_Cases'] * 100)
        fig.add_trace(
            go.Scatter(x=temporal['Date'], y=temporal['Recovery_Rate'], mode='lines+markers',
                      line=dict(color=COLOR_PALETTE['success'], width=2),
                      marker=dict(size=6),
                      name='Recovery Rate',
                      hovertemplate='<b>%{x}</b><br>Recovery Rate: %{y:.1f}%<extra></extra>'),
            row=2, col=2
        )
        
        fig.update_layout(
            template=TEMPLATE,
            title_text="<b>Temporal Analysis Dashboard</b>",
            title_font_size=24,
            showlegend=True,
            height=900,
            font=dict(size=11)
        )
        
        fig.update_xaxes(title_text="Date", row=1, col=1)
        fig.update_xaxes(title_text="Date", row=1, col=2)
        fig.update_xaxes(title_text="Year", row=2, col=1)
        fig.update_xaxes(title_text="Date", row=2, col=2)
        fig.update_yaxes(title_text="Cases", row=1, col=1)
        fig.update_yaxes(title_text="Deaths", row=1, col=2)
        fig.update_yaxes(title_text="Cases", row=2, col=1)
        fig.update_yaxes(title_text="Recovery Rate (%)", row=2, col=2)
        
        output_file = DASHBOARDS_DIR / "04_temporal_dashboard.html"
        fig.write_html(str(output_file))
        print(f"✓ Saved: {output_file.name}")
    
    def create_vaccination_dashboard(self):
        """Create vaccination analysis dashboard"""
        print("\n💉 Creating Vaccination Dashboard...")
        
        # Vaccination stats
        vaccinated_cases = self.df[self.df['Vaccinated'] == 1]['Reported_Cases'].sum()
        unvaccinated_cases = self.df[self.df['Vaccinated'] == 0]['Reported_Cases'].sum()
        vaccinated_deaths = self.df[self.df['Vaccinated'] == 1]['Deaths'].sum()
        unvaccinated_deaths = self.df[self.df['Vaccinated'] == 0]['Deaths'].sum()
        
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Cases: Vaccinated vs Unvaccinated', 'Deaths: Vaccinated vs Unvaccinated',
                          'Case Fatality Rate Comparison', 'Disease Distribution by Vaccination'),
            specs=[[{"type": "pie"}, {"type": "pie"}],
                   [{"type": "bar"}, {"type": "bar"}]]
        )
        
        # Cases pie
        cases_data = [vaccinated_cases, unvaccinated_cases]
        fig.add_trace(
            go.Pie(labels=['Vaccinated', 'Unvaccinated'], values=cases_data,
                   marker=dict(colors=[COLOR_PALETTE['success'], COLOR_PALETTE['danger']]),
                   hovertemplate='<b>%{label}</b><br>Cases: %{value:,}<br>%{percent}<extra></extra>'),
            row=1, col=1
        )
        
        # Deaths pie
        deaths_data = [vaccinated_deaths, unvaccinated_deaths]
        fig.add_trace(
            go.Pie(labels=['Vaccinated', 'Unvaccinated'], values=deaths_data,
                   marker=dict(colors=[COLOR_PALETTE['success'], COLOR_PALETTE['danger']]),
                   hovertemplate='<b>%{label}</b><br>Deaths: %{value:,}<br>%{percent}<extra></extra>'),
            row=1, col=2
        )
        
        # CFR Comparison
        vaccinated_cfr = (vaccinated_deaths / vaccinated_cases * 100) if vaccinated_cases > 0 else 0
        unvaccinated_cfr = (unvaccinated_deaths / unvaccinated_cases * 100) if unvaccinated_cases > 0 else 0
        
        fig.add_trace(
            go.Bar(x=['Vaccinated', 'Unvaccinated'], y=[vaccinated_cfr, unvaccinated_cfr],
                   marker_color=[COLOR_PALETTE['success'], COLOR_PALETTE['danger']],
                   hovertemplate='<b>%{x}</b><br>CFR: %{y:.2f}%<extra></extra>'),
            row=2, col=1
        )
        
        # Disease breakdown by vaccination
        disease_vax = self.df.groupby('Disease')['Vaccinated'].sum().nlargest(8)
        fig.add_trace(
            go.Bar(x=disease_vax.index, y=disease_vax.values,
                   marker_color=COLOR_PALETTE['info'],
                   hovertemplate='<b>%{x}</b><br>Vaccinated: %{y:,}<extra></extra>'),
            row=2, col=2
        )
        
        fig.update_layout(
            template=TEMPLATE,
            title_text="<b>Vaccination Impact Dashboard</b>",
            title_font_size=24,
            showlegend=False,
            height=900,
            font=dict(size=11)
        )
        
        fig.update_yaxes(title_text="CFR (%)", row=2, col=1)
        fig.update_yaxes(title_text="Vaccinated Count", row=2, col=2)
        fig.update_xaxes(title_text="Disease", row=2, col=2)
        
        output_file = DASHBOARDS_DIR / "05_vaccination_dashboard.html"
        fig.write_html(str(output_file))
        print(f"✓ Saved: {output_file.name}")
    
    def create_master_dashboard(self):
        """Create master index dashboard"""
        print("\n🏠 Creating Master Dashboard...")
        
        # Calculate key metrics
        metrics = {
            'Total Cases': self.df['Reported_Cases'].sum(),
            'Total Deaths': self.df['Deaths'].sum(),
            'Total Recovered': self.df['Recovered'].sum(),
            'Hospitalized': self.df['Hospitalized'].sum(),
            'Vaccinated': self.df['Vaccinated'].sum(),
            'CFR (%)': (self.df['Deaths'].sum() / self.df['Reported_Cases'].sum() * 100)
        }
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chinese Disease Analysis - Master Dashboard</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        
        .header {{
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            margin-bottom: 30px;
            text-align: center;
        }}
        
        .header h1 {{
            color: #333;
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        .header p {{
            color: #666;
            font-size: 1.1em;
        }}
        
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        
        .metric-card {{
            background: white;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            transition: transform 0.3s, box-shadow 0.3s;
        }}
        
        .metric-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 15px 30px rgba(0,0,0,0.15);
        }}
        
        .metric-label {{
            color: #999;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 10px;
        }}
        
        .metric-value {{
            font-size: 2em;
            font-weight: bold;
            color: #333;
        }}
        
        .dashboard-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
        }}
        
        .dashboard-card {{
            background: white;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            cursor: pointer;
            transition: all 0.3s;
        }}
        
        .dashboard-card:hover {{
            transform: translateY(-8px);
            box-shadow: 0 20px 40px rgba(0,0,0,0.15);
        }}
        
        .dashboard-card h2 {{
            color: #333;
            margin-bottom: 10px;
            font-size: 1.3em;
        }}
        
        .dashboard-card p {{
            color: #666;
            margin-bottom: 15px;
            font-size: 0.95em;
            line-height: 1.5;
        }}
        
        .dashboard-link {{
            display: inline-block;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 10px 20px;
            border-radius: 8px;
            text-decoration: none;
            font-weight: bold;
            transition: all 0.3s;
        }}
        
        .dashboard-link:hover {{
            transform: scale(1.05);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.4);
        }}
        
        .footer {{
            text-align: center;
            color: white;
            margin-top: 40px;
            padding: 20px;
        }}
        
        .emoji {{
            font-size: 1.2em;
            margin-right: 8px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Chinese Disease Analysis Hub</h1>
            <p>Interactive Dashboards for Epidemiological Data Visualization</p>
        </div>
        
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-label">📈 Total Cases</div>
                <div class="metric-value">{metrics['Total Cases']:,}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">💀 Total Deaths</div>
                <div class="metric-value">{metrics['Total Deaths']:,}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">✅ Recovered</div>
                <div class="metric-value">{metrics['Total Recovered']:,}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">🏥 Hospitalized</div>
                <div class="metric-value">{metrics['Hospitalized']:,}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">💉 Vaccinated</div>
                <div class="metric-value">{metrics['Vaccinated']:,}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">📊 CFR</div>
                <div class="metric-value">{metrics['CFR (%)']:.2f}%</div>
            </div>
        </div>
        
        <div class="dashboard-grid">
            <div class="dashboard-card">
                <h2><span class="emoji">📊</span>Overview Dashboard</h2>
                <p>High-level summary of cases, deaths, and recovery across all provinces and time periods.</p>
                <a href="01_overview_dashboard.html" class="dashboard-link">→ View Dashboard</a>
            </div>
            
            <div class="dashboard-card">
                <h2><span class="emoji">🦠</span>Disease Analysis</h2>
                <p>Detailed breakdown of different diseases including CFR, cases, and death statistics.</p>
                <a href="02_disease_dashboard.html" class="dashboard-link">→ View Dashboard</a>
            </div>
            
            <div class="dashboard-card">
                <h2><span class="emoji">🗺️</span>Geographic Analysis</h2>
                <p>Provincial distribution of cases, mortality rates, and healthcare load across regions.</p>
                <a href="03_geographic_dashboard.html" class="dashboard-link">→ View Dashboard</a>
            </div>
            
            <div class="dashboard-card">
                <h2><span class="emoji">📅</span>Temporal Analysis</h2>
                <p>Time series trends showing case progression, seasonal patterns, and year-over-year comparison.</p>
                <a href="04_temporal_dashboard.html" class="dashboard-link">→ View Dashboard</a>
            </div>
            
            <div class="dashboard-card">
                <h2><span class="emoji">💉</span>Vaccination Impact</h2>
                <p>Comparison of vaccination status with disease severity and outcomes.</p>
                <a href="05_vaccination_dashboard.html" class="dashboard-link">→ View Dashboard</a>
            </div>
        </div>
        
        <div class="dashboard-section" style="background: #eef2ff; border-radius: 12px; padding: 24px; margin-top: 24px; box-shadow: 0 4px 12px rgba(0,0,0,0.08);">
            <h2 style="margin-top: 0; color: #333;">🔧 Prediction & Model Insights</h2>
            <p style="color: #333;">For outbreak prediction and trend forecasting, open the dedicated Dash app with the latest trained models.</p>
            <p style="font-weight: bold;">Run: <code>python dash_app.py</code></p>
            <p style="color: #555;">This app displays live LSTM forecasts, XGBoost risk scores, and a dedicated model status summary panel.</p>
        </div>
        
        <div class="footer">
            <p>Generated on 2026-04-25 | All visualizations are interactive - hover over charts for details</p>
        </div>
    </div>
</body>
</html>
"""
        
        output_file = DASHBOARDS_DIR / "00_master_dashboard.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"✓ Saved: {output_file.name}")
    
    def generate_all_dashboards(self):
        """Generate all dashboards"""
        print("\n" + "="*80)
        print("🎨 GENERATING ALL HTML DASHBOARDS")
        print("="*80)
        
        try:
            self.create_overview_dashboard()
            self.create_disease_dashboard()
            self.create_geographic_dashboard()
            self.create_temporal_dashboard()
            self.create_vaccination_dashboard()
            self.create_master_dashboard()
            
            print("\n" + "="*80)
            print("✅ ALL DASHBOARDS GENERATED SUCCESSFULLY!")
            print("="*80)
            print(f"\n📁 Dashboards saved to: {DASHBOARDS_DIR}")
            print(f"\n🌐 Open this file in your browser to get started:")
            print(f"   {DASHBOARDS_DIR}/00_master_dashboard.html")
            print("\n📊 Available Dashboards:")
            print("   1. Master Dashboard - Overview & Navigation")
            print("   2. Overview Dashboard - Key Metrics & Trends")
            print("   3. Disease Analysis - Disease Comparison")
            print("   4. Geographic Analysis - Provincial Distribution")
            print("   5. Temporal Analysis - Time Series & Trends")
            print("   6. Vaccination Impact - Vaccine Effectiveness")
            print("\n💡 Tips:")
            print("   • Hover over charts for detailed information")
            print("   • Click legend items to show/hide data series")
            print("   • Use toolbar buttons to zoom, pan, and save as PNG")
            print("   • All dashboards are fully interactive")
            print()
            
            return True
        except Exception as e:
            print(f"\n✗ Error generating dashboards: {e}")
            import traceback
            traceback.print_exc()
            return False


def main():
    """Main execution"""
    # Check if data file exists
    if not DATA_FILE.exists():
        print(f"✗ Error: Data file not found at {DATA_FILE}")
        print(f"\nLooking for cleaned data in workspace...")
        
        # Try to find cleaned data
        parent = DATA_FILE.parent
        if not parent.exists():
            parent.mkdir(parents=True, exist_ok=True)
        
        # List available files
        project_parent = PROJECT_ROOT.parent
        print(f"\nAvailable CSV files in {project_parent}:")
        for f in project_parent.glob("*.csv"):
            print(f"  - {f.name}")
        
        return False
    
    # Generate dashboards
    generator = HTMLDashboardGenerator(str(DATA_FILE))
    if generator.df is not None:
        return generator.generate_all_dashboards()
    return False


if __name__ == "__main__":
    success = main()
    if not success:
        print("\n⚠️  Dashboard generation completed with errors.")
        exit(1)
