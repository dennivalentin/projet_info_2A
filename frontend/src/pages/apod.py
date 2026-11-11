"""Streamlit page for Feature FO8: export NASA's Astronomy Picture of the Day."""

from datetime import date
from pathlib import Path

import requests
import streamlit as st

from utils.api_client import api_client
from utils.auth_guard import check_authentification
from utils.log_init import get_page_logger

logger = get_page_logger("apod")

st.set_page_config(page_title="NEO-Watch | Picture of the Day", page_icon="🌌", layout="wide")

st.title("🌌 Picture of the Day")
st.markdown("Not everything is about danger: the sky has always made people dream.")

check_authentification()

if st.button("⬅ Back to Menu"):
    st.switch_page("pages/neo_menu.py")

st.divider()

# Choose the day (APOD exists since 16 June 1995)
day = st.date_input("Day", value=date.today(), min_value=date(1995, 6, 16), max_value=date.today())

# Call the API
with st.spinner("Asking NASA..."):
    res = api_client.get(f"/apod/?day={day.isoformat()}")

if not res or res.get("status_code") != 200:
    err = res.get("data") if res else "Connection failed"
    st.error(f"Picture of the day unavailable: {err}")
    st.stop()

apod = res.get("data", {})
st.subheader(apod.get("title", ""))
st.caption(apod.get("date", "")[:10])

url = apod.get("url", "")

# Download the image so it can be shown and exported
image_bytes = None
try:
    r = requests.get(url, timeout=10)
    if r.ok and r.headers.get("Content-Type", "").startswith("image"):
        image_bytes = r.content
except requests.RequestException:
    logger.warning(f"Could not download {url}")

if image_bytes:
    st.image(image_bytes, use_container_width=True)
else:
    # Some days NASA publishes a video instead of an image
    st.info("Today's media is not an image (often a video).")
    st.link_button("Open on NASA's website", url)

st.write(apod.get("caption", ""))

# Export
st.divider()
st.subheader("📥 Export")
c1, c2 = st.columns(2)
if image_bytes:
    ext = Path(url).suffix or ".jpg"
    c1.download_button("Download the image", data=image_bytes,
                       file_name=f"apod_{day.isoformat()}{ext}")
c2.download_button(
    "Download the description (.txt)",
    data=f"{apod.get('title', '')}\n{apod.get('date', '')[:10]}\n\n{apod.get('caption', '')}\n\nSource: {url}",
    file_name=f"apod_{day.isoformat()}.txt",
)