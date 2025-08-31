import pandas as pd
from agent.common.utils import get_logger

log = get_logger("clean.tourism")

def _standardize(df: pd.DataFrame) -> pd.DataFrame:
    return df.rename(columns={c: c.strip().lower() for c in df.columns})

def _parse_month(df: pd.DataFrame, date_col: str) -> pd.DataFrame:
    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
    df = df.dropna(subset=[date_col])
    df["year"] = df[date_col].dt.year
    df["month"] = df[date_col].dt.month
    return df

def clean(df: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    src = cfg["sources"]["tourism"]
    df = _standardize(df)
    date_col = src["date_column"].lower()
    df = _parse_month(df, date_col)
    df = df.drop_duplicates()
    log.info(f"Cleaned tourism rows: {len(df)}")
    return df
