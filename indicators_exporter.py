"""
Indicators Exporter Module
Exports all 20 health indicators to CSV format with detailed metadata
"""

import pandas as pd
import numpy as np
from datetime import datetime
from config import OUTPUT_DIR, VERBOSE


class IndicatorsExporter:
    """Handles export of health indicators to various formats"""
    
    def __init__(self, df, indicators_dict=None):
        self.df = df
        self.indicators_dict = indicators_dict or {}
        self.export_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
    def export_all_indicators_to_csv(self):
        """Export all 20 indicators to a single CSV file"""
        print("\n" + "="*100)
        print("EXPORTING ALL INDICATORS TO CSV")
        print("="*100)
        
        indicators_data = []
        
        # Indicator 1: Incidence Rate (per 100,000)
        total_cases = self.df['Reported_Cases'].sum()
        # Approximate population (using average)
        avg_population = 1_400_000_000  # China's population
        incidence_rate = (total_cases / avg_population) * 100_000
        indicators_data.append({
            'Indicator_Number': 1,
            'Indicator_Name': 'Incidence Rate per 100,000',
            'Value': round(incidence_rate, 2),
            'Unit': 'per 100,000 population',
            'Formula': 'Total Cases / Population × 100,000',
            'Data_Source': 'Reported Cases',
            'Calculation_Date': self.export_timestamp
        })
        
        # Indicator 2: Mortality Rate (per 100,000)
        total_deaths = self.df['Deaths'].sum()
        mortality_rate = (total_deaths / avg_population) * 100_000
        indicators_data.append({
            'Indicator_Number': 2,
            'Indicator_Name': 'Mortality Rate per 100,000',
            'Value': round(mortality_rate, 2),
            'Unit': 'per 100,000 population',
            'Formula': 'Total Deaths / Population × 100,000',
            'Data_Source': 'Deaths',
            'Calculation_Date': self.export_timestamp
        })
        
        # Indicator 3: Case Fatality Rate (CFR)
        cfr = (total_deaths / total_cases * 100) if total_cases > 0 else 0
        indicators_data.append({
            'Indicator_Number': 3,
            'Indicator_Name': 'Case Fatality Rate (CFR)',
            'Value': round(cfr, 2),
            'Unit': '%',
            'Formula': '(Total Deaths / Total Cases) × 100',
            'Data_Source': 'Deaths & Reported Cases',
            'Calculation_Date': self.export_timestamp
        })
        
        # Indicator 4: Recovery Rate
        total_recovered = self.df['Recovered'].sum()
        recovery_rate = (total_recovered / total_cases * 100) if total_cases > 0 else 0
        indicators_data.append({
            'Indicator_Number': 4,
            'Indicator_Name': 'Recovery Rate',
            'Value': round(recovery_rate, 2),
            'Unit': '%',
            'Formula': '(Total Recovered / Total Cases) × 100',
            'Data_Source': 'Recovered & Reported Cases',
            'Calculation_Date': self.export_timestamp
        })
        
        # Indicator 5: Hospitalization Rate
        total_hospitalized = self.df['Hospitalized'].sum()
        hospitalization_rate = (total_hospitalized / total_cases * 100) if total_cases > 0 else 0
        indicators_data.append({
            'Indicator_Number': 5,
            'Indicator_Name': 'Hospitalization Rate',
            'Value': round(hospitalization_rate, 2),
            'Unit': '%',
            'Formula': '(Total Hospitalized / Total Cases) × 100',
            'Data_Source': 'Hospitalized & Reported Cases',
            'Calculation_Date': self.export_timestamp
        })
        
        # Indicator 6: ICU Admission Rate
        total_icu = self.df['ICU_Admission'].sum()
        icu_rate = (total_icu / (total_hospitalized + 1) * 100) if total_hospitalized > 0 else 0
        indicators_data.append({
            'Indicator_Number': 6,
            'Indicator_Name': 'ICU Admission Rate',
            'Value': round(icu_rate, 2),
            'Unit': '%',
            'Formula': '(Total ICU Admissions / Total Hospitalized) × 100',
            'Data_Source': 'ICU Admission & Hospitalized',
            'Calculation_Date': self.export_timestamp
        })
        
        # Indicator 7: Vaccination Coverage
        vaccinated = self.df['Vaccinated'].sum()
        vaccination_coverage = (vaccinated / total_cases * 100) if total_cases > 0 else 0
        indicators_data.append({
            'Indicator_Number': 7,
            'Indicator_Name': 'Vaccination Coverage',
            'Value': round(vaccination_coverage, 2),
            'Unit': '%',
            'Formula': '(Vaccinated Cases / Total Cases) × 100',
            'Data_Source': 'Vaccinated & Reported Cases',
            'Calculation_Date': self.export_timestamp
        })
        
        # Indicator 8: Vaccination Effectiveness (CFR reduction)
        vaccinated_df = self.df[self.df['Vaccinated'] == 1]
        unvaccinated_df = self.df[self.df['Vaccinated'] == 0]
        
        vaccinated_cases = vaccinated_df['Reported_Cases'].sum()
        vaccinated_deaths = vaccinated_df['Deaths'].sum()
        vaccinated_cfr = (vaccinated_deaths / (vaccinated_cases + 1) * 100) if vaccinated_cases > 0 else 0
        
        unvaccinated_cases = unvaccinated_df['Reported_Cases'].sum()
        unvaccinated_deaths = unvaccinated_df['Deaths'].sum()
        unvaccinated_cfr = (unvaccinated_deaths / (unvaccinated_cases + 1) * 100) if unvaccinated_cases > 0 else 0
        
        effectiveness = ((unvaccinated_cfr - vaccinated_cfr) / unvaccinated_cfr * 100) if unvaccinated_cfr > 0 else 0
        indicators_data.append({
            'Indicator_Number': 8,
            'Indicator_Name': 'Vaccination Effectiveness',
            'Value': round(effectiveness, 2),
            'Unit': '%',
            'Formula': '((Unvaccinated CFR - Vaccinated CFR) / Unvaccinated CFR) × 100',
            'Data_Source': 'Vaccinated vs Unvaccinated CFR',
            'Calculation_Date': self.export_timestamp
        })
        
        # Additional indicators based on age groups
        age_group_cases = self.df.groupby('Age_Group')['Reported_Cases'].sum()
        age_65_plus_cases = age_group_cases.get('65+', 0)
        
        indicator_9_value = (age_65_plus_cases / total_cases * 100) if total_cases > 0 else 0
        indicators_data.append({
            'Indicator_Number': 9,
            'Indicator_Name': 'Proportion of Cases Age 65+',
            'Value': round(indicator_9_value, 2),
            'Unit': '%',
            'Formula': '(Cases Age 65+ / Total Cases) × 100',
            'Data_Source': 'Age Group Data',
            'Calculation_Date': self.export_timestamp
        })
        
        # Seasonal analysis
        seasonal_cases = self.df.groupby('Season')['Reported_Cases'].sum()
        winter_cases = seasonal_cases.get('Winter', 0)
        seasonal_indicator = (winter_cases / total_cases * 100) if total_cases > 0 else 0
        
        indicators_data.append({
            'Indicator_Number': 10,
            'Indicator_Name': 'Winter Season Case Proportion',
            'Value': round(seasonal_indicator, 2),
            'Unit': '%',
            'Formula': '(Winter Cases / Total Cases) × 100',
            'Data_Source': 'Seasonal Data',
            'Calculation_Date': self.export_timestamp
        })
        
        # Contact tracing rate
        contact_traced = self.df['Contact_Tracing'].sum()
        contact_tracing_rate = (contact_traced / total_cases * 100) if total_cases > 0 else 0
        indicators_data.append({
            'Indicator_Number': 11,
            'Indicator_Name': 'Contact Tracing Rate',
            'Value': round(contact_tracing_rate, 2),
            'Unit': '%',
            'Formula': '(Contact Traced / Total Cases) × 100',
            'Data_Source': 'Contact Tracing Data',
            'Calculation_Date': self.export_timestamp
        })
        
        # Lab confirmation rate
        lab_confirmed = self.df['Lab_Confirmed'].sum()
        lab_confirmation_rate = (lab_confirmed / total_cases * 100) if total_cases > 0 else 0
        indicators_data.append({
            'Indicator_Number': 12,
            'Indicator_Name': 'Laboratory Confirmation Rate',
            'Value': round(lab_confirmation_rate, 2),
            'Unit': '%',
            'Formula': '(Lab Confirmed / Total Cases) × 100',
            'Data_Source': 'Laboratory Confirmation Data',
            'Calculation_Date': self.export_timestamp
        })
        
        # Follow-up completion rate
        follow_up = self.df['Follow_Up'].sum()
        follow_up_rate = (follow_up / total_cases * 100) if total_cases > 0 else 0
        indicators_data.append({
            'Indicator_Number': 13,
            'Indicator_Name': 'Follow-up Completion Rate',
            'Value': round(follow_up_rate, 2),
            'Unit': '%',
            'Formula': '(Follow-up Completed / Total Cases) × 100',
            'Data_Source': 'Follow-up Data',
            'Calculation_Date': self.export_timestamp
        })
        
        # Quarantine rate
        quarantined = self.df['Quarantined'].sum()
        quarantine_rate = (quarantined / total_cases * 100) if total_cases > 0 else 0
        indicators_data.append({
            'Indicator_Number': 14,
            'Indicator_Name': 'Quarantine Rate',
            'Value': round(quarantine_rate, 2),
            'Unit': '%',
            'Formula': '(Quarantined / Total Cases) × 100',
            'Data_Source': 'Quarantine Data',
            'Calculation_Date': self.export_timestamp
        })
        
        # Average hospitalization days
        avg_hosp_days = self.df['Days_Hospitalized'].mean() if len(self.df) > 0 else 0
        indicators_data.append({
            'Indicator_Number': 15,
            'Indicator_Name': 'Average Hospitalization Days',
            'Value': round(avg_hosp_days, 2),
            'Unit': 'days',
            'Formula': 'Mean of Days Hospitalized',
            'Data_Source': 'Hospitalization Duration Data',
            'Calculation_Date': self.export_timestamp
        })
        
        # Gender distribution (Female cases)
        female_cases = len(self.df[self.df['Gender'] == 'F'])
        female_proportion = (female_cases / len(self.df) * 100) if len(self.df) > 0 else 0
        indicators_data.append({
            'Indicator_Number': 16,
            'Indicator_Name': 'Female Case Proportion',
            'Value': round(female_proportion, 2),
            'Unit': '%',
            'Formula': '(Female Cases / Total Cases) × 100',
            'Data_Source': 'Gender Data',
            'Calculation_Date': self.export_timestamp
        })
        
        # Comorbidity proportion
        comorbidity_cases = self.df['Comorbidity'].sum()
        comorbidity_prop = (comorbidity_cases / len(self.df) * 100) if len(self.df) > 0 else 0
        indicators_data.append({
            'Indicator_Number': 17,
            'Indicator_Name': 'Cases with Comorbidity',
            'Value': round(comorbidity_prop, 2),
            'Unit': '%',
            'Formula': '(Cases with Comorbidity / Total Cases) × 100',
            'Data_Source': 'Comorbidity Data',
            'Calculation_Date': self.export_timestamp
        })
        
        # Travel history
        travel_history = self.df['Travel_History'].sum()
        travel_prop = (travel_history / len(self.df) * 100) if len(self.df) > 0 else 0
        indicators_data.append({
            'Indicator_Number': 18,
            'Indicator_Name': 'Cases with Travel History',
            'Value': round(travel_prop, 2),
            'Unit': '%',
            'Formula': '(Cases with Travel History / Total Cases) × 100',
            'Data_Source': 'Travel History Data',
            'Calculation_Date': self.export_timestamp
        })
        
        # Fever symptom rate
        fever_cases = self.df['Symptom_Fever'].sum()
        fever_rate = (fever_cases / len(self.df) * 100) if len(self.df) > 0 else 0
        indicators_data.append({
            'Indicator_Number': 19,
            'Indicator_Name': 'Fever Symptom Rate',
            'Value': round(fever_rate, 2),
            'Unit': '%',
            'Formula': '(Cases with Fever / Total Cases) × 100',
            'Data_Source': 'Symptom Data',
            'Calculation_Date': self.export_timestamp
        })
        
        # Number of distinct diseases
        distinct_diseases = self.df['Disease'].nunique()
        indicators_data.append({
            'Indicator_Number': 20,
            'Indicator_Name': 'Number of Diseases Tracked',
            'Value': distinct_diseases,
            'Unit': 'count',
            'Formula': 'Count of Unique Disease Types',
            'Data_Source': 'Disease List',
            'Calculation_Date': self.export_timestamp
        })
        
        # Create DataFrame and export
        indicators_df = pd.DataFrame(indicators_data)
        csv_file = OUTPUT_DIR / 'indicators_summary.csv'
        indicators_df.to_csv(csv_file, index=False)
        
        if VERBOSE:
            print(f"\n✓ Indicators exported to: {csv_file}")
            print(f"\nIndicators Summary:")
            print(indicators_df[['Indicator_Number', 'Indicator_Name', 'Value', 'Unit']].to_string(index=False))
        
        return indicators_df
    
    def export_by_disease(self):
        """Export indicator breakdown by disease"""
        print("\nExporting disease-specific indicators...")
        
        disease_indicators = []
        
        for disease in self.df['Disease'].unique():
            disease_df = self.df[self.df['Disease'] == disease]
            
            cases = disease_df['Reported_Cases'].sum()
            deaths = disease_df['Deaths'].sum()
            recovered = disease_df['Recovered'].sum()
            hospitalized = disease_df['Hospitalized'].sum()
            
            cfr = (deaths / cases * 100) if cases > 0 else 0
            recovery_rate = (recovered / cases * 100) if cases > 0 else 0
            hosp_rate = (hospitalized / cases * 100) if cases > 0 else 0
            
            disease_indicators.append({
                'Disease': disease,
                'Total_Cases': cases,
                'Total_Deaths': deaths,
                'Total_Recovered': recovered,
                'Total_Hospitalized': hospitalized,
                'CFR_%': round(cfr, 2),
                'Recovery_%': round(recovery_rate, 2),
                'Hospitalization_%': round(hosp_rate, 2)
            })
        
        disease_df = pd.DataFrame(disease_indicators).sort_values('CFR_%', ascending=False)
        disease_file = OUTPUT_DIR / 'disease_indicators.csv'
        disease_df.to_csv(disease_file, index=False)
        
        if VERBOSE:
            print(f"✓ Disease indicators exported to: {disease_file}")
        
        return disease_df
    
    def export_by_geography(self):
        """Export indicator breakdown by province"""
        print("Exporting geographic indicators...")
        
        geo_indicators = []
        
        for province in self.df['Province'].unique():
            province_df = self.df[self.df['Province'] == province]
            
            cases = province_df['Reported_Cases'].sum()
            deaths = province_df['Deaths'].sum()
            recovered = province_df['Recovered'].sum()
            
            cfr = (deaths / cases * 100) if cases > 0 else 0
            recovery_rate = (recovered / cases * 100) if cases > 0 else 0
            
            urban_cases = len(province_df[province_df['Urban_Rural'] == 'Urban'])
            urban_pct = (urban_cases / len(province_df) * 100) if len(province_df) > 0 else 0
            
            geo_indicators.append({
                'Province': province,
                'Total_Cases': cases,
                'Total_Deaths': deaths,
                'CFR_%': round(cfr, 2),
                'Recovery_%': round(recovery_rate, 2),
                'Urban_%': round(urban_pct, 2),
                'Rural_%': round(100 - urban_pct, 2)
            })
        
        geo_df = pd.DataFrame(geo_indicators).sort_values('Total_Cases', ascending=False)
        geo_file = OUTPUT_DIR / 'geographic_indicators.csv'
        geo_df.to_csv(geo_file, index=False)
        
        if VERBOSE:
            print(f"✓ Geographic indicators exported to: {geo_file}")
        
        return geo_df
    
    def export_demographic_analysis(self):
        """Export demographic breakdown"""
        print("Exporting demographic analysis...")
        
        demographic_data = []
        
        # Age group analysis
        for age_group in self.df['Age_Group'].unique():
            age_df = self.df[self.df['Age_Group'] == age_group]
            
            # By gender
            for gender in age_df['Gender'].unique():
                gender_age_df = age_df[age_df['Gender'] == gender]
                
                cases = gender_age_df['Reported_Cases'].sum()
                deaths = gender_age_df['Deaths'].sum()
                cfr = (deaths / cases * 100) if cases > 0 else 0
                
                demographic_data.append({
                    'Age_Group': age_group,
                    'Gender': 'Male' if gender == 'M' else 'Female',
                    'Total_Cases': cases,
                    'Total_Deaths': deaths,
                    'CFR_%': round(cfr, 2),
                    'Proportion_of_Total': round((cases / self.df['Reported_Cases'].sum() * 100), 2)
                })
        
        demo_df = pd.DataFrame(demographic_data)
        demo_file = OUTPUT_DIR / 'demographic_indicators.csv'
        demo_df.to_csv(demo_file, index=False)
        
        if VERBOSE:
            print(f"✓ Demographic indicators exported to: {demo_file}")
        
        return demo_df
    
    def export_temporal_trends(self):
        """Export temporal trend data"""
        print("Exporting temporal trends...")
        
        temporal_data = []
        
        # Monthly trends for each year
        for year in sorted(self.df['Year'].unique()):
            for month in sorted(self.df[self.df['Year'] == year]['Month'].unique()):
                period_df = self.df[(self.df['Year'] == year) & (self.df['Month'] == month)]
                
                cases = period_df['Reported_Cases'].sum()
                deaths = period_df['Deaths'].sum()
                cfr = (deaths / cases * 100) if cases > 0 else 0
                
                temporal_data.append({
                    'Year': year,
                    'Month': int(month),
                    'Cases': cases,
                    'Deaths': deaths,
                    'CFR_%': round(cfr, 2)
                })
        
        temporal_df = pd.DataFrame(temporal_data).sort_values(['Year', 'Month'])
        temporal_file = OUTPUT_DIR / 'temporal_trends.csv'
        temporal_df.to_csv(temporal_file, index=False)
        
        if VERBOSE:
            print(f"✓ Temporal trends exported to: {temporal_file}")
        
        return temporal_df
    
    def export_all(self):
        """Export all indicator formats"""
        print("\n" + "="*100)
        print("EXPORTING ALL INDICATORS - COMPLETE")
        print("="*100)
        
        self.export_all_indicators_to_csv()
        self.export_by_disease()
        self.export_by_geography()
        self.export_demographic_analysis()
        self.export_temporal_trends()
        
        if VERBOSE:
            print("\n✓ ALL INDICATORS EXPORTED SUCCESSFULLY")
        
        return True
