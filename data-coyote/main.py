import os
import pandas as pd
from agent.common.utils import load_config, get_logger, env
from agent.ingest.crime_ingest import ingest as ingest_crime
from agent.ingest.tourism_ingest import ingest as ingest_tourism
from agent.clean.crime_clean import clean as clean_crime
from agent.clean.tourism_clean import clean as clean_tourism
from agent.publish.google_sheets_publish import publish_df
from agent.quality.expectations import expect_non_empty, expect_columns

print("\n   ╭━━━━━━╮\n   ┃  Data Coyote  ┃\n   ╰━╮     ╭━╯\n     ╰╮  ╭╯   Fast • Clever • Local Data\n      ╰━━╯\n")

log = get_logger("main")

def write_outputs(df: pd.DataFrame, name: str, out_dir: str):
    os.makedirs(out_dir, exist_ok=True)
    csv_path = os.path.join(out_dir, f"{name}.csv")
    df.to_csv(csv_path, index=False)
    log.info(f"Wrote {name} to {csv_path}")

def maybe_publish_to_sheets(cfg, crime_df, tourism_df):
    pub_cfg = cfg["publish"]["google_sheets"]
    creds = env("GOOGLE_APPLICATION_CREDENTIALS")
    ss_name = env(pub_cfg["spreadsheet_name_env"]) if pub_cfg.get("spreadsheet_name_env") else ""
    auto_enable = bool(creds and ss_name)
    enabled = bool(pub_cfg.get("enabled", False) or auto_enable)
    if not enabled:
        log.info("Google Sheets publish disabled (set creds + spreadsheet envs to auto-enable)")
        return
    if not ss_name:
        log.warning("Spreadsheet env var not set; skipping Sheets publish")
        return
    crime_tab = env(pub_cfg["crime_sheet_env"], "crime_data")
    tourism_tab = env(pub_cfg["tourism_sheet_env"], "tourism_data")
    try:
        publish_df(crime_df, ss_name, crime_tab)
        publish_df(tourism_df, ss_name, tourism_tab)
    except Exception as e:
        log.warning(f"Sheets publish skipped: {e}")

def run():
    cfg = load_config()
    raw_crime = ingest_crime(cfg)
    raw_tourism = ingest_tourism(cfg)
    expect_non_empty(raw_crime, "raw_crime")
    expect_non_empty(raw_tourism, "raw_tourism")
    crime = clean_crime(raw_crime, cfg)
    tourism = clean_tourism(raw_tourism, cfg)
    expect_columns(crime, ["year","month"], "crime")
    expect_columns(tourism, ["year","month"], "tourism")
    out_dir = cfg["publish"]["files"]["out_dir"]
    write_outputs(crime, "crime_latest", out_dir)
    write_outputs(tourism, "tourism_latest", out_dir)
    maybe_publish_to_sheets(cfg, crime, tourism)

if __name__ == "__main__":
    run()
