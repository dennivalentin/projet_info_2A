"""Streamlit page for the alerts: notifications, creation and management of alerts."""

import streamlit as st

from utils.api_client import api_client, error_message, fetch_new_notifications
from utils.auth_guard import check_authentification
from utils.log_init import get_page_logger

st.set_page_config(page_title="NEO-Watch | Alerts", page_icon="🔔", layout="wide")

st.title("NEO Alerts & Notifications")
logger = get_page_logger("alerts")

check_authentification()

user = st.session_state.get("user") or {}
user_id = user.get("user_id")


st.subheader("Triggered Notifications")
st.caption(
    "Each approach matching one of your active alerts is notified once. "
    "The notifications of this session are listed here, newest first."
)

with st.spinner("Checking for triggered alerts..."):
    fetch_new_notifications()

notifications = st.session_state.get("notifications", [])
if notifications:
    for notif in notifications:
        st.warning(notif)
else:
    st.info("No new notification. Nothing special to see.")

st.divider()


st.subheader("Create a New Alert")

with st.form("create_alert_form", clear_on_submit=True):
    alert_label = st.text_input(
        "Alert Label",
        placeholder="e.g. Hazardous big one",
        help="A name for your alert",
    )

    col1, col2 = st.columns(2)
    min_diam = col1.number_input(
        "Minimum Diameter (km)",
        min_value=0.0,
        value=None,
        step=0.1,
        placeholder="No limit (leave empty)",
        help="Leave empty for no minimum diameter filter",
    )
    max_dist = col2.number_input(
        "Maximum Distance (km)",
        min_value=0.0,
        value=None,
        step=10000.0,
        placeholder="No limit (leave empty)",
        help="Leave empty for no maximum distance filter",
    )

    hazardous_only = st.checkbox("Only Potentially Hazardous Asteroids", value=False)
    submit_create = st.form_submit_button("Create Alert", type="primary")

    if submit_create:
        if not alert_label.strip():
            st.error("Please provide a label for your alert.")
        else:
            alert_temp = {
                "user_id": user_id,
                "label": alert_label.strip(),
                "diameter_min": min_diam,
                "distance_max": max_dist,
                "hazardous_only": hazardous_only,
            }

            logger.info(f"Creating alert for user {user_id}: {alert_temp}")
            create_res = api_client.post("/alerts/", json=alert_temp)

            if create_res["status_code"] in (200, 201):
                st.success(f"Alert '{alert_label}' successfully created!")
                st.rerun()
            else:
                if create_res["status_code"] == 400:
                    st.error("Alert not created: you may already have one with these criteria.")
                else:
                    st.error(f"Failed to create alert: {error_message(create_res)}")

st.divider()


st.subheader("Your Monitored Alerts")

alerts_res = api_client.get(f"/alerts/user/{user_id}")

if alerts_res["status_code"] != 200:
    st.error("Failed to load your alerts.")
    st.stop()

alerts = alerts_res.get("data", [])

if not alerts:
    st.info("You haven't configured any alert yet.")
else:
    for alert in alerts:
        a_id = alert.get("alert_id")
        a_label = alert.get("label", f"Alert #{a_id}")
        is_active = alert.get("active", True)
        d_min = alert.get("diameter_min")
        d_max = alert.get("distance_max")
        haz_only = "Yes" if alert.get("hazardous_only") else "No"

        with st.container(border=True):
            col_info, col_toggle, col_delete = st.columns([4, 1.2, 1])

            with col_info:
                status_icon = "🟢 Active" if is_active else "⚪ Inactive"
                st.markdown(f"**{a_label}** — `{status_icon}`")
                st.caption(
                    f"Min Diameter: **{f'{d_min} km' if d_min is not None else 'any'}** | "
                    f"Max Distance: **{f'{d_max:,.0f} km' if d_max is not None else 'any'}** | "
                    f"Hazardous Only: **{haz_only}**"
                )

            with col_toggle:
                toggle_btn_label = "Turn off" if is_active else "Turn on"
                if st.button(toggle_btn_label, key=f"toggle_{a_id}"):
                    logger.info(f"Toggling alert {a_id}")
                    update_res = api_client.put(f"/alerts/{a_id}/toggle")
                    if update_res["status_code"] == 200:
                        st.success("Status updated")
                        st.rerun()
                    else:
                        st.error("Error updating status")

            with col_delete:
                if st.button("Delete", key=f"del_{a_id}"):
                    logger.info(f"Deleting alert {a_id}")
                    del_res = api_client.delete(f"/alerts/{a_id}")
                    if del_res["status_code"] in (200, 204):
                        st.success("Alert deleted")
                        st.rerun()
                    else:
                        st.error("Error while deleting alert")

st.divider()

if st.button("Back to menu"):
    st.switch_page("pages/neo_menu.py")
