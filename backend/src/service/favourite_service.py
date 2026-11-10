
import io
from utils.log_utils import log

from dao.approach_dao import ApproachDao
from dao.neo_dao import NeoDao
from dao.favourite_dao import FavouriteDao
from business_object.neo import Neo
from business_object.approach import Approach

import matplotlib.pyplot as plt 


class FavouriteService:
    @log
    def add_favourite(self, neo_id: int, user_id: int) -> bool:
        """Add a NEO to the user's favorites list."""
        if FavouriteDao().create(neo_id, user_id):
            print("Succesfully created")
            return True
        else:
            print("Error happened")
            return False

    @log
    def remove_favourite(self, neo_id: int, user_id: int) -> bool:
        """Remove a NEO from the user's favorites list."""
        if FavouriteDao().delete(neo_id, user_id):
            print("Succesfully deleted")
            return True
        else:
            print("Nothing deleted")
            return False

    @log
    def list_all_favourite_by_user(self, user_id: int) -> list[Neo]:
        """
        list of all the favourite by user

        Parameters
        ----------
            user_id : id of the user
        Return
        ------
            list(Neo) : list of all the favourite of the user
        """
        list_fav = FavouriteDao().find_favourite_by_user(user_id)
        list_neo = []

        for neo_id in list_fav:
            neo_fav = NeoDao().find_by_id(neo_id)
            list_neo.append(neo_fav)

        return list_neo

    @log
    def approches_favourite(self, user_id: int) -> dict[int, list[Approach]]:
        """
        list of all the approches by the favourites Neo of a user

        Parameters
        ----------
            user_id : id of the user
        Return
        ------
            dict[int, list[Approach]] : dictionnary of list of all the favourite approaches
        """
        dict_approaches = {}

        list_fav = FavouriteDao().find_favourite_by_user(user_id)
        for item in list_fav:
            dict_approaches[item] = ApproachDao().find_by_neo_id(item)

        return dict_approaches

    @log
    def graph_favourite(self, user_id, neo_id) -> io.BytesIO:
        list_approaches = self.approches_favourite(user_id)[neo_id]

        if not list_approaches:
            raise ValueError(f"No data available for Neo : {neo_id}.")

        dates = []
        distances = []

        for item in list_approaches:
            dates.append(item._approach_date)
            distances.append(item._distance)

        fig, ax = plt.subplots(figsize=(10, 5))

        ax.plot(
            dates,
            distances,
            marker="o",
            linestyle="-",
            color="#1f77b4",
            markersize=5,
        )
        ax.set_title(f"Distance to Earth over time - NEO n°{neo_id}", pad=12)
        ax.set_xlabel("Date")
        ax.set_ylabel("Distance (km)")
        ax.grid(True, linestyle=":", alpha=0.6)

        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format="png", dpi=200)
        plt.close(fig)
        img_buffer.seek(0)

        return img_buffer
