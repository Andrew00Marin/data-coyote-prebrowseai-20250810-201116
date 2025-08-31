from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"name": "Data Coyote API", "status": "ok"}

@app.get("/health")
def health():
    return {"ok": True, "message": "pong"}
import os
import requests
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, Query

SOC_DOMAIN = os.getenv("SOC_DOMAIN", "")
SOC_DATASET = os.getenv("SOC_DATASET", "")
SOC_OFFENSE_FIELD = os.getenv("SOC_OFFENSE_FIELD", "offense")
SOC_TIME_FIELD = os.getenv("SOC_TIME_FIELD", "incident_datetime")
SOC_LOCATION_FIELD = os.getenv("SOC_LOCATION_FIELD", "location")

def _socrata_url():
    if not SOC_DOMAIN or not SOC_DATASET:
        raise HTTPException(status_code=500, detail="Socrata domain/dataset not configured")
    return f"https://{SOC_DOMAIN}/resource/{SOC_DATASET}.json"

def _iso(dt: datetime) -> str:
    # Socrata expects UTC ISO without subsecond for $where
    return dt.astimezone(timezone.utc).replace(microsecond=0).isoformat()

@app.get("/santafe/crime")
def santafe_crime(
    days: int = Query(7, ge=1, le=60, description="Lookback window in days"),
    limit: int = Query(500, ge=1, le=5000, description="Max rows to return"),
):
    """
    Returns recent incidents from the configured Santa Fe Socrata dataset.
    No API key required for most public datasets.
    """
    since = datetime.now(timezone.utc) - timedelta(days=days)

    # Build a safe SoQL where/order selecting only columns we need
    url = _socrata_url()
    select_cols = [
        SOC_TIME_FIELD,
        SOC_OFFENSE_FIELD,
        SOC_LOCATION_FIELD,
    ]
    params = {
        "$select": ", ".join(select_cols),
        "$where": f"{SOC_TIME_FIELD} >= '{_iso(since)}'",
        "$order": f"{SOC_TIME_FIELD} DESC",
        "$limit": limit,
    }

    r = requests.get(url, params=params, timeout=20)
    try:
        r.raise_for_status()
    except Exception:
        raise HTTPException(status_code=502, detail=f"Socrata error: {r.text[:300]}")

    items = r.json()

    # Normalize location to lat/lon if possible
    out = []
    for it in items:
        lat = lon = None
        loc = it.get(SOC_LOCATION_FIELD)
        # Socrata geolocation field is usually an object with 'latitude'/'longitude' or 'coordinates'
        if isinstance(loc, dict):
            lat = loc.get("latitude")
            lon = loc.get("longitude")
            if lat is None and "coordinates" in loc and isinstance(loc["coordinates"], list):
                # coordinates = [lon, lat]
                coords = loc["coordinates"]
                if len(coords) >= 2:
                    lon, lat = coords[0], coords[1]

        out.append({
            "datetime": it.get(SOC_TIME_FIELD),
            "offense": it.get(SOC_OFFENSE_FIELD),
            "latitude": float(lat) if lat not in (None, "") else None,
            "longitude": float(lon) if lon not in (None, "") else None,
        })
    return out

