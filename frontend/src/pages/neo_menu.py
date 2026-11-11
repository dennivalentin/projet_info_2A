"""Streamlit main menu for NEO-Watch.

Provides navigation to core features: Dashboard, NEO Search & Exploration,
Object Creation, and Statistics.
"""

from datetime import date

import streamlit as st

from utils.api_client import api_client
from utils.auth_guard import check_authentification
from utils.log_init import get_page_logger

st.set_page_config(page_title="NEO-Watch | Menu Principal", page_icon="🔭", layout="wide")

logger = get_page_logger("neo_menu")
check_authentification()

user = st.session_state.get("user") or {}
username = user.get("username", "Observateur")

st.title("🔭 NEO-Watch — Espace Principal")
st.markdown(f"Bienvenue, **{username}** ! Choisissez une fonctionnalité ci-dessous :")

col1, col2 = st.columns(2)

with col1:
    with st.container(border=True):
        st.subheader("☄️ Tableau de bord (F2)")
        st.write(
            "Consultez vos statistiques personnalisées, les prochains passages rapprochés et vos objets favoris."
        )
        if st.button("Accéder au Tableau de bord", type="primary", use_container_width=True):
            st.switch_page("pages/dashboard.py")

    with st.container(border=True):
        st.subheader("➕ Déclarer un NEO (F4)")
        st.write(
            "Enregistrez une observation personnelle d'un astéroïde avec l'étiquette protégée 'USER'."
        )
        if st.button("Créer un nouvel objet", use_container_width=True):
            st.switch_page("pages/create_neo.py")

with col2:
    with st.container(border=True):
        st.subheader("🔍 Recherche & Exploration (F3)")
        st.write(
            "Recherchez des astéroïdes selon des critères multiples, inspectez leurs passages en km/UA et exportez en CSV."
        )
        if st.button("Explorer le catalogue NEO", type="primary", use_container_width=True):
            st.switch_page("pages/search_neo.py")

    with st.container(border=True):
        st.subheader("📊 Statistiques Générales (FO3)")
        st.write(
            "Analysez la distribution des diamètres, la proportion d'objets potentiellement dangereux et les tendances globales."
        )
        if st.button("Voir les statistiques", use_container_width=True):
            st.switch_page("pages/statistics.py")

st.divider()

if st.button("🚪 Déconnexion", type="secondary"):
    logger.info("Log out")
    st.session_state.clear()
    st.switch_page("pages/home.py")


today_str = str(date.today())

if st.session_state.get("daily_update_done") != today_str:
    # Mark it first: the import must be launched only once per session and per day
    st.session_state["daily_update_done"] = today_str
    last_res = api_client.get("/import/last")
    if last_res.get("status_code") == 200:
        last_date = last_res.get("data", {}).get("last_end_date")
        if last_date is None or last_date < today_str:
            # The backend runs the NASA import in the background and answers at once
            sync_res = api_client.post("/import/update")
            if sync_res.get("status_code") == 200:
                st.toast("Mise à jour des données NASA lancée en arrière-plan")

status_res = api_client.get("/import/status")
if status_res.get("status_code") == 200 and status_res.get("data", {}).get("running"):
    st.info(
        "⏳ Import des données NASA en cours : les NEO apparaissent au fur et à mesure "
        "dans la recherche, le tableau de bord et les statistiques."
    )


if user.get("role") == "admin":
    st.markdown("---")
    st.subheader("🛠️ Manage data")

    col_reset, col_sync = st.columns(2)

    with col_reset:
        if st.button("🗑️ Reset database", type="secondary", use_container_width=True):
            logger.info("Database reset requested by admin")
            with st.spinner("Reset in progress..."):
                response = api_client.post("/reset_database")

            if response.get("status_code") == 200:
                logger.info("Database successfully reset")
                st.session_state.pop("daily_update_done", None)
                st.toast("Database succesfully reset ✅")
                st.rerun()
            else:
                logger.error("Error during database reset")
                err_msg = response.get("data", {}).get("detail", "Fail during the reset")
                st.error(f"Erreur : {err_msg}")

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
                err_msg = response.get("data", {}).get("detail", "Fail during import")
                st.error(f"Erreur : {err_msg}")
