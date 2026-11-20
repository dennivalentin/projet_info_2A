"""Streamlit page for the favourite NEOs: add, list, approaches, graph and delete."""

import base64

import pandas as pd
import streamlit as st

from utils.api_client import api_client, error_message
from utils.auth_guard import check_authentification
from utils.log_init import get_page_logger

st.set_page_config(page_title="NEO-Watch | Favourites", page_icon="⭐", layout="wide")

st.title("Favourite NEOs")
logger = get_page_logger("favourites")

check_authentification()

user = st.session_state.get("user") or {}
user_id = user.get("user_id")


st.subheader("Add a Favourite NEO")
with st.form("add_favourite_form", clear_on_submit=True):
    col_id, col_btn = st.columns([3, 1])
    neo_id_input = col_id.number_input(
        "NEO ID", min_value=1, step=1, help="Enter the ID of the asteroid to save"
    )
    submit_add = col_btn.form_submit_button("Add to Favourites")

    if submit_add:
        logger.info(f"Adding NEO {neo_id_input} to favourites for user {user_id}")
        req = {"user_id": user_id, "neo_id": neo_id_input}
        add_response = api_client.post("/favourites/", json=req)

        if add_response["status_code"] in (200, 201):
            st.toast(f"NEO #{neo_id_input} successfully added!")
            st.rerun()
        else:
            st.error(f"Failed to add favourite: {error_message(add_response)}")

st.divider()


response = api_client.get(f"/favourites/user/{user_id}")

if response["status_code"] != 200:
    st.error("Error loading favourites")
    st.stop()

favourites = response["data"]

if not favourites:
    st.info("You do not have any favourite NEOs yet.")
else:
    st.subheader("List of your favourite(s)")
    table_data = []
    for neo in favourites:
        table_data.append(
            {
                "ID": neo["neo_id"],
                "Name": neo["name"],
                "Diameter Min (km)": neo.get("diameter_min"),
                "Diameter Max (km)": neo.get("diameter_max"),
                "Hazardous": "Yes" if neo.get("hazardous") else "No",
            }
        )
    st.dataframe(table_data, use_container_width=True)

    st.divider()

    st.subheader("Approaches of your favourite")
    if st.checkbox("Display the approaches", value=False):
        with st.spinner("Loading..."):
            appr_res = api_client.get(f"/favourites/user/{user_id}/approaches")

        if appr_res["status_code"] == 200:
            approaches_dict = appr_res["data"]

            if not approaches_dict:
                st.write("No approaches available")
            else:
                for neo in favourites:
                    # JSON keys are strings: the approaches of NEO 12 are under "12"
                    neo_id_str = str(neo["neo_id"])
                    neo_name = neo["name"]

                    approaches = approaches_dict.get(neo_id_str, [])
                    with st.expander(
                        f"Approaches for {neo_name} ({len(approaches)} approaches recorded)"
                    ):
                        if approaches:
                            df_approaches = pd.DataFrame(approaches)
                            st.dataframe(df_approaches, use_container_width=True)
                            st.download_button(
                                "📥 Export the distance history (CSV)",
                                data=df_approaches.to_csv(index=False).encode("utf-8"),
                                file_name=f"approaches_neo_{neo_id_str}.csv",
                                mime="text/csv",
                                key=f"csv_{neo_id_str}",
                            )
                        else:
                            st.write("No approaches available")
        else:
            st.error("Error during the loading of approaches")

    st.divider()

    st.subheader("Trajectory Visualizer")
    selected_fav = st.selectbox(
        "Choose a favourite NEO to plot",
        favourites,
        format_func=lambda item: f"{item['name']} (ID: {item['neo_id']})",
    )

    if st.button("Display Neo infos"):
        target_id = selected_fav["neo_id"]
        logger.info(f"Displaying graph for neo_id={target_id}")
        with st.spinner("Generating plot..."):
            graph_response = api_client.get(f"/favourites/user/{user_id}/neo/{target_id}/graph")

        if graph_response["status_code"] == 200:
            img_b64 = graph_response["data"]["image"]
            st.image(img_b64, caption=f"Graph for {selected_fav['name']}")
            # The API sends a data URL "data:image/png;base64,...": decoded for the export
            st.download_button(
                "📥 Download the graph (PNG)",
                data=base64.b64decode(img_b64.split(",", 1)[1]),
                file_name=f"distance_neo_{target_id}.png",
                mime="image/png",
            )
        else:
            st.error(f"Unable to generate the graph: {error_message(graph_response)}")

    st.divider()

    st.subheader("Manage Favourites")
    for fav in favourites:
        f_neo_id = fav["neo_id"]
        f_name = fav["name"]
        col_name, col_del = st.columns([4, 1])
        col_name.write(f"**{f_name}** (ID: `{f_neo_id}`)")

        if col_del.button("Delete", key=f"del_fav_{f_neo_id}"):
            logger.info(f"Deleting favourite neo_id={f_neo_id}")
            del_response = api_client.delete(f"/favourites/{user_id}/{f_neo_id}")
            if del_response["status_code"] in (200, 204):
                st.success("Favourite deleted")
                st.rerun()
            else:
                st.error(error_message(del_response, "Error deleting favourite"))

if st.button("Back to menu", type="primary"):
    st.switch_page("pages/neo_menu.py")
