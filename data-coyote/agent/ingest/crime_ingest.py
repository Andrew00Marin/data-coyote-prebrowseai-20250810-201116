import pandas as pd, requests
from io import BytesIO
from agent.common.utils import get_logger, env

log = get_logger("ingest.crime")

def load_csv(p): return pd.read_csv(p)

def load_from_url(u):
    r = requests.get(u, timeout=45); r.raise_for_status()
    return pd.read_csv(BytesIO(r.content))

def _usable_url(u: str) -> bool:
    return isinstance(u, str) and u.startswith("http") and not u.strip().startswith("${")

def resolve_fbi_agency_url() -> str:
    api_key = env("FBI_API_KEY","").strip()
    if not api_key: return ""
    state = env("FBI_STATE_ABBR","NM").upper().strip()
    city  = env("FBI_CITY_NAME","SANTA FE").upper().strip()
    from_y = env("FBI_FROM_YEAR","2019").strip()
    to_y   = env("FBI_TO_YEAR","2025").strip()
    try:
        resp = requests.get(f"https://api.usa.gov/crime/fbi/sapi/api/agencies?state_abbr={state}&api_key={api_key}", timeout=45)
        resp.raise_for_status()
        agencies = resp.json()
    except Exception as e:
        log.warning(f"ORI lookup failed: {e}")
        return ""
    ori = ""
    if isinstance(agencies, list):
        exact = [a for a in agencies if str(a.get("city_name","")).upper()==city]
        contains = [a for a in agencies if city in str(a.get("city_name","")).upper()]
        for pool in (exact, contains, agencies):
            for a in pool:
                if a.get("ori"):
                    ori = a["ori"]
                    if "POLICE" in str(a.get("agency_name","")).upper(): break
            if ori: break
    if not ori:
        log.warning("ORI not found")
        return ""
    return (f"https://api.usa.gov/crime/fbi/sapi/api/summarized/agencies/{ori}/offense/reported/month"
            f"?from={from_y}&to={to_y}&format=csv&api_key={api_key}")

def ingest(cfg: dict) -> pd.DataFrame:
    src = cfg["sources"]["crime"]
    url = src.get("url","")
    if not _usable_url(url):
        resolved = resolve_fbi_agency_url()
        if _usable_url(resolved):
            url = resolved
    if _usable_url(url):
        log.info(f"Fetching crime data from URL: {url}")
        df = load_from_url(url)
    else:
        log.info(f"Reading local crime data: {src['local_path']}")
        df = load_csv(src["local_path"])
    log.info(f"Ingested crime rows: {len(df)}")
    return df
