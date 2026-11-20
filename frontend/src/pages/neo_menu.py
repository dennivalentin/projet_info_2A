"""Streamlit main menu for NEO-Watch.

Gives access to every feature of the application, shows the new alert
notifications once logged in and, for administrators, the management tools.
The NASA data is updated by the backend itself, every day (FO7).
"""

import streamlit as st

from utils.api_client import api_client, error_message, fetch_new_notifications
from utils.auth_guard import check_authentification
from utils.log_init import get_page_logger

st.set_page_config(page_title="NEO-Watch | Menu", page_icon="🔭", layout="wide")

logger = get_page_logger("neo_menu")
check_authentification()

user = st.session_state.get("user") or {}
username = user.get("username", "Observer")

# (title, description, page) of each feature, displayed as cards on two columns
FEATURES = [
    (
        "☄️ Dashboard",
        "Upcoming close approaches, key figures of the period and your favourite NEOs.",
        "pages/dashboard.py",
    ),
    (
        "🔍 Search & Explore",
        "Search NEOs with several criteria, see their approaches in km and AU, export as CSV.",
        "pages/search_neo.py",
    ),
    (
        "📊 Statistics",
        "Size distribution, share of potentially hazardous objects and approaches per month.",
        "pages/statistics.py",
    ),
    (
        "⭐ Favourites",
        "Follow your favourite NEOs: their approaches and a graph of their distance to Earth.",
        "pages/favourites.py",
    ),
    (
        "🔔 Alerts",
        "Be notified when a NEO matches your criteria (size, distance, hazardous).",
        "pages/alert.py",
    ),
    (
        "➕ Declare a NEO",
        "Record your own observation of an asteroid (origin 'USER', never overwritten by NASA).",
        "pages/create_neo.py",
    ),
    (
        "🌌 Picture of the Day",
        "NASA's astronomy picture of the day, with its description, to download.",
        "pages/apod.py",
    ),
]

st.title("🔭 NEO-Watch")
st.markdown(f"Welcome, **{username}**! Choose a feature:")

# F6: the notifications are evaluated when the user logs in (once per session)
if not st.session_state.get("notifications_checked"):
    st.session_state["notifications_checked"] = True
    new_notifications = fetch_new_notifications()
    if new_notifications:
        with st.container(border=True):
            st.markdown(f"🔔 **{len(new_notifications)} new notification(s)**")
            for notification in new_notifications[:5]:
                st.warning(notification)
            if len(new_notifications) > 5:
                st.caption("See all of them on the Alerts page.")

columns = st.columns(2)
for index, (title, description, page) in enumerate(FEATURES):
    with columns[index % 2], st.container(border=True):
        st.subheader(title)
        st.write(description)
        if st.button(f"Open {title.split(' ', 1)[1]}", key=page, use_container_width=True):
            st.switch_page(page)

st.divider()

if st.button("🚪 Log out", type="secondary"):
    logger.info("Log out")
    st.session_state.clear()
    st.switch_page("pages/home.py")


status_res = api_client.get("/import/status")
if status_res.get("status_code") == 200 and status_res.get("data", {}).get("running"):
    st.info(
        "⏳ NASA data import in progress: the NEOs appear little by little "
        "in the search, the dashboard and the statistics."
    )


if user.get("role") == "admin":
    st.markdown("---")
    st.subheader("🛠️ Administration")

    last_res = api_client.get("/import/last")
    if last_res.get("status_code") == 200:
        last_date = last_res.get("data", {}).get("last_end_date")
        st.caption(
            f"NASA data imported up to **{last_date}**. It is updated automatically every day."
            if last_date
            else "No NASA data imported yet: the first import starts with the API."
        )

    col_users, col_reset, col_sync = st.columns(3)

    with col_users:
        if st.button("👥 Manage users", use_container_width=True):
            st.switch_page("pages/admin.py")

    with col_reset:
        if st.button("🗑️ Reset database", type="secondary", use_container_width=True):
            logger.info("Database reset requested by admin")
            with st.spinner("Reset in progress..."):
                response = api_client.post("/reset_database")

            if response.get("status_code") == 200:
                logger.info("Database successfully reset")
                st.toast("Database successfully reset ✅")
                st.rerun()
            else:
                logger.error("Error during database reset")
                st.error(f"Error: {error_message(response, 'Fail during the reset')}")

    with col_sync:
        if st.button("🔄 Manual update", type="primary", use_container_width=True):
            logger.info("Manual update requested by admin")
            response = api_client.post("/import/update")

            if response.get("status_code") == 200:
                result = response.get("data", {}).get("result", {})
                if result.get("status") == "running":
                    st.info("An import is already running")
                else:
                    st.toast("Update started in the background ✅")
            else:
                logger.error("Error during manual sync")
                st.error(f"Error: {error_message(response, 'Fail during import')}")
