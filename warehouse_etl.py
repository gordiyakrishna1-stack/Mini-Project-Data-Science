import sqlite3
from pathlib import Path
import pandas as pd

from config import DATA_FILE, OUTPUT_DIR, SEASON_ORDER, AGE_GROUP_ORDER, YES_NO_COLUMNS
from data_loader import DataLoader

WAREHOUSE_DIR = OUTPUT_DIR / "warehouse"
BRONZE_DIR = WAREHOUSE_DIR / "bronze"
SILVER_DIR = WAREHOUSE_DIR / "silver"
GOLD_DIR = WAREHOUSE_DIR / "gold"
DB_FILE = WAREHOUSE_DIR / "epidemic_warehouse.sqlite"


def _ensure_directories():
    for path in [WAREHOUSE_DIR, BRONZE_DIR, SILVER_DIR, GOLD_DIR]:
        path.mkdir(parents=True, exist_ok=True)


def _season_from_month(month):
    if month in [12, 1, 2]:
        return 'Winter'
    if month in [3, 4, 5]:
        return 'Spring'
    if month in [6, 7, 8]:
        return 'Summer'
    return 'Autumn'


def _title_case_series(series):
    return series.astype(str).str.strip().str.title()


class MedallionETL:
    """ETL implementation for Bronze, Silver, and Gold warehouse layers."""

    def __init__(self, source_path=DATA_FILE):
        self.source_path = Path(source_path)
        _ensure_directories()
        self.raw_path = BRONZE_DIR / self.source_path.name
        self.silver_path = SILVER_DIR / f"{self.source_path.stem}_silver.csv"
        self.dim_paths = {
            'Dim_Disease': GOLD_DIR / 'Dim_Disease.csv',
            'Dim_Province': GOLD_DIR / 'Dim_Province.csv',
            'Dim_Time': GOLD_DIR / 'Dim_Time.csv',
            'Dim_AgeGroup': GOLD_DIR / 'Dim_AgeGroup.csv',
            'Dim_Gender': GOLD_DIR / 'Dim_Gender.csv',
            'Dim_Vaccination': GOLD_DIR / 'Dim_Vaccination.csv',
            'Dim_TravelHistory': GOLD_DIR / 'Dim_TravelHistory.csv',
            'Dim_Comorbidity': GOLD_DIR / 'Dim_Comorbidity.csv',
            'Dim_LabConfirmation': GOLD_DIR / 'Dim_LabConfirmation.csv',
            'Dim_Quarantine': GOLD_DIR / 'Dim_Quarantine.csv',
            'Dim_ICU': GOLD_DIR / 'Dim_ICU.csv',
        }
        self.fact_path = GOLD_DIR / 'Fact_Cases.csv'
        self.data_raw = None
        self.data_silver = None
        self.dimensions = {}
        self.fact = None

    def run(self):
        print("\n" + "=" * 80)
        print("MEDALLION ETL PIPELINE: BRONZE → SILVER → GOLD")
        print("=" * 80)
        self.run_bronze()
        self.run_silver()
        self.run_gold()
        self.save_summary()
        print("\n✅ Medallion ETL completed successfully.")

    def run_bronze(self):
        print("\n[BRONZE LAYER] Ingesting raw data")
        self.data_raw = pd.read_csv(self.source_path)
        self.data_raw.to_csv(self.raw_path, index=False)
        print(f"✓ Bronze layer saved: {self.raw_path}")
        print(f"  Rows: {len(self.data_raw)} | Columns: {len(self.data_raw.columns)}")

    def run_silver(self):
        print("\n[SILVER LAYER] Cleaning and standardizing data")
        loader = DataLoader(self.source_path)
        loader.load_data()
        loader.quality_check()
        loader.preprocess()
        self.data_silver = loader.get_data().copy()
        self.data_silver = self._standardize_data(self.data_silver)
        self.data_silver = self._deduplicate(self.data_silver)
        self.data_silver.to_csv(self.silver_path, index=False)
        print(f"✓ Silver layer saved: {self.silver_path}")
        print(f"  Rows after deduplication: {len(self.data_silver)}")

    def run_gold(self):
        print("\n[GOLD LAYER] Building star schema tables")
        self._build_dimensions()
        self._build_fact_table()
        self._save_gold_tables()
        self._save_sqlite()
        print(f"✓ Gold layer saved to CSV under: {GOLD_DIR}")
        print(f"✓ Gold layer SQLite database saved: {DB_FILE}")

    def _standardize_data(self, df):
        text_columns = ['Disease', 'Province', 'Age_Group', 'Gender', 'Season', 'Urban_Rural']
        for col in text_columns:
            if col in df.columns:
                df[col] = _title_case_series(df[col])

        if 'Region_Code' in df.columns:
            df['Region_Code'] = pd.to_numeric(df['Region_Code'], errors='coerce').fillna(-1).astype(int)

        for col in YES_NO_COLUMNS:
            if col in df.columns:
                df[col] = df[col].replace({0: 0, 1: 1}).fillna(0).astype(int)

        if 'Month' in df.columns:
            df['Month'] = pd.to_numeric(df['Month'], errors='coerce').fillna(0).astype(int)
        if 'Year' in df.columns:
            df['Year'] = pd.to_numeric(df['Year'], errors='coerce').fillna(0).astype(int)

        return df

    def _deduplicate(self, df):
        before = len(df)
        df = df.drop_duplicates()
        after = len(df)
        removed = before - after
        print(f"  Removed {removed} duplicate rows")
        return df

    def _build_dimensions(self):
        df = self.data_silver
        self.dimensions['Dim_Disease'] = pd.DataFrame({
            'Disease_ID': range(1, len(df['Disease'].dropna().unique()) + 1),
            'Disease_Name': sorted(df['Disease'].dropna().unique()),
            'Disease_Category': ['Unknown'] * df['Disease'].nunique(),
            'Created_Date': pd.Timestamp.now()
        })

        province_group = df.groupby('Province', dropna=False).agg({
            'Region_Code': lambda values: int(pd.to_numeric(values, errors='coerce').dropna().mode().iloc[0]) if len(pd.to_numeric(values, errors='coerce').dropna()) > 0 else -1,
            'Urban_Rural': lambda values: values.mode().iloc[0] if len(values.mode()) > 0 else 'Unknown'
        }).reset_index()
        province_group = province_group.sort_values(['Province']).reset_index(drop=True)
        province_group['Province_ID'] = province_group.index + 1
        province_group['Region_Name'] = province_group['Province'].apply(lambda x: 'Region ' + str(abs(hash(x)) % 100))
        province_group['Created_Date'] = pd.Timestamp.now()
        self.dimensions['Dim_Province'] = province_group[['Province_ID', 'Province', 'Region_Code', 'Region_Name', 'Urban_Rural', 'Created_Date']].rename(columns={
            'Province': 'Province_Name'
        })

        time_rows = df[['Year', 'Month']].drop_duplicates().sort_values(['Year', 'Month']).reset_index(drop=True)
        time_rows['Time_ID'] = time_rows.index + 1
        time_rows['Date_Key'] = pd.to_datetime(time_rows[['Year', 'Month']].assign(DAY=1))
        time_rows['Quarter'] = ((time_rows['Month'] - 1) // 3 + 1).astype(int)
        time_rows['Season'] = time_rows['Month'].apply(_season_from_month)
        time_rows['Week_Number'] = time_rows['Date_Key'].dt.isocalendar().week
        time_rows['Is_Weekend'] = time_rows['Date_Key'].dt.dayofweek >= 5
        time_rows['Created_Date'] = pd.Timestamp.now()
        self.dimensions['Dim_Time'] = time_rows[['Time_ID', 'Year', 'Month', 'Quarter', 'Season', 'Week_Number', 'Date_Key', 'Is_Weekend', 'Created_Date']]

        age_groups = pd.DataFrame({
            'AgeGroup_ID': range(1, len(AGE_GROUP_ORDER) + 1),
            'Age_Range': AGE_GROUP_ORDER,
            'Lower_Bound': [0, 15, 25, 45, 65],
            'Upper_Bound': [14, 24, 44, 64, 150],
            'Age_Category': ['Children', 'Youth', 'Adults', 'Middle-aged', 'Elderly'],
            'Created_Date': pd.Timestamp.now()
        })
        self.dimensions['Dim_AgeGroup'] = age_groups

        gender_rows = pd.DataFrame({
            'Gender_ID': [1, 2],
            'Gender': ['Male', 'Female'],
            'Gender_Code': ['M', 'F'],
            'Created_Date': pd.Timestamp.now()
        })
        self.dimensions['Dim_Gender'] = gender_rows

        self.dimensions['Dim_Vaccination'] = pd.DataFrame({
            'Vaccination_ID': [1, 2, 3],
            'Vaccination_Status': ['Vaccinated', 'Non-vaccinated', 'Unknown'],
            'Vaccinated_Indicator': [1, 0, -1],
            'Created_Date': pd.Timestamp.now()
        })

        self.dimensions['Dim_TravelHistory'] = pd.DataFrame({
            'TravelHistory_ID': [1, 2],
            'Travel_History': ['Travel History', 'Local Case'],
            'Travel_Indicator': [1, 0],
            'Created_Date': pd.Timestamp.now()
        })

        self.dimensions['Dim_Comorbidity'] = pd.DataFrame({
            'Comorbidity_ID': [1, 2],
            'Comorbidity_Status': ['Yes', 'No'],
            'Comorbidity_Indicator': [1, 0],
            'Created_Date': pd.Timestamp.now()
        })

        self.dimensions['Dim_LabConfirmation'] = pd.DataFrame({
            'LabConfirmation_ID': [1, 2],
            'Lab_Confirmation': ['Confirmed', 'Not Confirmed'],
            'Confirmation_Indicator': [1, 0],
            'Created_Date': pd.Timestamp.now()
        })

        self.dimensions['Dim_Quarantine'] = pd.DataFrame({
            'Quarantine_ID': [1, 2],
            'Quarantine_Status': ['Quarantined', 'Not Quarantined'],
            'Quarantine_Indicator': [1, 0],
            'Created_Date': pd.Timestamp.now()
        })

        self.dimensions['Dim_ICU'] = pd.DataFrame({
            'ICU_ID': [1, 2],
            'ICU_Status': ['ICU Admission', 'No ICU Admission'],
            'ICU_Indicator': [1, 0],
            'Created_Date': pd.Timestamp.now()
        })

        for name, df_dim in self.dimensions.items():
            df_dim.to_csv(self.dim_paths[name], index=False)
            print(f"  ✓ {name} saved ({len(df_dim)} rows)")

    def _build_fact_table(self):
        df = self.data_silver.copy()
        df = df.merge(self.dimensions['Dim_Disease'][['Disease_ID', 'Disease_Name']], left_on='Disease', right_on='Disease_Name', how='left')
        df = df.merge(self.dimensions['Dim_Province'][['Province_ID', 'Province_Name']], left_on='Province', right_on='Province_Name', how='left')
        df = df.merge(self.dimensions['Dim_Time'][['Time_ID', 'Year', 'Month']], on=['Year', 'Month'], how='left')
        df = df.merge(self.dimensions['Dim_AgeGroup'][['AgeGroup_ID', 'Age_Range']], left_on='Age_Group', right_on='Age_Range', how='left')
        df = df.merge(self.dimensions['Dim_Gender'][['Gender_ID', 'Gender']], on='Gender', how='left')

        df['Vaccination_ID'] = df['Vaccinated'].map({1: 1, 0: 2}).fillna(3).astype(int)
        df['TravelHistory_ID'] = df['Travel_History'].map({1: 1, 0: 2}).fillna(2).astype(int)
        df['Comorbidity_ID'] = df['Comorbidity'].map({1: 1, 0: 2}).fillna(2).astype(int)
        df['LabConfirmation_ID'] = df['Lab_Confirmed'].map({1: 1, 0: 2}).fillna(2).astype(int)
        df['Quarantine_ID'] = df['Quarantined'].map({1: 1, 0: 2}).fillna(2).astype(int)
        df['ICU_ID'] = df['ICU_Admission'].map({1: 1, 0: 2}).fillna(2).astype(int)

        fact_df = pd.DataFrame({
            'Disease_ID': df['Disease_ID'].fillna(0).astype(int),
            'Province_ID': df['Province_ID'].fillna(0).astype(int),
            'Time_ID': df['Time_ID'].fillna(0).astype(int),
            'AgeGroup_ID': df['AgeGroup_ID'].fillna(0).astype(int),
            'Gender_ID': df['Gender_ID'].fillna(0).astype(int),
            'Vaccination_ID': df['Vaccination_ID'],
            'TravelHistory_ID': df['TravelHistory_ID'],
            'Comorbidity_ID': df['Comorbidity_ID'],
            'LabConfirmation_ID': df['LabConfirmation_ID'],
            'Quarantine_ID': df['Quarantine_ID'],
            'ICU_ID': df['ICU_ID'],
            'Reported_Cases': df['Reported_Cases'].fillna(0).astype(int),
            'Deaths': df['Deaths'].fillna(0).astype(int),
            'Hospitalized': df['Hospitalized'].fillna(0).astype(int),
            'Recovered': df['Recovered'].fillna(0).astype(int),
            'Quarantined': df['Quarantined'].fillna(0).astype(int),
            'ICU_Admission': df['ICU_Admission'].fillna(0).astype(int),
            'Days_Hospitalized': df['Days_Hospitalized'].fillna(0).astype(float),
            'Contact_Tracing': df['Contact_Tracing'].fillna(0).astype(int),
            'Lab_Confirmed': df['Lab_Confirmed'].fillna(0).astype(int),
            'Follow_Up': df['Follow_Up'].fillna(0).astype(int),
            'CFR': (df['Deaths'] / df['Reported_Cases'].replace(0, pd.NA) * 100).fillna(0).round(4),
            'Recovery_Rate': (df['Recovered'] / df['Reported_Cases'].replace(0, pd.NA) * 100).fillna(0).round(4),
            'Hospitalization_Rate': (df['Hospitalized'] / df['Reported_Cases'].replace(0, pd.NA) * 100).fillna(0).round(4),
            'ICU_Rate': (df['ICU_Admission'] / df['Reported_Cases'].replace(0, pd.NA) * 100).fillna(0).round(4),
            'Record_Source': 'COVID-19 Surveillance Dataset',
            'Load_Date': pd.Timestamp.now(),
            'Update_Date': pd.Timestamp.now(),
            'Record_Status': 'Active'
        })

        fact_df.to_csv(self.fact_path, index=False)
        self.fact = fact_df
        print(f"  ✓ Fact_Cases saved ({len(fact_df)} rows)")

    def _save_gold_tables(self):
        for name, df_dim in self.dimensions.items():
            df_dim.to_csv(self.dim_paths[name], index=False)
        if self.fact is not None:
            self.fact.to_csv(self.fact_path, index=False)

    def _save_sqlite(self):
        conn = sqlite3.connect(DB_FILE)
        for name, df_dim in self.dimensions.items():
            df_dim.to_sql(name, conn, if_exists='replace', index=False)
        if self.fact is not None:
            self.fact.to_sql('Fact_Cases', conn, if_exists='replace', index=False)
        conn.close()

    def save_summary(self):
        print("\nWAREHOUSE SUMMARY")
        print("-" * 40)
        print(f"Bronze rows: {len(self.data_raw) if self.data_raw is not None else 0}")
        print(f"Silver rows: {len(self.data_silver) if self.data_silver is not None else 0}")
        print(f"Gold dimensions: {len(self.dimensions)}")
        print(f"Gold fact rows: {len(self.fact) if self.fact is not None else 0}")
        print(f"Warehouse DB: {DB_FILE}")
