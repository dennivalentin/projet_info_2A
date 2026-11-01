"""Streamlit page for Feature F4: Create a New Near-Earth Object (NEO).

Allows users to log newly observed NEOs. Objects are tagged with origin='USER'
to guarantee they are never overwritten during automatic NASA data imports.
"""

import streamlit as st

from utils.api_client import api_client
from utils.log_init import get_page_logger

logger = get_page_logger("create_neo")

st.set_page_config(page_title="NEO-Watch | Create NEO", page_icon="➕", layout="centered")

st.title("➕ Register a New NEO (F4)")
st.markdown(
    """
    Log an amateur observation or hypothetical Near-Earth Object into NEO-Watch.
    User-created objects are saved with **Origin: USER**, ensuring they remain preserved
    and distinct from official NASA data synchronizations.
    """
)

# Navigation
if st.button("⬅ Back to Explorer (F3)"):
    st.switch_page("pages/search_neo.py")

st.divider()

with st.form("create_neo_form"):
    st.subheader("📝 Object Characteristics")

    neo_name = st.text_input("Object Name *", placeholder="e.g., Asteroid-2026-X1")

    col1, col2 = st.columns(2)
    with col1:
        dia_min = st.number_input(
            "Estimated Min Diameter (km)",
            min_value=0.001,
            max_value=1000.0,
            value=0.150,
            step=0.01,
            format="%.3f",
        )
        magnitude = st.number_input(
            "Absolute Magnitude (H)",
            min_value=-10.0,
            max_value=40.0,
            value=22.5,
            step=0.1,
            format="%.1f",
        )

    with col2:
        dia_max = st.number_input(
            "Estimated Max Diameter (km)",
            min_value=0.001,
            max_value=1000.0,
            value=0.350,
            step=0.01,
            format="%.3f",
        )
        is_hazardous = st.checkbox("Potentially Hazardous Asteroid (PHA)", value=False)

    submitted = st.form_submit_button("🚀 Submit NEO", type="primary")

if submitted:
    if not neo_name.strip():
        st.error("Please provide a valid name for the NEO.")
    elif dia_min > dia_max:
        st.error("Minimum diameter cannot exceed maximum diameter.")
    else:
        payload = {
            "name": neo_name.strip(),
            "diameter_min": float(dia_min),
            "diameter_max": float(dia_max),
            "absolute_magnitude": float(magnitude),
            "hazardous": bool(is_hazardous),
        }

        with st.spinner("Submitting object to database..."):
            response = api_client.post("/neo", json=payload)

            if response and response.get("status_code") == 201:
                created_data = response.get("data", {})
                st.success(f"🎉 NEO **{created_data.get('name')}** created successfully! (ID: {created_data.get('neo_id')})")
                st.json(created_data)

                if st.button("🔍 View in Explorer"):
                    st.switch_page("pages/search_neo.py")
            else:
                err_msg = response.get("data") if response else "Unknown server error"
                st.error(f"Failed to create NEO: {err_msg}")
