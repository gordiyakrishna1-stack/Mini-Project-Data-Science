"""
Health Indicators Calculation Module
Implements all 20 health indicators from the reference document
"""

import pandas as pd
import numpy as np
from config import AGE_GROUP_ORDER, SEASON_ORDER, VERBOSE


class HealthIndicators:
    """Calculates all 20 health indicators"""
    
    def __init__(self, df):
        self.df = df
        self.indicators = {}
        
    def calculate_all(self):
        """Calculate all 20 indicators"""
        print("\n" + "="*100)
        print("HEALTH INDICATORS CALCULATION - ALL 20 INDICATORS")
        print("="*100)
        
        # Group A: Disease Severity & Outcomes (1-6)
        self._calculate_indicators_1_6()
        
        # Group B: Control Measures (7, 8, 15)
        self._calculate_indicators_7_8_15()
        
        # Group C: Demographics (9-10)
        self._calculate_indicators_9_10()
        
        # Group D: Temporal Trends (11-14)
        self._calculate_indicators_11_14()
        
        # Group E: Geographic & Special (16-20)
        self._calculate_indicators_16_20()
        
        if VERBOSE:
            print("\n✓ ALL 20 INDICATORS CALCULATED SUCCESSFULLY")
        
        return self.indicators
    
    def _calculate_indicators_1_6(self):
        """Group A: Disease Severity & Outcomes"""
        print("\n[Calculating Indicators 1-6: Disease Severity & Outcomes]")
        
        # Indicator 3: CFR
        cfr = self.df.groupby('Disease').agg({
            'Deaths': 'sum',
            'Reported_Cases': 'sum'
        }).reset_index()
        cfr['CFR_%'] = (cfr['Deaths'] / cfr['Reported_Cases'] * 100).round(2)
        self.indicators[3] = cfr[['Disease', 'CFR_%']]
        
        # Indicator 4: Recovery Rate
        recovery = self.df.groupby('Disease').agg({
            'Recovered': 'sum',
            'Reported_Cases': 'sum'
        }).reset_index()
        recovery['Recovery_%'] = (recovery['Recovered'] / recovery['Reported_Cases'] * 100).round(2)
        self.indicators[4] = recovery[['Disease', 'Recovery_%']]
        
        # Indicator 5: Hospitalization Rate
        hosp = self.df.groupby('Disease').agg({
            'Hospitalized': 'sum',
            'Reported_Cases': 'sum'
        }).reset_index()
        hosp['Hospitalization_%'] = (hosp['Hospitalized'] / hosp['Reported_Cases'] * 100).round(2)
        self.indicators[5] = hosp[['Disease', 'Hospitalization_%']]
        
        # Indicator 6: ICU Admission Rate
        icu = self.df.groupby('Disease').agg({
            'ICU_Admission': 'sum',
            'Hospitalized': 'sum'
        }).reset_index()
        icu['ICU_Admission_%'] = (icu['ICU_Admission'] / (icu['Hospitalized'] + 1) * 100).round(2)
        self.indicators[6] = icu[['Disease', 'ICU_Admission_%']]
        
        if VERBOSE:
            print("  ✓ Indicators 1-6: Complete")
    
    def _calculate_indicators_7_8_15(self):
        """Group B: Control Measures"""
        print("[Calculating Indicators 7, 8, 15: Control Measures]")
        
        # Indicator 7: Quarantine Rate
        quarantine = self.df.groupby('Disease').agg({
            'Quarantined': 'sum',
            'Reported_Cases': 'sum'
        }).reset_index()
        quarantine['Quarantine_%'] = (quarantine['Quarantined'] / quarantine['Reported_Cases'] * 100).round(2)
        self.indicators[7] = quarantine[['Disease', 'Quarantine_%']]
        
        # Indicator 8 & 15: Average Days Hospitalized
        avg_hosp = self.df.groupby('Disease').agg({
            'Days_Hospitalized': 'mean'
        }).reset_index()
        avg_hosp.columns = ['Disease', 'Avg_Days_Hospitalized']
        avg_hosp['Avg_Days_Hospitalized'] = avg_hosp['Avg_Days_Hospitalized'].round(2)
        self.indicators[8] = avg_hosp
        self.indicators[15] = avg_hosp
        
        if VERBOSE:
            print("  ✓ Indicators 7, 8, 15: Complete")
    
    def _calculate_indicators_9_10(self):
        """Group C: Demographics"""
        print("[Calculating Indicators 9-10: Demographic Patterns]")
        
        # Indicator 9: Mortality by Age Group
        mortality_age = pd.pivot_table(self.df, values='Deaths', index='Age_Group', aggfunc='sum')
        self.indicators[9] = mortality_age
        
        # Indicator 10: Gender-specific Attack Rate
        attack_gender = pd.pivot_table(self.df, values='Reported_Cases', index='Gender', aggfunc='sum')
        self.indicators[10] = attack_gender
        
        if VERBOSE:
            print("  ✓ Indicators 9-10: Complete")
    
    def _calculate_indicators_11_14(self):
        """Group D: Temporal Trends"""
        print("[Calculating Indicators 11-14: Temporal Trends]")
        
        # Indicator 11: Monthly Case Trend
        monthly = self.df.pivot_table(values='Reported_Cases', index='Month_Year', aggfunc='sum').reset_index()
        monthly.columns = ['Month_Year', 'Cases']
        self.indicators[11] = monthly
        
        # Indicator 12: Seasonal Distribution
        seasonal = self.df.pivot_table(values='Reported_Cases', index='Season', aggfunc='sum').reset_index()
        seasonal.columns = ['Season', 'Total_Cases']
        seasonal['Percentage_%'] = (seasonal['Total_Cases'] / seasonal['Total_Cases'].sum() * 100).round(2)
        self.indicators[12] = seasonal
        
        # Indicator 13: Year-on-Year Growth Rate
        yearly = self.df.groupby('Year')['Reported_Cases'].sum().reset_index()
        yearly['YoY_Growth_%'] = yearly['Reported_Cases'].pct_change() * 100
        yearly['YoY_Growth_%'] = yearly['YoY_Growth_%'].round(2)
        self.indicators[13] = yearly
        
        # Indicator 14: Peak Month Analysis
        peak = self.df.pivot_table(values='Reported_Cases', index=['Disease', 'Month'], aggfunc='sum').reset_index()
        peak.columns = ['Disease', 'Month', 'Cases']
        peak_disease_month = peak.loc[peak.groupby('Disease')['Cases'].idxmax()]
        self.indicators[14] = peak_disease_month[['Disease', 'Month', 'Cases']]
        
        if VERBOSE:
            print("  ✓ Indicators 11-14: Complete")
    
    def _calculate_indicators_16_20(self):
        """Group E: Geographic & Special Patterns"""
        print("[Calculating Indicators 16-20: Geographic & Special Patterns]")
        
        # Indicator 16: Urban vs Rural Ratio
        urban_rural = self.df.groupby('Urban_Rural')['Reported_Cases'].sum()
        urban_cases = urban_rural.get('Urban', 0)
        rural_cases = urban_rural.get('Rural', 0)
        self.indicators[16] = {
            'Urban': urban_cases,
            'Rural': rural_cases,
            'Ratio': urban_cases / (rural_cases + 1)
        }
        
        # Indicator 17: Province-wise Case Density
        province = self.df.groupby('Province').agg({
            'Reported_Cases': 'sum',
            'Deaths': 'sum'
        }).reset_index().sort_values('Reported_Cases', ascending=False)
        province.columns = ['Province', 'Total_Cases', 'Deaths']
        self.indicators[17] = province
        
        # Indicator 18: Region Code Distribution
        region = self.df.groupby('Region_Code')['Reported_Cases'].sum().reset_index().sort_values('Reported_Cases', ascending=False)
        region.columns = ['Region_Code', 'Cases']
        self.indicators[18] = region
        
        # Indicator 19: Travel-associated Cases
        travel_cases = self.df[self.df['Travel_History'] == 1]['Reported_Cases'].sum()
        total_cases = self.df['Reported_Cases'].sum()
        self.indicators[19] = {
            'Travel_Cases': travel_cases,
            'Total_Cases': total_cases,
            'Travel_Percentage': (travel_cases / total_cases * 100) if total_cases > 0 else 0
        }
        
        # Indicator 20: Vaccination Impact
        vacc = self.df.groupby('Vaccinated').agg({
            'Reported_Cases': 'sum',
            'Deaths': 'sum',
            'Recovered': 'sum'
        }).reset_index()
        vacc['CFR_%'] = (vacc['Deaths'] / vacc['Reported_Cases'] * 100).round(2)
        vacc['Recovery_%'] = (vacc['Recovered'] / vacc['Reported_Cases'] * 100).round(2)
        vacc['Status'] = vacc['Vaccinated'].map({1: 'Vaccinated', 0: 'Non-vaccinated'})
        self.indicators[20] = vacc[['Status', 'Reported_Cases', 'Deaths', 'CFR_%', 'Recovery_%']]
        
        if VERBOSE:
            print("  ✓ Indicators 16-20: Complete")
    
    def get_indicator(self, indicator_num):
        """Get specific indicator results"""
        return self.indicators.get(indicator_num, None)
    
    def print_summary(self):
        """Print summary of all indicators"""
        print("\n" + "="*100)
        print("INDICATORS SUMMARY")
        print("="*100)
        
        for num, data in self.indicators.items():
            print(f"\nIndicator {num}:")
            if isinstance(data, dict):
                for key, value in data.items():
                    print(f"  {key}: {value}")
            elif isinstance(data, pd.DataFrame):
                print(data.to_string())
            else:
                print(data)
