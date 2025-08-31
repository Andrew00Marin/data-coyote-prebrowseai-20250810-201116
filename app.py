# app.py  — Data Coyote (Minimal Dashboard)
# -----------------------------------------
# Works in three modes automatically:
# - Local:   API_URL defaults to http://127.0.0.1:8000
# - Docker:  set env API_URL=http://datacoyote:8000 (service name in compose)
# - Cloud:   set env API_URL=https://<your-render>.onrender.com

import os
import requests
import pandas as pd
import streamlit as st

# ---------- Config ----------
st.set_page_config(page_title="Data Coyote", page_icon="🐺", layout="wide")

# Environment-driven backend URL
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000").rstrip("/")

# Unique key helper (prevents duplicate-key errors as app grows)
APP_ID = "dc"
PAGE_ID = "crime"
def k(name: str) -> str:
    return f"{APP_ID}:{PAGE_ID}:{name}"

st.title("🐺 Data Coyote – Minimal Dashboard (Cloud)")
st.subheader("Santa Fe Police Incidents")


# ---------- Data helpers ----------
@st.cache_data(show_spinner=False, ttl=60)
def fetch_crime(days_back: int, limit_rows: int) -> pd.DataFrame:
    """Fetch crime data from FastAPI and return as DataFrame."""
    url = f"{API_URL}/santafe/crime"
    params = {"days": int(days_back), "limit": int(limit_rows)}
    resp = requests.get(url, params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json() or []

    # Normalize JSON to DataFrame safely
    df = pd.json_normalize(data)
    return df


def latlon_columns(df: pd.DataFrame):
    """Try to find latitude/longitude column names, return (lat, lon) or (None, None)."""
    candidates = [
        ("latitude", "longitude"),
        ("lat", "lon"),
        ("lat", "lng"),
        ("y", "x"),
    ]
    lc = {c.lower(): c for c in df.columns}
    for a, b in candidates:
        if a in lc and b in lc:
            return lc[a], lc[b]
    return None, None


# ---------- Controls ----------
with st.form(key=k("crime_controls_form")):
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        lookback = st.slider("Days back", min_value=1, max_value=60, value=7, key=k("days_back"))
    with col2:
        max_rows = st.selectbox("Max rows", [200, 500, 1000], index=0, key=k("max_rows"))
    with col3:
        st.caption(f"API_URL: `{API_URL}`")
    submitted = st.form_submit_button("Load incidents", use_container_width=True)

# ---------- Results ----------
if submitted:
    try:
        df = fetch_crime(lookback, max_rows)

        if df.empty:
            st.warning("No data available for the selected range.")
        else:
            # Basic metrics
            left, right = st.columns(2)
            with left:
                st.metric("Rows returned", len(df))
            with right:
                st.metric("Days back", lookback)

            # Show table (first 500 rows to keep UI snappy)
            st.write("### Table preview")
            st.dataframe(df.head(500), use_container_width=True)

            # Optional map if lat/lon exist
            lat_col, lon_col = latlon_columns(df)
            if lat_col and lon_col:
                st.write("### Map")
                map_df = df[[lat_col, lon_col]].dropna()
                if not map_df.empty:
                    st.map(map_df.rename(columns={lat_col: "latitude", lon_col: "longitude"}))
                else:
                    st.info("No mappable coordinates in the current results.")
            else:
                st.info("Latitude/Longitude columns not found in this dataset.")

            # Download CSV
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"santafe_crime_last_{lookback}_days.csv",
                mime="text/csv",
                key=k("download_csv"),
            )

    except requests.HTTPError as e:
        st.error(f"HTTP error from backend: {e}")
    except requests.ConnectionError:
        st.error("Could not reach the API. Is the backend running and API_URL correct?")
    except Exception as e:
        st.error(f"Failed to load crime data: {e}")
else:
    st.info("Set your options and click **Load incidents** to fetch data.")

