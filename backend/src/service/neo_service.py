import secrets

from business_object.neo import Neo
from dao.neo_dao import NeoDao
from utils.log_utils import log
from utils.security import hash_password


class NeoService:
    """Service that handles business logic related to neos (creation, search, etc.)."""

    @log
    def create(self,
        name: str,
        absolute_magnitude: float,
        diameter_min: float,
        diameter_max: float,
        hazardous: bool) -> Neo:
        """Creates a new neo in the system.
        Args:
            neo_id (int | None): The internal unique identifier for the NEO, by default None.
            name (str): The name of the Near-Earth Object.
            absolute_magnitude (float): The absolute magnitude of the NEO.
            diameter_min (float): The estimated minimum diameter in kilometers.
            diameter_max (float): The estimated maximum diameter in kilometers.
            hazardous (bool): Indicates if the NEO is considered potentially hazardous.
        Returns:
            Neo object created or None if creation failed.
        """
        new_neo = Neo(
            nasa_id = ""
            name = name
            absolute_magnitude = absolute_magnitude
            diameter_min = diameter_min
            diameter_max = diameter_max
            hazardous = hazardous
            url_nasa = ""
            origin = "USER"
            date_update = date_update
        )
        return new_neo if PlayerDao().create(new_neo) else None