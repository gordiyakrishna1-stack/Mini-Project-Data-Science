"""Gold layer aggregation script.
Builds star schema dimension tables and the fact table from Silver data.
"""

from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine

from config import OUTPUT_DIR, AGE_GROUP_ORDER

WAREHOUSE_DIR = OUTPUT_DIR / "warehouse"
SILVER_DIR = WAREHOUSE_DIR / "silver"
GOLD_DIR = WAREHOUSE_DIR / "gold"
DB_FILE = WAREHOUSE_DIR / "epidemic_warehouse.sqlite"


def _season_from_month(month: int) -> str:
    if month in [12, 1, 2]:
        return 'Winter'
    if month in [3, 4, 5]:
        return 'Spring'
    if month in [6, 7, 8]:
        return 'Summer'
    return 'Autumn'


def build_dimensions(df: pd.DataFrame) -> dict:
    dims = {}

    disease_names = sorted(df['Disease'].dropna().unique())
    dims['Dim_Disease'] = pd.DataFrame({
        'Disease_ID': range(1, len(disease_names) + 1),
        'Disease_Name': disease_names,
        'Disease_Category': ['Unknown'] * len(disease_names),
        'Created_Date': pd.Timestamp.now()
    })

    province_rows = df[['Province', 'Region_Code', 'Urban_Rural']].drop_duplicates().copy()
    province_rows['Province_Name'] = province_rows['Province'].astype(str)
    province_rows = province_rows.sort_values('Province_Name').reset_index(drop=True)
    province_rows['Province_ID'] = province_rows.index + 1
    province_rows['Region_Name'] = province_rows['Province_Name'].apply(lambda x: f"Region_{abs(hash(x)) % 100}")
    province_rows['Created_Date'] = pd.Timestamp.now()
    dims['Dim_Province'] = province_rows[['Province_ID', 'Province_Name', 'Region_Code', 'Region_Name', 'Urban_Rural', 'Created_Date']]

    time_rows = df[['Year', 'Month']].drop_duplicates().sort_values(['Year', 'Month']).reset_index(drop=True)
    time_rows['Time_ID'] = time_rows.index + 1
    time_rows['Date_Key'] = pd.to_datetime(time_rows[['Year', 'Month']].assign(DAY=1))
    time_rows['Quarter'] = ((time_rows['Month'] - 1) // 3 + 1).astype(int)
    time_rows['Season'] = time_rows['Month'].apply(_season_from_month)
    time_rows['Week_Number'] = time_rows['Date_Key'].dt.isocalendar().week
    time_rows['Is_Weekend'] = time_rows['Date_Key'].dt.dayofweek >= 5
    time_rows['Created_Date'] = pd.Timestamp.now()
    dims['Dim_Time'] = time_rows[['Time_ID', 'Year', 'Month', 'Quarter', 'Season', 'Week_Number', 'Date_Key', 'Is_Weekend', 'Created_Date']]

    dims['Dim_AgeGroup'] = pd.DataFrame({
        'AgeGroup_ID': range(1, len(AGE_GROUP_ORDER) + 1),
        'Age_Range': AGE_GROUP_ORDER,
        'Lower_Bound': [0, 15, 25, 45, 65],
        'Upper_Bound': [14, 24, 44, 64, 150],
        'Age_Category': ['Children', 'Youth', 'Adults', 'Middle-aged', 'Elderly'],
        'Created_Date': pd.Timestamp.now()
    })

    dims['Dim_Gender'] = pd.DataFrame({
        'Gender_ID': [1, 2],
        'Gender': ['Male', 'Female'],
        'Gender_Code': ['M', 'F'],
        'Created_Date': pd.Timestamp.now()
    })

    dims['Dim_Vaccination'] = pd.DataFrame({
        'Vaccination_ID': [1, 2, 3],
        'Vaccination_Status': ['Vaccinated', 'Non-vaccinated', 'Unknown'],
        'Vaccinated_Indicator': [1, 0, -1],
        'Created_Date': pd.Timestamp.now()
    })

    dims['Dim_TravelHistory'] = pd.DataFrame({
        'TravelHistory_ID': [1, 2],
        'Travel_History': ['Travel History', 'Local Case'],
        'Travel_Indicator': [1, 0],
        'Created_Date': pd.Timestamp.now()
    })

    dims['Dim_Comorbidity'] = pd.DataFrame({
        'Comorbidity_ID': [1, 2],
        'Comorbidity_Status': ['Yes', 'No'],
        'Comorbidity_Indicator': [1, 0],
        'Created_Date': pd.Timestamp.now()
    })

    dims['Dim_LabConfirmation'] = pd.DataFrame({
        'LabConfirmation_ID': [1, 2],
        'Lab_Confirmation': ['Confirmed', 'Not Confirmed'],
        'Confirmation_Indicator': [1, 0],
        'Created_Date': pd.Timestamp.now()
    })

    dims['Dim_Quarantine'] = pd.DataFrame({
        'Quarantine_ID': [1, 2],
        'Quarantine_Status': ['Quarantined', 'Not Quarantined'],
        'Quarantine_Indicator': [1, 0],
        'Created_Date': pd.Timestamp.now()
    })

    dims['Dim_ICU'] = pd.DataFrame({
        'ICU_ID': [1, 2],
        'ICU_Status': ['ICU Admission', 'No ICU Admission'],
        'ICU_Indicator': [1, 0],
        'Created_Date': pd.Timestamp.now()
    })

    return dims


def build_fact(df: pd.DataFrame, dims: dict) -> pd.DataFrame:
    df = df.copy()

    df = df.merge(dims['Dim_Disease'][['Disease_ID', 'Disease_Name']], left_on='Disease', right_on='Disease_Name', how='left')
    df = df.merge(dims['Dim_Province'][['Province_ID', 'Province_Name']], left_on='Province', right_on='Province_Name', how='left')
    df = df.merge(dims['Dim_Time'][['Time_ID', 'Year', 'Month']], on=['Year', 'Month'], how='left')
    df = df.merge(dims['Dim_AgeGroup'][['AgeGroup_ID', 'Age_Range']], left_on='Age_Group', right_on='Age_Range', how='left')
    df = df.merge(dims['Dim_Gender'][['Gender_ID', 'Gender']], on='Gender', how='left')

    df['Vaccination_ID'] = df['Vaccinated'].map({1: 1, 0: 2}).fillna(3).astype(int)
    df['TravelHistory_ID'] = df.get('Travel_History', pd.Series([0] * len(df))).map({1: 1, 0: 2}).fillna(2).astype(int)
    df['Comorbidity_ID'] = df.get('Comorbidity', pd.Series([0] * len(df))).map({1: 1, 0: 2}).fillna(2).astype(int)
    df['LabConfirmation_ID'] = df.get('Lab_Confirmed', pd.Series([0] * len(df))).map({1: 1, 0: 2}).fillna(2).astype(int)
    df['Quarantine_ID'] = df.get('Quarantined', pd.Series([0] * len(df))).map({1: 1, 0: 2}).fillna(2).astype(int)
    df['ICU_ID'] = df.get('ICU_Admission', pd.Series([0] * len(df))).map({1: 1, 0: 2}).fillna(2).astype(int)

    fact = pd.DataFrame({
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
        'Quarantined': df.get('Quarantined', pd.Series([0] * len(df))).fillna(0).astype(int),
        'ICU_Admission': df.get('ICU_Admission', pd.Series([0] * len(df))).fillna(0).astype(int),
        'Days_Hospitalized': df.get('Days_Hospitalized', pd.Series([0] * len(df))).fillna(0).astype(float),
        'Contact_Tracing': df.get('Contact_Tracing', pd.Series([0] * len(df))).fillna(0).astype(int),
        'Lab_Confirmed': df.get('Lab_Confirmed', pd.Series([0] * len(df))).fillna(0).astype(int),
        'Follow_Up': df.get('Follow_Up', pd.Series([0] * len(df))).fillna(0).astype(int),
        'CFR': (df['Deaths'] / df['Reported_Cases'].replace(0, pd.NA) * 100).fillna(0).round(4),
        'Recovery_Rate': (df['Recovered'] / df['Reported_Cases'].replace(0, pd.NA) * 100).fillna(0).round(4),
        'Hospitalization_Rate': (df['Hospitalized'] / df['Reported_Cases'].replace(0, pd.NA) * 100).fillna(0).round(4),
        'ICU_Rate': (df['ICU_Admission'] / df['Reported_Cases'].replace(0, pd.NA) * 100).fillna(0).round(4),
        'Record_Source': 'Chinese Disease Analysis Dataset',
        'Load_Date': pd.Timestamp.now(),
        'Update_Date': pd.Timestamp.now(),
        'Record_Status': 'Active'
    })

    return fact


def save_gold(dims: dict, fact: pd.DataFrame):
    GOLD_DIR.mkdir(parents=True, exist_ok=True)
    engine = create_engine(f"sqlite:///{DB_FILE}")

    for name, df_dim in dims.items():
        path = GOLD_DIR / f"{name}.csv"
        df_dim.to_csv(path, index=False)
        df_dim.to_sql(name, engine, if_exists='replace', index=False)
        print(f"  Saved dimension: {path}")

    fact_path = GOLD_DIR / "Fact_Cases.csv"
    fact.to_csv(fact_path, index=False)
    fact.to_sql("Fact_Cases", engine, if_exists='replace', index=False)
    engine.dispose()
    print(f"  Saved fact table: {fact_path}")


def build_gold():
    silver_files = list(SILVER_DIR.glob("*_silver.csv"))
    if not silver_files:
        raise FileNotFoundError("No Silver CSV file found in the warehouse silver directory.")

    silver_path = silver_files[0]
    df_silver = pd.read_csv(silver_path)
    dims = build_dimensions(df_silver)
    fact = build_fact(df_silver, dims)
    save_gold(dims, fact)

    print("\n[GOLD LAYER] Aggregation complete")
    print(f"  Source Silver file: {silver_path}")
    print(f"  Gold directory: {GOLD_DIR}")
    print(f"  Warehouse DB: {DB_FILE}")
    print(f"  Fact rows: {len(fact)}")


if __name__ == "__main__":
    build_gold()
