"""Streamlit home page for NEO-Watch.

Provides options to log in, register a new account, or reset the database.
"""

import streamlit as st
from streamlit import config

from utils.api_client import api_client
from utils.log_init import get_page_logger

if "user" in st.session_state:
    st.switch_page("pages/neo_menu.py")

st.set_page_config(page_title="NEO-Watch", page_icon="🔭", layout="centered")

st.markdown(
    f"""
    <div style="text-align:center; padding-bottom: 1rem;">
        <h1 style="color:{config.get_option("theme.primaryColor")}; margin-bottom: 0.2rem;">🔭 NEO-Watch</h1>
        <p style="font-size: 1.05rem; opacity: 0.85;">Plateforme d'exploration et de surveillance des astéroïdes</p>
    </div>
    """,
    unsafe_allow_html=True,
)
logger = get_page_logger("home")

tab_login, tab_register = st.tabs(["🔐 Connexion", "📝 Créer un compte"])

with tab_login:
    username = st.text_input("Nom d'utilisateur", placeholder="admin", key="login_user")
    password = st.text_input("Mot de passe", type="password", placeholder="admin", key="login_pass")

    if st.button("Se connecter", type="primary", use_container_width=True):
        logger.info(f"Attempting login for user: {username}")
        try:
            response = api_client.post("/login/", json={"username": username, "password": password})

            if response:
                status_code = response.get("status_code")
                data = response.get("data")

                if status_code == 200:
                    logger.info(f"User {username} successfully logged in.")
                    st.session_state["user"] = data
                    st.session_state["access_token"] = data["access_token"]
                    if "refresh_token" in data:
                        st.session_state["refresh_token"] = data["refresh_token"]
                    st.switch_page("pages/neo_menu.py")
                elif status_code == 401:
                    logger.warning(f"Login failed: 401 for user {username}.")
                    st.error("Identifiants incorrects.")
                else:
                    logger.error(f"Login failed: Status {status_code}, Data: {data}")
                    st.error("Erreur serveur, voir les logs.")
            else:
                st.error("Aucune réponse du serveur.")
        except Exception as e:
            logger.exception(f"Critical error during API call: {str(e)}")
            st.error(f"Erreur de connexion : {str(e)}")

with tab_register:
    new_username = st.text_input("Nom d'utilisateur", placeholder="astronome2026", key="reg_user")
    new_email = st.text_input("Adresse email", placeholder="astronome@ensai.fr", key="reg_email")
    new_password = st.text_input("Mot de passe", type="password", key="reg_pass")

    if st.button("Créer mon compte", use_container_width=True):
        if not new_username or not new_email or not new_password:
            st.error("Veuillez renseigner tous les champs.")
        else:
            try:
                reg_res = api_client.post(
                    "/login/register",
                    json={
                        "username": new_username.strip(),
                        "email": new_email.strip(),
                        "password": new_password,
                    },
                )
                if reg_res and reg_res.get("status_code") == 200:
                    st.success("Compte créé avec succès ! Vous pouvez maintenant vous connecter.")
                else:
                    err = reg_res.get("data") if reg_res else "Erreur"
                    st.error(f"Échec de l'inscription : {err}")
            except Exception as e:
                st.error(f"Erreur : {e}")

st.divider()
