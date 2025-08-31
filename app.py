import streamlit as st
import requests

st.set_page_config(page_title="Data Coyote", page_icon="🐺")

st.title("🐺 Data Coyote – Minimal Dashboard (Cloud)")
st.subheader("API Health Check")

# ✅ Use your Render backend URL here instead of localhost
API_URL = "https://data-coyote-prebrowseai-20250810-201116.onrender.com"

try:
    response = requests.get(API_URL + "/health")
    if response.status_code == 200:
        st.success("API is reachable ✅")
        st.json(response.json())
    else:
        st.error(f"API responded with status code {response.status_code}")
except Exception as e:
    st.error(f"API not reachable: {e}")

st.write("☑️ Deployed on Streamlit Cloud")
import pandas as pd

st.subheader("Santa Fe Police Incidents (last 7 days)")
with st.form("crime_controls"):
    lookback = st.slider("Days back", min_value=1, max_value=60, value=7)
    maxrows = st.selectbox("Max rows", [200, 500, 1000, 2000], index=1)
    submitted = st.form_submit_button("Load incidents")

if submitted:
    try:
        resp = requests.get(f"{API_URL}/santafe/crime", params={"days": lookback, "limit": maxrows}, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        if not data:
            st.info("No incidents in the selected window.")
        else:
            df = pd.DataFrame(data)
            # Basic cleaning
            if "datetime" in df.columns:
                df["datetime"] = pd.to_datetime(df["datetime"], errors="coerce")

            # KPI row
            c1, c2 = st.columns(2)
            c1.metric("Incidents", len(df))
            top = df["offense"].value_counts().head(1)
            c2.metric("Top offense", top.index[0] if len(top) else "—")

            # Top offenses bar chart
            st.markdown("**Top offenses**")
            st.bar_chart(df["offense"].value_counts().head(15))

            # Table
            st.markdown("**Recent incidents**")
            st.dataframe(df[["datetime", "offense"]].sort_values("datetime", ascending=False))

            # Map (if lat/lon present)
            if {"latitude", "longitude"}.issubset(df.columns):
                map_df = df[["latitude", "longitude"]].dropna()
                if not map_df.empty:
                    st.markdown("**Map**")
                    st.map(map_df.rename(columns={"latitude": "lat", "longitude": "lon"}))
                else:
                    st.info("No mappable coordinates in this window.")
    except Exception as e:
        st.error(f"Error loading incidents: {e}")

