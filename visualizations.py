"""
Visualization Module
Creates publication-quality charts and visualizations
"""

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from config import (
    FIGURE_SIZE_DEFAULT, FIGURE_SIZE_LARGE, FIGURE_SIZE_SQUARE,
    COLORS_SEASON, COLORS_VACCINATION, COLORS_GENDER, COLOR_PALETTE_MAIN,
    SEASON_ORDER, AGE_GROUP_ORDER, CHARTS_DIR, VERBOSE
)


class DiseaseVisualizer:
    """Creates visualizations for disease data"""
    
    def __init__(self, df):
        self.df = df
        sns.set_palette(COLOR_PALETTE_MAIN)
        plt.rcParams['figure.figsize'] = FIGURE_SIZE_DEFAULT
        plt.rcParams['font.size'] = 10
        self.chart_count = 0
    
    def plot_monthly_trends(self, figsize=FIGURE_SIZE_LARGE):
        """Visualization 1: Monthly case trends for top diseases"""
        self.chart_count += 1
        fig, ax = plt.subplots(figsize=figsize)
        
        for disease in self.df['Disease'].unique()[:5]:
            disease_data = self.df[self.df['Disease'] == disease].groupby('Month_Year')['Reported_Cases'].sum()
            ax.plot(disease_data.index, disease_data.values, marker='o', label=disease, linewidth=2)
        
        ax.set_xlabel('Month-Year', fontsize=12, fontweight='bold')
        ax.set_ylabel('Reported Cases', fontsize=12, fontweight='bold')
        ax.set_title('Monthly Case Trends for Top 5 Diseases (2018-2022)', fontsize=14, fontweight='bold')
        ax.legend(loc='best', fontsize=10)
        ax.grid(True, alpha=0.3)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        self._save_figure('01_monthly_trends')
        plt.show()
        return fig
    
    def plot_seasonal_distribution(self, figsize=(10, 8)):
        """Visualization 2: Seasonal distribution pie chart"""
        self.chart_count += 1
        fig, ax = plt.subplots(figsize=figsize)
        
        season_data = self.df.groupby('Season')['Reported_Cases'].sum()
        season_data_ordered = season_data.reindex(SEASON_ORDER)
        
        ax.pie(season_data_ordered.values, labels=season_data_ordered.index, autopct='%1.1f%%',
               colors=COLORS_SEASON, startangle=90, textprops={'fontsize': 12, 'weight': 'bold'})
        ax.set_title('Disease Cases Distribution by Season', fontsize=14, fontweight='bold', pad=20)
        
        plt.tight_layout()
        self._save_figure('02_seasonal_distribution')
        plt.show()
        return fig
    
    def plot_urban_rural_comparison(self, figsize=FIGURE_SIZE_DEFAULT):
        """Visualization: Urban vs Rural comparison"""
        self.chart_count += 1
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
        
        # Cases
        urban_rural_cases = self.df.groupby('Urban_Rural')['Reported_Cases'].sum()
        urban_rural_cases.plot(kind='pie', ax=ax1, autopct='%1.1f%%',
                              colors=['#3498db', '#2ecc71'], startangle=90)
        ax1.set_ylabel('')
        ax1.set_title('Urban vs Rural Cases', fontsize=12, fontweight='bold')
        
        # Deaths
        urban_rural_deaths = self.df.groupby('Urban_Rural')['Deaths'].sum()
        urban_rural_deaths.plot(kind='pie', ax=ax2, autopct='%1.1f%%',
                               colors=['#e74c3c', '#f39c12'], startangle=90)
        ax2.set_ylabel('')
        ax2.set_title('Urban vs Rural Deaths', fontsize=12, fontweight='bold')
        
        plt.tight_layout()
        self._save_figure('03_urban_rural')
        plt.show()
        return fig
    
    def plot_top_provinces(self, top_n=10, figsize=(12, 6)):
        """Visualization: Top provinces by cases"""
        self.chart_count += 1
        fig, ax = plt.subplots(figsize=figsize)
        
        top_provinces = self.df.groupby('Province')['Reported_Cases'].sum().nlargest(top_n)
        top_provinces.plot(kind='barh', ax=ax, color='#3498db')
        
        ax.set_xlabel('Total Reported Cases', fontsize=12, fontweight='bold')
        ax.set_ylabel('Province', fontsize=12, fontweight='bold')
        ax.set_title(f'Top {top_n} Provinces by Reported Cases', fontsize=14, fontweight='bold')
        ax.invert_yaxis()
        
        for i, v in enumerate(top_provinces.values):
            ax.text(v + 5, i, str(int(v)), va='center', fontweight='bold')
        
        plt.tight_layout()
        self._save_figure(f'04_top_{top_n}_provinces')
        plt.show()
        return fig
    
    def plot_age_gender_distribution(self, figsize=FIGURE_SIZE_DEFAULT):
        """Visualization: Cases by age group and gender"""
        self.chart_count += 1
        fig, ax = plt.subplots(figsize=figsize)
        
        age_gender = pd.pivot_table(self.df, values='Reported_Cases',
                                   index='Age_Group', columns='Gender', aggfunc='sum', fill_value=0)
        age_gender = age_gender.reindex(AGE_GROUP_ORDER)
        age_gender.plot(kind='bar', ax=ax, color=COLORS_GENDER, width=0.8)
        
        ax.set_xlabel('Age Group', fontsize=12, fontweight='bold')
        ax.set_ylabel('Reported Cases', fontsize=12, fontweight='bold')
        ax.set_title('Cases Distribution by Age Group and Gender', fontsize=14, fontweight='bold')
        ax.legend(title='Gender', fontsize=10)
        plt.xticks(rotation=45, ha='right')
        
        plt.tight_layout()
        self._save_figure('05_age_gender_distribution')
        plt.show()
        return fig
    
    def plot_mortality_by_age(self, figsize=FIGURE_SIZE_DEFAULT):
        """Visualization: Mortality by age group"""
        self.chart_count += 1
        fig, ax = plt.subplots(figsize=figsize)
        
        mortality_age = self.df.groupby('Age_Group')['Deaths'].sum().reindex(AGE_GROUP_ORDER)
        colors = ['#95E1D3', '#C7FFED', '#EAFFAF', '#FCFF49', '#FF6B6B']
        bars = ax.bar(range(len(mortality_age)), mortality_age.values, color=colors, edgecolor='black', linewidth=1.5)
        
        ax.set_xticks(range(len(mortality_age)))
        ax.set_xticklabels(list(mortality_age.index))
        ax.set_xlabel('Age Group', fontsize=12, fontweight='bold')
        ax.set_ylabel('Total Deaths', fontsize=12, fontweight='bold')
        ax.set_title('Mortality Distribution by Age Group', fontsize=14, fontweight='bold')
        
        for bar, val in zip(bars, mortality_age.values):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height(), f'{int(val)}',
                   ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        self._save_figure('06_mortality_by_age')
        plt.show()
        return fig
    
    def plot_vaccination_impact(self, figsize=(14, 6)):
        """Visualization: Vaccination impact on cases and deaths"""
        self.chart_count += 1
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
        
        # Cases
        vacc_cases = self.df.groupby('Vaccinated')['Reported_Cases'].sum()
        vacc_labels = {0: 'Non-vaccinated', 1: 'Vaccinated'} if len(vacc_cases) == 2 else {0: 'No', 1: 'Yes'}
        vacc_labels_list = [vacc_labels.get(i, f'Group {i}') for i in range(len(vacc_cases))]
        ax1.bar(range(len(vacc_cases)), vacc_cases.values, color=COLORS_VACCINATION[:len(vacc_cases)], edgecolor='black', linewidth=1.5)
        ax1.set_xticks(range(len(vacc_cases)))
        ax1.set_xticklabels(vacc_labels_list)
        ax1.set_ylabel('Total Cases', fontsize=11, fontweight='bold')
        ax1.set_title('Total Cases: Vaccinated vs Non-vaccinated', fontsize=12, fontweight='bold')
        
        for i, v in enumerate(vacc_cases.values):
            ax1.text(i, v, f'{int(v)}', ha='center', va='bottom', fontweight='bold')
        
        # Deaths
        vacc_deaths = self.df.groupby('Vaccinated')['Deaths'].sum()
        ax2.bar(range(len(vacc_deaths)), vacc_deaths.values, color=COLORS_VACCINATION[:len(vacc_deaths)], edgecolor='black', linewidth=1.5)
        ax2.set_xticks(range(len(vacc_deaths)))
        ax2.set_xticklabels(vacc_labels_list)
        ax2.set_ylabel('Total Deaths', fontsize=11, fontweight='bold')
        ax2.set_title('Total Deaths: Vaccinated vs Non-vaccinated', fontsize=12, fontweight='bold')
        
        for i, v in enumerate(vacc_deaths.values):
            ax2.text(i, v, f'{int(v)}', ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        self._save_figure('07_vaccination_impact_cases_deaths')
        plt.show()
        return fig
    
    def plot_cfr_comparison(self, figsize=FIGURE_SIZE_DEFAULT):
        """Visualization: CFR by disease"""
        self.chart_count += 1
        fig, ax = plt.subplots(figsize=figsize)
        
        cfr_data = self.df.groupby('Disease').agg({
            'Deaths': 'sum',
            'Reported_Cases': 'sum'
        }).reset_index()
        cfr_data['CFR_%'] = (cfr_data['Deaths'] / cfr_data['Reported_Cases'] * 100).round(2)
        cfr_data = cfr_data.sort_values('CFR_%', ascending=True)
        
        bars = ax.barh(cfr_data['Disease'], cfr_data['CFR_%'], color='#e74c3c', edgecolor='black', linewidth=1.5)
        ax.set_xlabel('Case Fatality Rate (%)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Disease', fontsize=12, fontweight='bold')
        ax.set_title('Case Fatality Rate by Disease Type', fontsize=14, fontweight='bold')
        
        for bar, val in zip(bars, cfr_data['CFR_%']):
            ax.text(val, bar.get_y() + bar.get_height()/2, f'{val:.2f}%',
                   ha='left', va='center', fontweight='bold')
        
        plt.tight_layout()
        self._save_figure('08_cfr_by_disease')
        plt.show()
        return fig
    
    def plot_heatmap_disease_month(self):
        """Visualization: Disease-month heatmap"""
        self.chart_count += 1
        fig, ax = plt.subplots(figsize=FIGURE_SIZE_LARGE)
        
        top_diseases = self.df.groupby('Disease')['Reported_Cases'].sum().nlargest(5).index
        df_top = self.df[self.df['Disease'].isin(top_diseases)]
        heatmap_data = pd.pivot_table(df_top, values='Reported_Cases',
                                     index='Disease', columns='Month', aggfunc='sum', fill_value=0)
        
        sns.heatmap(heatmap_data, annot=True, fmt='.0f', cmap='YlOrRd', ax=ax, cbar_kws={'label': 'Cases'})
        ax.set_xlabel('Month', fontsize=12, fontweight='bold')
        ax.set_ylabel('Disease', fontsize=12, fontweight='bold')
        ax.set_title('Monthly Case Distribution for Top 5 Diseases (Heatmap)', fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        self._save_figure('09_disease_month_heatmap')
        plt.show()
        return fig
    
    def plot_year_over_year_comparison(self, figsize=FIGURE_SIZE_DEFAULT):
        """Visualization: Year-over-year case trends"""
        self.chart_count += 1
        fig, ax = plt.subplots(figsize=figsize)
        
        yearly_data = self.df.groupby('Year')['Reported_Cases'].sum()
        colors_gradient = plt.cm.Blues(np.linspace(0.4, 0.8, len(yearly_data)))
        bars = ax.bar(yearly_data.index, yearly_data.values, color=colors_gradient, edgecolor='black', linewidth=1.5)
        
        ax.set_xlabel('Year', fontsize=12, fontweight='bold')
        ax.set_ylabel('Total Cases', fontsize=12, fontweight='bold')
        ax.set_title('Year-over-Year Case Trends (2018-2022)', fontsize=14, fontweight='bold')
        ax.grid(axis='y', alpha=0.3)
        
        for bar, val in zip(bars, yearly_data.values):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height(), f'{int(val)}',
                   ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        self._save_figure('10_year_over_year')
        plt.close()
        return fig
    
    def plot_gender_specific_mortality(self, figsize=FIGURE_SIZE_DEFAULT):
        """Visualization: Gender-specific CFR comparison"""
        self.chart_count += 1
        fig, ax = plt.subplots(figsize=figsize)
        
        gender_stats = self.df.groupby('Gender').agg({
            'Reported_Cases': 'sum',
            'Deaths': 'sum'
        }).reset_index()
        gender_stats['CFR_%'] = (gender_stats['Deaths'] / gender_stats['Reported_Cases'] * 100)
        
        bars = ax.bar(range(len(gender_stats)), gender_stats['CFR_%'], color=COLORS_GENDER, edgecolor='black', linewidth=1.5)
        ax.set_xticks(range(len(gender_stats)))
        ax.set_xticklabels(gender_stats['Gender'])
        ax.set_ylabel('Case Fatality Rate (%)', fontsize=12, fontweight='bold')
        ax.set_title('Case Fatality Rate by Gender', fontsize=14, fontweight='bold')
        ax.grid(axis='y', alpha=0.3)
        
        for bar, val in zip(bars, gender_stats['CFR_%']):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height(), f'{val:.2f}%',
                   ha='center', va='bottom', fontweight='bold', fontsize=11)
        
        plt.tight_layout()
        self._save_figure('11_gender_mortality')
        plt.close()
        return fig
    
    def plot_province_comparison(self, figsize=FIGURE_SIZE_DEFAULT):
        """Visualization: Top vs Bottom provinces comparison"""
        self.chart_count += 1
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
        
        province_cases = self.df.groupby('Province')['Reported_Cases'].sum().sort_values(ascending=False)
        top_5 = province_cases.head(5)
        bottom_5 = province_cases.tail(5)
        
        # Top provinces
        top_5.plot(kind='barh', ax=ax1, color='#e74c3c', edgecolor='black', linewidth=1)
        ax1.set_xlabel('Cases', fontsize=11, fontweight='bold')
        ax1.set_title('Top 5 Provinces', fontsize=12, fontweight='bold')
        ax1.invert_yaxis()
        for i, v in enumerate(top_5.values):
            ax1.text(v + 50, i, str(int(v)), va='center', fontweight='bold', fontsize=9)
        
        # Bottom provinces
        bottom_5.plot(kind='barh', ax=ax2, color='#2ecc71', edgecolor='black', linewidth=1)
        ax2.set_xlabel('Cases', fontsize=11, fontweight='bold')
        ax2.set_title('Bottom 5 Provinces', fontsize=12, fontweight='bold')
        ax2.invert_yaxis()
        for i, v in enumerate(bottom_5.values):
            ax2.text(v + 50, i, str(int(v)), va='center', fontweight='bold', fontsize=9)
        
        plt.suptitle('Province Case Distribution Comparison', fontsize=14, fontweight='bold', y=1.00)
        plt.tight_layout()
        self._save_figure('12_province_comparison')
        plt.close()
        return fig
    
    def plot_cfr_case_scatter(self, figsize=FIGURE_SIZE_LARGE):
        """Visualization: CFR vs Case Volume scatter plot"""
        self.chart_count += 1
        fig, ax = plt.subplots(figsize=figsize)
        
        disease_analysis = self.df.groupby('Disease').agg({
            'Reported_Cases': 'sum',
            'Deaths': 'sum'
        }).reset_index()
        disease_analysis['CFR_%'] = (disease_analysis['Deaths'] / disease_analysis['Reported_Cases'] * 100)
        
        scatter = ax.scatter(disease_analysis['Reported_Cases'], disease_analysis['CFR_%'], 
                           s=300, alpha=0.6, c=range(len(disease_analysis)), cmap='viridis', edgecolor='black', linewidth=1.5)
        
        for idx, row in disease_analysis.iterrows():
            ax.annotate(row['Disease'], (row['Reported_Cases'], row['CFR_%']), 
                       fontsize=8, ha='center', va='center', fontweight='bold')
        
        ax.set_xlabel('Total Cases', fontsize=12, fontweight='bold')
        ax.set_ylabel('Case Fatality Rate (%)', fontsize=12, fontweight='bold')
        ax.set_title('Disease Severity vs Case Volume (Bubble Plot)', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        self._save_figure('13_cfr_case_scatter')
        plt.close()
        return fig
    
    def plot_seasonal_trend_by_disease(self, figsize=FIGURE_SIZE_LARGE):
        """Visualization: Seasonal trends for top diseases"""
        self.chart_count += 1
        fig, ax = plt.subplots(figsize=figsize)
        
        top_diseases = self.df.groupby('Disease')['Reported_Cases'].sum().nlargest(5).index
        for disease in top_diseases:
            seasonal_data = self.df[self.df['Disease'] == disease].groupby('Season')['Reported_Cases'].sum()
            seasonal_data = seasonal_data.reindex(SEASON_ORDER)
            ax.plot(SEASON_ORDER, seasonal_data.values, marker='o', label=disease, linewidth=2.5, markersize=8)
        
        ax.set_xlabel('Season', fontsize=12, fontweight='bold')
        ax.set_ylabel('Cases', fontsize=12, fontweight='bold')
        ax.set_title('Seasonal Disease Patterns - Top 5 Diseases', fontsize=14, fontweight='bold')
        ax.legend(loc='best', fontsize=10)
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        self._save_figure('14_seasonal_by_disease')
        plt.close()
        return fig
    
    def plot_key_metrics_infographic(self, figsize=(14, 10)):
        """Visualization: Key metrics infographic/dashboard"""
        self.chart_count += 1
        fig = plt.figure(figsize=figsize)
        gs = fig.add_gridspec(3, 3, hspace=0.4, wspace=0.3)
        
        # Calculate metrics
        total_cases = self.df['Reported_Cases'].sum()
        total_deaths = self.df['Deaths'].sum()
        cfr = (total_deaths / total_cases * 100)
        top_disease = self.df.groupby('Disease')['Reported_Cases'].sum().idxmax()
        top_province = self.df.groupby('Province')['Reported_Cases'].sum().idxmax()
        
        # Title
        fig.suptitle('Key Disease Surveillance Metrics Dashboard', fontsize=16, fontweight='bold', y=0.98)
        
        # Metric 1: Total Cases (large)
        ax1 = fig.add_subplot(gs[0, 0])
        ax1.text(0.5, 0.7, f'{int(total_cases):,}', ha='center', va='center', fontsize=32, fontweight='bold', color='#3498db')
        ax1.text(0.5, 0.3, 'Total Cases', ha='center', va='center', fontsize=12, fontweight='bold')
        ax1.set_xlim(0, 1)
        ax1.set_ylim(0, 1)
        ax1.axis('off')
        ax1.add_patch(plt.Rectangle((0.05, 0.05), 0.9, 0.9, fill=False, edgecolor='#3498db', linewidth=2))
        
        # Metric 2: Total Deaths
        ax2 = fig.add_subplot(gs[0, 1])
        ax2.text(0.5, 0.7, f'{int(total_deaths):,}', ha='center', va='center', fontsize=32, fontweight='bold', color='#e74c3c')
        ax2.text(0.5, 0.3, 'Total Deaths', ha='center', va='center', fontsize=12, fontweight='bold')
        ax2.set_xlim(0, 1)
        ax2.set_ylim(0, 1)
        ax2.axis('off')
        ax2.add_patch(plt.Rectangle((0.05, 0.05), 0.9, 0.9, fill=False, edgecolor='#e74c3c', linewidth=2))
        
        # Metric 3: CFR
        ax3 = fig.add_subplot(gs[0, 2])
        ax3.text(0.5, 0.7, f'{cfr:.2f}%', ha='center', va='center', fontsize=32, fontweight='bold', color='#f39c12')
        ax3.text(0.5, 0.3, 'CFR', ha='center', va='center', fontsize=12, fontweight='bold')
        ax3.set_xlim(0, 1)
        ax3.set_ylim(0, 1)
        ax3.axis('off')
        ax3.add_patch(plt.Rectangle((0.05, 0.05), 0.9, 0.9, fill=False, edgecolor='#f39c12', linewidth=2))
        
        # Top disease
        ax4 = fig.add_subplot(gs[1, 0])
        ax4.text(0.5, 0.6, top_disease, ha='center', va='center', fontsize=14, fontweight='bold', wrap=True)
        ax4.text(0.5, 0.2, 'Most Common Disease', ha='center', va='center', fontsize=10, fontweight='bold')
        ax4.set_xlim(0, 1)
        ax4.set_ylim(0, 1)
        ax4.axis('off')
        ax4.add_patch(plt.Rectangle((0.05, 0.05), 0.9, 0.9, fill=False, edgecolor='#2ecc71', linewidth=2))
        
        # Top province
        ax5 = fig.add_subplot(gs[1, 1])
        ax5.text(0.5, 0.6, top_province, ha='center', va='center', fontsize=14, fontweight='bold')
        ax5.text(0.5, 0.2, 'Most Affected Province', ha='center', va='center', fontsize=10, fontweight='bold')
        ax5.set_xlim(0, 1)
        ax5.set_ylim(0, 1)
        ax5.axis('off')
        ax5.add_patch(plt.Rectangle((0.05, 0.05), 0.9, 0.9, fill=False, edgecolor='#9b59b6', linewidth=2))
        
        # Diseases count
        ax6 = fig.add_subplot(gs[1, 2])
        disease_count = self.df['Disease'].nunique()
        ax6.text(0.5, 0.7, f'{disease_count}', ha='center', va='center', fontsize=32, fontweight='bold', color='#1abc9c')
        ax6.text(0.5, 0.3, 'Diseases Tracked', ha='center', va='center', fontsize=12, fontweight='bold')
        ax6.set_xlim(0, 1)
        ax6.set_ylim(0, 1)
        ax6.axis('off')
        ax6.add_patch(plt.Rectangle((0.05, 0.05), 0.9, 0.9, fill=False, edgecolor='#1abc9c', linewidth=2))
        
        # Mini charts row
        ax7 = fig.add_subplot(gs[2, :])
        ax7.axis('off')
        ax7.text(0.02, 0.9, 'Analysis Period: 2018-2022', fontsize=11, fontweight='bold', transform=ax7.transAxes)
        ax7.text(0.02, 0.7, f'Provinces: {self.df["Province"].nunique()} | Gender: 2 | Age Groups: {self.df["Age_Group"].nunique()}', 
                fontsize=11, fontweight='bold', transform=ax7.transAxes)
        ax7.text(0.02, 0.5, f'Urban Cases: {self.df[self.df["Urban_Rural"]=="Urban"]["Reported_Cases"].sum():,} | Rural Cases: {self.df[self.df["Urban_Rural"]=="Rural"]["Reported_Cases"].sum():,}',
                fontsize=11, fontweight='bold', transform=ax7.transAxes)
        
        plt.tight_layout()
        self._save_figure('15_key_metrics_dashboard')
        plt.close()
        return fig
    
    def plot_disease_severity_ranking(self, figsize=FIGURE_SIZE_DEFAULT):
        """Visualization: Disease severity ranking with multiple metrics"""
        self.chart_count += 1
        fig, ax = plt.subplots(figsize=figsize)
        
        disease_metrics = self.df.groupby('Disease').agg({
            'Reported_Cases': 'sum',
            'Deaths': 'sum'
        }).reset_index()
        disease_metrics['CFR_%'] = (disease_metrics['Deaths'] / disease_metrics['Reported_Cases'] * 100)
        disease_metrics = disease_metrics.sort_values('CFR_%', ascending=True)
        
        colors_map = plt.cm.RdYlGn_r(np.linspace(0.2, 0.8, len(disease_metrics)))
        bars = ax.barh(disease_metrics['Disease'], disease_metrics['CFR_%'], color=colors_map, edgecolor='black', linewidth=1)
        
        ax.set_xlabel('Case Fatality Rate (%)', fontsize=12, fontweight='bold')
        ax.set_title('Disease Severity Ranking by CFR', fontsize=14, fontweight='bold')
        ax.grid(axis='x', alpha=0.3)
        
        for i, (bar, val) in enumerate(zip(bars, disease_metrics['CFR_%'])):
            cases = disease_metrics.iloc[i]['Reported_Cases']
            ax.text(val + 0.05, bar.get_y() + bar.get_height()/2, 
                   f'{val:.2f}% ({int(cases)} cases)', va='center', fontweight='bold', fontsize=9)
        
        plt.tight_layout()
        self._save_figure('16_disease_severity_ranking')
        plt.close()
        return fig
    
    def plot_outbreak_timeline(self, figsize=FIGURE_SIZE_LARGE):
        """Visualization: Outbreak timeline showing disease progression"""
        self.chart_count += 1
        fig, ax = plt.subplots(figsize=figsize)
        
        monthly_data = self.df.groupby('Month_Year')['Reported_Cases'].sum()
        monthly_data_deaths = self.df.groupby('Month_Year')['Deaths'].sum()
        
        ax2 = ax.twinx()
        line1 = ax.plot(range(len(monthly_data)), monthly_data.values, color='#3498db', marker='o', linewidth=2.5, label='Cases')
        line2 = ax2.plot(range(len(monthly_data_deaths)), monthly_data_deaths.values, color='#e74c3c', marker='s', linewidth=2.5, label='Deaths')
        
        ax.set_xlabel('Time Period', fontsize=12, fontweight='bold')
        ax.set_ylabel('Cases', fontsize=12, fontweight='bold', color='#3498db')
        ax2.set_ylabel('Deaths', fontsize=12, fontweight='bold', color='#e74c3c')
        ax.set_title('Disease Outbreak Timeline (2018-2022)', fontsize=14, fontweight='bold')
        ax.tick_params(axis='y', labelcolor='#3498db')
        ax2.tick_params(axis='y', labelcolor='#e74c3c')
        
        lines = line1 + line2
        labels = [l.get_label() for l in lines]
        ax.legend(lines, labels, loc='upper left', fontsize=10)
        ax.grid(True, alpha=0.3)
        
        plt.xticks(range(0, len(monthly_data), max(1, len(monthly_data)//5)), rotation=45, ha='right')
        plt.tight_layout()
        self._save_figure('17_outbreak_timeline')
        plt.close()
        return fig
    
    def _save_figure(self, filename):
        """Save figure to disk"""
        filepath = CHARTS_DIR / f"{filename}.png"
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        if VERBOSE:
            print(f"  Saved: {filename}.png")
    
    def generate_all_visualizations(self):
        """Generate all visualizations"""
        print("\n" + "="*100)
        print("GENERATING VISUALIZATIONS")
        print("="*100 + "\n")
        
        self.plot_monthly_trends()
        self.plot_seasonal_distribution()
        self.plot_urban_rural_comparison()
        self.plot_top_provinces()
        self.plot_age_gender_distribution()
        self.plot_mortality_by_age()
        self.plot_vaccination_impact()
        self.plot_cfr_comparison()
        self.plot_heatmap_disease_month()
        
        # NEW ENHANCED VISUALIZATIONS
        print("  Generating enhanced visualizations...")
        self.plot_year_over_year_comparison()
        self.plot_gender_specific_mortality()
        self.plot_province_comparison()
        self.plot_cfr_case_scatter()
        self.plot_seasonal_trend_by_disease()
        self.plot_key_metrics_infographic()
        self.plot_disease_severity_ranking()
        self.plot_outbreak_timeline()
        
        if VERBOSE:
            print(f"\n✓ Generated {self.chart_count} visualizations total")
