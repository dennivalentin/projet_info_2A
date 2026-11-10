import streamlit as st
from utils.api_client import api_client
from utils.auth_guard import check_authentification
from utils.log_init import get_page_logger

st.title("Favourite NEOs")
logger = get_page_logger("favourites")

check_authentification()

user = st.session_state.get("user")
user_id = user.get("user_id") or user.get("id", 1)


st.subheader("Add a Favourite NEO")
with st.form("add_favourite_form", clear_on_submit=True):
    col_id, col_btn = st.columns([3, 1])
    neo_id_input = col_id.number_input("NEO ID", min_value=1, step=1, help="Enter the ID of the asteroid to save")
    submit_add = col_btn.form_submit_button("Add to Favourites")

    if submit_add:
        logger.info(f"Adding NEO {neo_id_input} to favourites for user {user_id}")
        req = {"user_id": user_id, "neo_id": neo_id_input}
        add_response = api_client.post("/favourites/", json=req)

        if add_response["status_code"] in (200, 201):
            st.success(f"NEO #{neo_id_input} successfully added!")
            st.rerun()
        else:
            err_msg = add_response.get("data", "Error adding favourite")
            st.error(f"Failed to add favourite: {err_msg}")

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
        neo_id = neo.get("id_neo") or neo.get("neo_id") or neo.get("id")
        table_data.append({
            "ID": neo_id,
            "Name": neo.get("name", "Inconnu"),
            "Diametre Min (km)": neo.get("diameter_min", "-"),
            "Diametre Max (km)": neo.get("diameter_max", "-"),
            "Hazardous": "Yes" if neo.get("hazardous") else "No",
        })
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
                    neo_id_str = str(neo.get("id_neo") or neo.get("neo_id") or neo.get("id"))
                    neo_name = neo.get("name", f"NEO #{neo_id_str}")
                    
                    approaches = approaches_dict.get(neo_id_str, [])
                    with st.expander(f"Approaches for {neo_name} ({len(approaches)} approaches recorded)"):
                        if approaches:
                            st.dataframe(approaches, use_container_width=True)
                        else:
                            st.write("No approaches availabe")
        else:
            st.error("Error during the loading of approaches")

    st.divider()


    st.subheader("Trajectory Visualizer")
    selected_fav = st.selectbox(
        "Choose a favourite NEO to plot",
        favourites,
        format_func=lambda item: f"{item.get('name', 'NEO')} (ID: {item.get('neo_id')})",
    )

    if st.button("Display Neo infos"):
        target_id = selected_fav.get("neo_id")
        logger.info(f"Displaying graph for neo_id={selected_fav['neo_id']}")
        with st.spinner("Generating plot..."):
            graph_response = api_client.get(f"/favourites/user/{user_id}/neo/{target_id}/graph")

        if graph_response["status_code"] == 200:
            img_b64 = graph_response["data"]["image"]
            st.image(img_b64, caption=f"Graph for {selected_fav.get('name', 'NEO')}")
        else:
            st.error("Unable to generate trajectory graph for this NEO.")

    st.divider()

    st.subheader("Manage Favourites")
    for fav in favourites:
        f_neo_id = fav.get("neo_id")
        f_name = fav.get("name", "Unknown NEO")
        col_name, col_del = st.columns([4, 1])
        col_name.write(f"**{f_name}** (ID: `{f_neo_id}`)")

        if col_del.button("Delete", key=f"del_fav_{f_neo_id}"):
            logger.info(f"Deleting favourite neo_id={f_neo_id}")
            del_response = api_client.delete(f"/favourites/{user_id}/{f_neo_id}")
            if del_response["status_code"] in (200, 204):
                st.success("Favourite deleted")
                st.rerun()
            else:
                st.error(del_response.get("data", "Error deleting favourite"))

if st.button("Back to menu", type="primary"):
    st.switch_page("pages/neo_menu.py")