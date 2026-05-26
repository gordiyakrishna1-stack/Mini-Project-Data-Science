"""Bronze layer ingestion script.
Reads raw CSV data and stores it in the Bronze layer and SQLite warehouse.
"""

from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine

from config import DATA_FILE, OUTPUT_DIR

WAREHOUSE_DIR = OUTPUT_DIR / "warehouse"
BRONZE_DIR = WAREHOUSE_DIR / "bronze"
DB_FILE = WAREHOUSE_DIR / "epidemic_warehouse.sqlite"


def ingest_bronze():
    BRONZE_DIR.mkdir(parents=True, exist_ok=True)
    df_raw = pd.read_csv(DATA_FILE)

    raw_path = BRONZE_DIR / DATA_FILE.name
    df_raw.to_csv(raw_path, index=False)

    engine = create_engine(f"sqlite:///{DB_FILE}")
    df_raw.to_sql("Bronze_Raw", engine, if_exists="replace", index=False)
    engine.dispose()

    print("\n[BRONZE LAYER] Raw data ingestion complete")
    print(f"  Raw file saved: {raw_path}")
    print(f"  SQLite table saved: Bronze_Raw in {DB_FILE}")
    print(f"  Records: {len(df_raw)} rows")


if __name__ == "__main__":
    ingest_bronze()
