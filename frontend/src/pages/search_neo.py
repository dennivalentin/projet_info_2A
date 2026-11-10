"""Streamlit page for Feature F3: Search and Explore Near-Earth Objects (NEOs).

Allows filtering by name, size, hazard flag, origin, and approach dates,
viewing detailed approaches with Astronomical Units (AU), and exporting results as CSV.
"""

from datetime import datetime
import pandas as pd
import streamlit as st

from utils.api_client import api_client
from utils.log_init import get_page_logger
from utils.auth_guard import check_authentification

logger = get_page_logger("search_neo")

st.set_page_config(
    page_title="NEO-Watch | Search & Explore", page_icon="🔭", layout="wide"
)

st.title("🔭 Near-Earth Objects (NEO) Explorer")
st.markdown("Search, inspect, and analyze Near-Earth Objects in the database.")

check_authentification()

# Top Navigation
col_nav1, col_nav2 = st.columns([1, 5])
with col_nav1:
    if st.button("⬅ Back to Menu"):
        st.switch_page("pages/neo_menu.py")
with col_nav2:
    if st.button("➕ Create a New NEO (F4)"):
        st.switch_page("pages/create_neo.py")

st.divider()

# Search Filters Section
st.subheader("🔍 Search Criteria")

with st.expander("Filter Options", expanded=True):
    col1, col2, col3 = st.columns(3)

    with col1:
        name_input = st.text_input(
            "Object Name (partial match)", placeholder="e.g. Apophis, 2024..."
        )
        origin_choice = st.selectbox("Origin", options=["All", "NASA", "USER"])

    with col2:
        hazard_choice = st.selectbox(
            "Hazard Status", options=["All", "Hazardous Only", "Non-Hazardous Only"]
        )
        sort_choice = st.selectbox(
            "Sort By",
            options=[
                "neo_id",
                "name",
                "diameter_min",
                "diameter_max",
                "hazardous",
                "date_update",
            ],
            index=0,
        )

    with col3:
        order_choice = st.selectbox("Order", options=["ASC", "DESC"], index=0)
        limit_val = st.number_input(
            "Max Results", min_value=10, max_value=500, value=100, step=10
        )

    col4, col5 = st.columns(2)
    with col4:
        use_dia_min = st.checkbox("Filter by Min Diameter (km)")
        dia_min = st.number_input(
            "Diameter Min >= (km)",
            min_value=0.0,
            value=0.1,
            step=0.05,
            disabled=not use_dia_min,
        )

    with col5:
        use_dia_max = st.checkbox("Filter by Max Diameter (km)")
        dia_max = st.number_input(
            "Diameter Max <= (km)",
            min_value=0.0,
            value=5.0,
            step=0.1,
            disabled=not use_dia_max,
        )

    search_clicked = st.button("🔎 Run Search", type="primary")

# Execute Search
if search_clicked or "search_results" not in st.session_state:
    payload = {
        "limit": int(limit_val),
        "sort_by": sort_choice,
        "order": order_choice,
    }

    if name_input.strip():
        payload["name"] = name_input.strip()

    if origin_choice != "All":
        payload["origin"] = origin_choice

    if hazard_choice == "Hazardous Only":
        payload["hazardous"] = True
    elif hazard_choice == "Non-Hazardous Only":
        payload["hazardous"] = False

    if use_dia_min:
        payload["diameter_min"] = float(dia_min)

    if use_dia_max:
        payload["diameter_max"] = float(dia_max)

    with st.spinner("Searching database..."):
        res = api_client.post("/neo/search", json=payload)
        if res and res.get("status_code") == 200:
            st.session_state["search_results"] = res.get("data", [])
        else:
            err = res.get("data") if res else "Connection failed"
            st.error(f"Search error: {err}")
            st.session_state["search_results"] = []

results = st.session_state.get("search_results", [])

# Display Results
st.subheader(f"📊 Results ({len(results)} found)")

if results:
    df = pd.DataFrame(results)

    # Format dataframe columns for display
    display_cols = [
        "neo_id",
        "name",
        "nasa_id",
        "hazardous",
        "diameter_min",
        "diameter_max",
        "origin",
    ]
    available_cols = [c for c in display_cols if c in df.columns]

    st.dataframe(
        df[available_cols],
        use_container_width=True,
        hide_index=True,
    )

    # CSV Export Button (F3 requirement)
    csv_data = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Export Results as CSV",
        data=csv_data,
        file_name=f"neo_search_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv",
    )

    st.divider()

    # Detailed View for a Selected NEO
    st.subheader("🔬 Object Details & Close Approaches")

    neo_options = {
        f"{r.get('name')} (ID: {r.get('neo_id')})": r.get("neo_id") for r in results
    }
    selected_label = st.selectbox(
        "Select a NEO to inspect details:", options=list(neo_options.keys())
    )

    if selected_label:
        selected_id = neo_options[selected_label]
        with st.spinner("Loading NEO details and close approaches..."):
            detail_res = api_client.get(f"/neo/{selected_id}")

            if detail_res and detail_res.get("status_code") == 200:
                neo_data = detail_res.get("data", {})

                det_col1, det_col2, det_col3 = st.columns(3)
                det_col1.metric("Name", neo_data.get("name"))
                det_col1.metric(
                    "NASA ID", neo_data.get("nasa_id") or "N/A (User submitted)"
                )

                hazard_status = (
                    "⚠️ Hazardous" if neo_data.get("hazardous") else "✅ Safe"
                )
                det_col2.metric("Hazard Flag", hazard_status)
                det_col2.metric("Origin", neo_data.get("origin"))

                d_min = neo_data.get("diameter_min")
                d_max = neo_data.get("diameter_max")
                size_str = (
                    f"{d_min:.3f} - {d_max:.3f} km"
                    if d_min is not None and d_max is not None
                    else "Unknown"
                )
                det_col3.metric("Estimated Diameter", size_str)
                det_col3.metric(
                    "Magnitude", f"{neo_data.get('absolute_magnitude') or 'N/A'}"
                )

                if neo_data.get("url_nasa"):
                    st.markdown(f"🔗 [NASA JPL Web Page]({neo_data.get('url_nasa')})")

                # Approaches Table
                approaches = neo_data.get("approaches", [])
                st.write(f"#### 🌍 Close Approaches ({len(approaches)} recorded)")

                if approaches:
                    appr_df = pd.DataFrame(approaches)
                    st.dataframe(
                        appr_df[
                            [
                                "approach_day",
                                "distance_km",
                                "distance_au",
                                "speed_km_h",
                                "body",
                            ]
                        ],
                        use_container_width=True,
                        hide_index=True,
                    )

                    appr_csv = appr_df.to_csv(index=False).encode("utf-8")
                    st.download_button(
                        label="📥 Export Close Approaches as CSV",
                        data=appr_csv,
                        file_name=f"approaches_{neo_data.get('name')}.csv",
                        mime="text/csv",
                    )
                else:
                    st.info(
                        "No close approaches currently recorded for this object in the database."
                    )
            else:
                st.error("Failed to fetch detailed information.")
else:
    st.info("No NEOs match the specified search criteria.")
