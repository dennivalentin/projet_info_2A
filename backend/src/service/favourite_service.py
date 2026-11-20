import base64
import io

import matplotlib.pyplot as plt

from business_object.approach import Approach
from business_object.neo import Neo
from dao.approach_dao import ApproachDao
from dao.favourite_dao import FavouriteDao
from dao.neo_dao import NeoDao
from utils.log_utils import get_logger, log

logger = get_logger(__name__)


class FavouriteService:
    """Business logic of the favourite NEOs of a user (list, approaches, graph)."""

    @log
    def add_favourite(self, neo_id: int, user_id: int) -> bool:
        """Adds a NEO to the user's favourites.

        Returns:
            bool: True if the favourite was added, False if it already was a favourite.

        Raises:
            ValueError: If the NEO does not exist.
        """
        if NeoDao().find_by_id(neo_id) is None:
            raise ValueError(f"NEO {neo_id} not found")
        added = FavouriteDao().create(neo_id, user_id)
        if not added:
            logger.warning(f"NEO {neo_id} not added to the favourites of user {user_id}")
        return added

    @log
    def remove_favourite(self, neo_id: int, user_id: int) -> bool:
        """Removes a NEO from the user's favourites.

        Returns:
            bool: True if a favourite was removed, False if there was none.
        """
        return FavouriteDao().delete(neo_id, user_id)

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
    def approaches_favourite(self, user_id: int) -> dict[int, list[Approach]]:
        """
        list of all the approaches of the favourites Neo of a user

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
    def graph_favourite(self, user_id: int, neo_id: int) -> str:
        """Draws the distance to Earth of a favourite NEO over time.

        Args:
            user_id: Owner of the favourites.
            neo_id: The favourite NEO to draw.

        Returns:
            str: The PNG image as a data URL ("data:image/png;base64,...").

        Raises:
            KeyError: If the NEO is not one of the user's favourites.
            ValueError: If the NEO has no recorded approach.
        """
        list_approaches = self.approaches_favourite(user_id)[neo_id]

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

        buf = io.BytesIO()
        plt.savefig(buf, format="png", bbox_inches="tight")
        plt.close()
        buf.seek(0)

        encoded = base64.b64encode(buf.getvalue()).decode("ascii")
        return f"data:image/png;base64,{encoded}"
