"""Streamlit page for Feature FO3: statistics on Near-Earth Objects."""

import pandas as pd
import streamlit as st

from utils.api_client import api_client
from utils.log_init import get_page_logger

logger = get_page_logger("statistics")

st.set_page_config(page_title="NEO-Watch | Statistics", page_icon="📊", layout="wide")

st.title("📊 NEO Statistics")
st.markdown("Key figures and distributions computed on all the NEOs in the database.")

if st.button("⬅ Back to Menu"):
    st.switch_page("pages/player_menu.py")

st.divider()

# Call the API
with st.spinner("Computing statistics..."):
    res = api_client.get("/statistics")

if not res or res.get("status_code") != 200:
    err = res.get("data") if res else "Connection failed"
    st.error(f"Statistics error: {err}")
    st.stop()

data = res.get("data", {})
summary = data.get("summary", {})
why = data.get("justifications", {})

# Key figures
st.subheader("🔢 Key Figures")
c1, c2, c3 = st.columns(3)
c1.metric("NEOs in the database", summary.get("nb_neos", 0))
c2.metric("Potentially hazardous", f"{summary.get('hazardous_pct') or 0} %")
c3.metric("Median distance", f"{summary.get('median_distance_ld', '-')} LD")
st.caption(why.get("hazardous_pct", ""))
st.divider()

# Chart 1: approaches per month
st.subheader("📅 Approaches per Month")
monthly = data.get("approaches_per_month", [])
if monthly:
    df_month = pd.DataFrame(monthly).set_index("month")
    st.bar_chart(df_month["nb_approaches"])
    st.caption(why.get("approaches_per_month", ""))
else:
    st.info("No approach in the database.")

st.divider()

# Chart 2: size distribution
st.subheader("📏 Size Distribution")
sizes = data.get("size_distribution", [])
if sizes:
    df_size = pd.DataFrame(sizes).set_index("size_class")
    st.bar_chart(df_size["nb_neos"])
    st.caption(why.get("size_distribution", ""))
else:
    st.info("No NEO in the database.")
