import pandas as pd
from agent.common.utils import get_logger, env

log = get_logger("publish.gsheets")

def _get_client():
    try:
        import gspread
    except ImportError:
        raise RuntimeError("gspread not installed; install requirements or disable Sheets publishing in config.")
    creds_path = env("GOOGLE_APPLICATION_CREDENTIALS")
    if not creds_path:
        raise RuntimeError("GOOGLE_APPLICATION_CREDENTIALS not set; cannot publish to Google Sheets.")
    return gspread.service_account(filename=creds_path)

def _open_or_create_sheet(gc, spreadsheet_name: str):
    try:
        sh = gc.open(spreadsheet_name)
    except Exception as e:
        log.info(f"Creating spreadsheet: {spreadsheet_name} ({e})")
        sh = gc.create(spreadsheet_name)
    return sh

def publish_df(df: pd.DataFrame, spreadsheet_name: str, worksheet_name: str):
    try:
        import gspread  # noqa
    except ImportError:
        raise RuntimeError("gspread not installed; install requirements or disable Sheets publishing in config.")
    gc = _get_client()
    sh = _open_or_create_sheet(gc, spreadsheet_name)
    try:
        ws = sh.worksheet(worksheet_name)
        ws.clear()
    except Exception:
        ws = sh.add_worksheet(title=worksheet_name, rows="100", cols="26")
    ws.update([df.columns.tolist()] + df.astype(str).values.tolist())
    log.info(f"Wrote {len(df)} rows to Google Sheet '{spreadsheet_name}' tab '{worksheet_name}'")
