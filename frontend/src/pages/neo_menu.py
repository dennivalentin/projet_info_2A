"""Streamlit main menu for NEO-Watch.

Provides navigation to core features: Dashboard, NEO Search & Exploration,
Object Creation, and Statistics.
"""

import streamlit as st

from utils.auth_guard import check_authentification
from utils.log_init import get_page_logger

st.set_page_config(page_title="NEO-Watch | Menu Principal", page_icon="🔭", layout="wide")

logger = get_page_logger("neo_menu")
check_authentification()

user = st.session_state.get("user") or  {}
username = user.get("username", "Observateur")

st.title("🔭 NEO-Watch — Espace Principal")
st.markdown(f"Bienvenue, **{username}** ! Choisissez une fonctionnalité ci-dessous :")

col1, col2 = st.columns(2)

with col1:
    with st.container(border=True):
        st.subheader("☄️ Tableau de bord (F2)")
        st.write("Consultez vos statistiques personnalisées, les prochains passages rapprochés et vos objets favoris.")
        if st.button("Accéder au Tableau de bord", type="primary", use_container_width=True):
            st.switch_page("pages/dashboard.py")

    with st.container(border=True):
        st.subheader("➕ Déclarer un NEO (F4)")
        st.write("Enregistrez une observation personnelle d'un astéroïde avec l'étiquette protégée 'USER'.")
        if st.button("Créer un nouvel objet", use_container_width=True):
            st.switch_page("pages/create_neo.py")

with col2:
    with st.container(border=True):
        st.subheader("🔍 Recherche & Exploration (F3)")
        st.write("Recherchez des astéroïdes selon des critères multiples, inspectez leurs passages en km/UA et exportez en CSV.")
        if st.button("Explorer le catalogue NEO", type="primary", use_container_width=True):
            st.switch_page("pages/search_neo.py")

    with st.container(border=True):
        st.subheader("📊 Statistiques Générales (FO3)")
        st.write("Analysez la distribution des diamètres, la proportion d'objets potentiellement dangereux et les tendances globales.")
        if st.button("Voir les statistiques", use_container_width=True):
            st.switch_page("pages/statistics.py")

st.divider()

if st.button("🚪 Déconnexion", type="secondary"):
    logger.info("Log out")
    st.session_state.clear()
    st.switch_page("pages/home.py")


if user.get("role") == "admin":
    if st.button("🔄 Réinitialiser la base de données", type="secondary"):
        logger.info("Reset the database")
        response = api_client.get("/reset_database")

    if response and response.get("status_code") == 200:
        logger.info("Database successfully reset")
        st.toast("Base de données réinitialisée avec succès ✅")
    else:
        logger.info("Error during database reset")
        st.toast("Erreur lors de la réinitialisation ❌")