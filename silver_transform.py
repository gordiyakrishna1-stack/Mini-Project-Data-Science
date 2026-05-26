"""Silver layer transform script.
Loads raw Bronze data, applies cleaning and feature engineering, and writes the cleaned Silver dataset.
"""

from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine

from config import OUTPUT_DIR, YES_NO_COLUMNS
from data_loader import DataLoader

WAREHOUSE_DIR = OUTPUT_DIR / "warehouse"
BRONZE_DIR = WAREHOUSE_DIR / "bronze"
SILVER_DIR = WAREHOUSE_DIR / "silver"
DB_FILE = WAREHOUSE_DIR / "epidemic_warehouse.sqlite"


def compute_epidemiological_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    for col in ['Reported_Cases', 'Deaths', 'Recovered', 'Hospitalized', 'ICU_Admission']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    if 'Reported_Cases' in df.columns and 'Deaths' in df.columns:
        df['CFR'] = (df['Deaths'] / df['Reported_Cases'].replace(0, pd.NA) * 100).fillna(0)
    if 'Reported_Cases' in df.columns and 'Recovered' in df.columns:
        df['Recovery_Rate'] = (df['Recovered'] / df['Reported_Cases'].replace(0, pd.NA) * 100).fillna(0)
    if 'Reported_Cases' in df.columns and 'Hospitalized' in df.columns:
        df['Hospitalization_Rate'] = (df['Hospitalized'] / df['Reported_Cases'].replace(0, pd.NA) * 100).fillna(0)

    if 'Month' in df.columns:
        df['Month'] = pd.to_numeric(df['Month'], errors='coerce').fillna(0).astype(int)
    if 'Year' in df.columns:
        df['Year'] = pd.to_numeric(df['Year'], errors='coerce').fillna(0).astype(int)

    if 'Age_Group' in df.columns:
        df['Age_Group'] = df['Age_Group'].astype(str).str.strip().str.title()
    if 'Gender' in df.columns:
        df['Gender'] = df['Gender'].astype(str).str.strip().str.title()
    if 'Province' in df.columns:
        df['Province'] = df['Province'].astype(str).str.strip().str.title()
    if 'Disease' in df.columns:
        df['Disease'] = df['Disease'].astype(str).str.strip().str.title()

    if 'Month' in df.columns and 'Year' in df.columns:
        df['Month_Year'] = df['Month'].astype(str).str.zfill(2) + '-' + df['Year'].astype(str)

    if 'Reported_Cases' in df.columns and 'Recovered' in df.columns:
        df['Active_Cases'] = df['Reported_Cases'] - df['Recovered']

    if 'Days_Hospitalized' in df.columns:
        df['Days_Hospitalized'] = pd.to_numeric(df['Days_Hospitalized'], errors='coerce').fillna(0)
        df['Quarantine_Days'] = df['Days_Hospitalized'] * 0.5

    for col in YES_NO_COLUMNS:
        if col in df.columns:
            df[col] = df[col].replace({'Yes': 1, 'No': 0}).fillna(0).astype(int)

    return df


def transform_silver():
    SILVER_DIR.mkdir(parents=True, exist_ok=True)
    raw_file = BRONZE_DIR / "china_disease_data_Cleaned.csv"

    if not raw_file.exists():
        raise FileNotFoundError(f"Bronze raw file not found: {raw_file}")

    loader = DataLoader(raw_file)
    loader.load_data()
    loader.quality_check()
    loader.preprocess()
    df_silver = loader.get_data()
    df_silver = compute_epidemiological_features(df_silver)

    silver_filename = raw_file.stem + "_silver.csv"
    silver_path = SILVER_DIR / silver_filename
    df_silver.to_csv(silver_path, index=False)

    engine = create_engine(f"sqlite:///{DB_FILE}")
    df_silver.to_sql("Silver_Clean", engine, if_exists="replace", index=False)
    engine.dispose()

    print("\n[SILVER LAYER] Transform complete")
    print(f"  Silver file saved: {silver_path}")
    print(f"  SQLite table saved: Silver_Clean in {DB_FILE}")
    print(f"  Records: {len(df_silver)} rows")


if __name__ == "__main__":
    transform_silver()
