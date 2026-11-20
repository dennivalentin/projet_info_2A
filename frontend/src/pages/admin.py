"""Streamlit page for administrators (F1): user accounts and connection history."""

import pandas as pd
import streamlit as st

from utils.api_client import api_client, error_message
from utils.auth_guard import check_authentification
from utils.log_init import get_page_logger

st.set_page_config(page_title="NEO-Watch | Users", page_icon="👥", layout="wide")

logger = get_page_logger("admin")
check_authentification()

current_user = st.session_state.get("user") or {}
if current_user.get("role") != "admin":
    st.error("This page is reserved to administrators.")
    if st.button("⬅ Back to Menu"):
        st.switch_page("pages/neo_menu.py")
    st.stop()

st.title("👥 User Accounts")

if st.button("⬅ Back to Menu"):
    st.switch_page("pages/neo_menu.py")

st.divider()

res = api_client.get("/users/")
if res.get("status_code") != 200:
    st.error(f"Users unavailable: {error_message(res)}")
    st.stop()

users = res.get("data", [])
st.subheader(f"Accounts ({len(users)})")
df_users = pd.DataFrame(users)
if not df_users.empty:
    df_users["creation_date"] = df_users["creation_date"].astype(str).str[:16].str.replace("T", " ")
st.dataframe(df_users, use_container_width=True, hide_index=True)

st.divider()
st.subheader("Manage an account")

selected = st.selectbox(
    "Account",
    users,
    format_func=lambda u: f"{u['username']} ({u['role']}) - {u['email']}",
)

if selected:
    user_id = selected["user_id"]
    col_promote, col_delete = st.columns(2)

    with col_promote:
        if selected["role"] == "admin":
            st.info("This account is already an administrator.")
        elif st.button("⬆️ Make administrator", use_container_width=True):
            logger.info(f"Promote user {user_id}")
            promote_res = api_client.put(f"/users/{user_id}/admin")
            if promote_res.get("status_code") == 200:
                st.toast(f"{selected['username']} is now an administrator ✅")
                st.rerun()
            else:
                st.error(error_message(promote_res))

    with col_delete:
        if user_id == current_user.get("user_id"):
            st.info("You cannot delete your own account.")
        else:
            confirm = st.checkbox(
                f"I confirm the deletion of {selected['username']} "
                "(with their favourites and alerts)"
            )
            if st.button("🗑️ Delete account", disabled=not confirm, use_container_width=True):
                logger.info(f"Delete user {user_id}")
                delete_res = api_client.delete(f"/users/{user_id}")
                if delete_res.get("status_code") == 200:
                    st.toast(f"{selected['username']} deleted")
                    st.rerun()
                else:
                    st.error(error_message(delete_res))

    st.markdown(f"#### 🕒 Connection history of {selected['username']}")
    history_res = api_client.get(f"/users/{user_id}/connections")
    if history_res.get("status_code") != 200:
        st.error(error_message(history_res))
    elif not history_res.get("data"):
        st.info("This user has never logged in.")
    else:
        connections = pd.DataFrame(history_res["data"])
        connections["date"] = connections["date"].astype(str).str[:19].str.replace("T", " ")
        st.caption(f"{len(connections)} connection(s), latest first")
        st.dataframe(connections[["date"]], use_container_width=True, hide_index=True)
