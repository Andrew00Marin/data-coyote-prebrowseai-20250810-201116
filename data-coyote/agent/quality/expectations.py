import pandas as pd
from agent.common.utils import get_logger

log = get_logger("quality")

def expect_non_empty(df: pd.DataFrame, name: str):
    if df.empty:
        raise AssertionError(f"{name} dataframe is empty.")
    log.info(f"{name}: row count OK ({len(df)})")

def expect_columns(df: pd.DataFrame, required_cols: list, name: str):
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise AssertionError(f"{name} missing required columns: {missing}")
    log.info(f"{name}: required columns present")
