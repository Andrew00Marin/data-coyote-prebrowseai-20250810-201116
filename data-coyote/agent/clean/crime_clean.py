import pandas as pd
from agent.common.utils import get_logger

log = get_logger("clean.crime")

def _standardize(df: pd.DataFrame) -> pd.DataFrame:
    return df.rename(columns={c: c.strip().lower() for c in df.columns})

def _enrich_dates(df: pd.DataFrame, date_col: str) -> pd.DataFrame:
    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
    df = df.dropna(subset=[date_col])
    df["year"] = df[date_col].dt.year
    df["month"] = df[date_col].dt.month
    df["dow"] = df[date_col].dt.day_name()
    df["hour"] = df[date_col].dt.hour
    return df

ALLOWED_TYPES = {
    "ASSAULT":"Violent","ROBBERY":"Violent","HOMICIDE":"Violent",
    "BURGLARY":"Property","LARCENY":"Property","MOTOR VEHICLE THEFT":"Property","VANDALISM":"Property",
    "DRUG":"Other","DUI":"Other"
}

def _map_category(df: pd.DataFrame, type_col: str) -> pd.DataFrame:
    def mapper(x):
        if pd.isna(x): return "Other"
        u = str(x).strip().upper()
        for k,v in ALLOWED_TYPES.items():
            if k in u: return v
        return "Other"
    df["crime_category"] = df[type_col].apply(mapper)
    return df

def clean(df: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    src = cfg["sources"]["crime"]
    df = _standardize(df)
    date_col = src["date_column"].lower()
    if date_col not in df.columns:
        for alt in ["date","incident_datetime","incident_date","reported_date","data_year"]:
            if alt in df.columns:
                date_col = alt; break
    type_col = src["type_column"].lower()
    df = _enrich_dates(df, date_col)
    if type_col in df.columns:
        df = _map_category(df, type_col)
    df = df.drop_duplicates()
    log.info(f"Cleaned crime rows: {len(df)}")
    return df
