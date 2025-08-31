import pandas as pd, requests
from io import BytesIO
from agent.common.utils import get_logger

log = get_logger("ingest.tourism")

def load_csv(p): return pd.read_csv(p)

def load_from_url(u):
    r = requests.get(u, timeout=45); r.raise_for_status()
    return pd.read_csv(BytesIO(r.content))

def _usable_url(u: str) -> bool:
    return isinstance(u, str) and u.startswith("http") and not u.strip().startswith("${")

def ingest(cfg: dict) -> pd.DataFrame:
    src = cfg["sources"]["tourism"]
    url = src.get("url","")
    if _usable_url(url):
        log.info(f"Fetching tourism data from URL: {url}")
        df = load_from_url(url)
    else:
        log.info(f"Reading local tourism data: {src['local_path']}")
        df = load_csv(src["local_path"])
    log.info(f"Ingested tourism rows: {len(df)}")
    return df
