import sys
import os
import logging
from datetime import datetime
from pathlib import Path
 
import pandas as pd
import numpy as np
# from sqlalchemy import create_engine, text

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("etl")

CSV_PATH = r"C:\Users\monil\OneDrive\Documents\Data_Analyst_Project\DOHMH_New_York_City_Restaurant_Inspection_Results_20260603.csv"

DB_URL = (
    f"postgresql+psycopg2://"
    f"{os.getenv('DB_USER', 'postgres')}:"
    f"{os.getenv('DB_PASSWORD', 'password')}@"
    f"{os.getenv('DB_HOST', 'localhost')}:"
    f"{os.getenv('DB_PORT', '5432')}/"
    f"{os.getenv('DB_NAME', 'analytics')}"
)

NUMERIC_SENTINEL = 0
STRING_SENTINEL = "Unknown"
DATE_SENTINEL = pd.Timestamp("1900-01-01")
 
# Subset of columns that must ALL match to consider a row a duplicate
DEDUP_SUBSET: list[str] | None = None  # None = all columns

def extract(path: str) -> pd.DataFrame:
    log.info("EXTRACT  reading %s", path)
    df = pd.read_csv(path, low_memory=False)
    log.info("         shape  %s rows × %s cols", *df.shape)
    return df

def clean_missing(df: pd.DataFrame) -> pd.DataFrame:
    log.info("CLEAN    filling missing values with sentinels")
 
    before = df.isnull().sum().sum()
 
    for col in df.columns:
        if df[col].isnull().sum() == 0:
            continue
 
        if pd.api.types.is_numeric_dtype(df[col]):
            df[col] = df[col].fillna(NUMERIC_SENTINEL)
        elif pd.api.types.is_datetime64_any_dtype(df[col]):
            df[col] = df[col].fillna(DATE_SENTINEL)
        else:
            df[col] = df[col].fillna(STRING_SENTINEL)
 
    after = df.isnull().sum().sum()
    log.info("         nulls before=%d  after=%d", before, after)
    return df

def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    before = len(df)
    df = df.drop_duplicates(subset=DEDUP_SUBSET or None, keep="first")
    removed = before - len(df)
    log.info("DEDUP    removed %d duplicate rows  (%d remaining)", removed, len(df))
    return df

def main():
    csv_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("data.csv")
    out_path  = csv_path.parent / f"cleaned_{csv_path.name}"
 
    log.info("Input : %s", csv_path)
    df = pd.read_csv(csv_path, low_memory=False)
    log.info("Loaded  %d rows × %d cols", *df.shape)
 
    df = clean_missing(df)
    # df = standardize_categories(df)
    # df = fix_dates(df)
    df = remove_duplicates(df)
 
    df.to_csv(out_path, index=False)
    log.info("Output: %s  (%d rows × %d cols)", out_path, *df.shape)
 
 
if __name__ == "__main__":
    main()
