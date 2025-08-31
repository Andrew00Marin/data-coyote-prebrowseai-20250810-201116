import streamlit as st
import requests

st.set_page_config(page_title="Data Coyote", page_icon="🐺")

st.title("🐺 Data Coyote — Minimal Dashboard (Cloud)")

st.subheader("API Health Check")

API_URL = "http://localhost:8000"  # ⚠️ replace later with hosted FastAPI URL

try:
    response = requests.get(API_URL)
    if response.status_code == 200:
        st.success("API is reachable ✅")
        st.json(response.json())
    else:
        st.error(f"API responded with status code {response.status_code}")
except Exception as e:
    st.error(f"API not reachable: {e}")

st.write("✅ Deployed on Streamlit Cloud")
