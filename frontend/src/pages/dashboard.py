"""Streamlit page for Feature F2: personal dashboard of the connected user."""

from datetime import date, datetime, timedelta

import pandas as pd
import streamlit as st

from utils.api_client import api_client

st.set_page_config(page_title="NEO-Watch | Dashboard", page_icon="☄️", layout="wide")

st.title("☄️ My Dashboard")
st.markdown("What is coming close to Earth, and what happens to your favourite NEOs.")

if st.button("⬅ Back to Menu"):
    st.switch_page("pages/player_menu.py")

st.divider()
st.subheader("📅 Period")
col_start, col_end = st.columns(2)
start = col_start.date_input("From", value=date.today())
end = col_end.date_input("To", value=date.today() + timedelta(days=7))
with st.spinner("Loading dashboard..."):
    res = api_client.get(
        "/dashboard", params={"start": start.isoformat(), "end": end.isoformat()}
    )

if not res or res.get("status_code") != 200:
    err = res.get("data") if res else "Connection failed"
    st.error(f"Dashboard error: {err}")
    st.stop()

data = res.get("data", {})
# Call the API
with st.spinner("Loading dashboard..."):
    res = api_client.get(
        "/dashboard", params={"start": start.isoformat(), "end": end.isoformat()}
    )

if not res or res.get("status_code") != 200:
    err = res.get("data") if res else "Connection failed"
    st.error(f"Dashboard error: {err}")
    st.stop()

data = res.get("data", {})
# Key figures
st.subheader("📊 Key Figures")
c1, c2, c3 = st.columns(3)
c1.metric("NEOs passing by", data.get("nb_neos", 0))
c2.metric("Potentially hazardous", data.get("nb_hazardous", 0))
c3.metric("Hazardous share", f"{data.get('hazardous_share_pct', 0)} %")
# Closest approach
st.subheader("🎯 Closest Approach")
closest = data.get("closest_approach")
if closest:
    hazard_status = "⚠️ Hazardous" if closest.get("hazardous") else "✅ Safe"
    d1, d2, d3 = st.columns(3)
    d1.metric("Name", closest.get("name"))
    d2.metric("Distance", f"{float(closest.get('distance', 0)):,.0f} km")
    d3.metric("Hazard Flag", hazard_status)
    st.caption(f"On {str(closest.get('approach_date', ''))[:16].replace('T', ' ')}")
else:
    st.info("No approach in this period.")

st.divider()
upcoming = data.get("upcoming_approaches", [])
st.subheader(f"🌍 Upcoming Approaches ({len(upcoming)})")
if upcoming:
    df = pd.DataFrame(upcoming)
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.download_button(
        label="📥 Export Approaches as CSV",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name=f"dashboard_approaches_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv",
    )
else:
    st.info("No approach in this period.")

st.divider()
# Favourites (personalised part)
favourites = data.get("favourites", [])
st.subheader(f"⭐ My Favourite NEOs ({len(favourites)})")
if favourites:
    st.dataframe(pd.DataFrame(favourites), use_container_width=True, hide_index=True)
else:
    st.info("You have no favourite NEO yet.")
