import secrets

from business_object.neo import Neo
from dao.neo_dao import NeoDao
from utils.log_utils import log
from utils.security import hash_password
from datetime import datetime

class NeoService:
    """Service that handles business logic related to neos (creation, search, etc.)."""

    @log
    def create(self,
        name: str,
        absolute_magnitude: float,
        diameter_min: float,
        diameter_max: float,
        hazardous: bool,
        date_update : datetime) -> Neo:
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

        if NeoDao().find({"absolute_magnitude":absolute_magnitude, "diameter_min":diameter_min, "diameter_max":diameter_max, "hazardous":hazardous, "date_update": date_update}):
            return 


        new_neo = Neo(
            nasa_id = None,
            name = name,
            absolute_magnitude = absolute_magnitude,
            diameter_min = diameter_min,
            diameter_max = diameter_max,
            hazardous = hazardous,
            url_nasa = None,
            origin = "USER",
            date_update = date_update
        )
        return new_neo if NeoDao().create(new_neo) else None


    def search_neo(self,  nasa_id: str | None,
                name: str | None,
                absolute_magnitude: float | None,
                diameter_min: float | None,
                diameter_max: float | None,
                hazardous: bool | None,
                url_nasa: str | None,
                origin: str | None,
                date_update: datetime  | None,
                neo_id: int | None):
        """ Search neos corresping to specific criterias.
        Args:
                neo_id (int | None): The internal unique identifier for the NEO, by default None.
                nasa_id (str): The official identifier provided by NASA.
                name (str): The name of the Near-Earth Object.
                absolute_magnitude (float): The absolute magnitude of the NEO.
                diameter_min (float): The estimated minimum diameter in kilometers.
                diameter_max (float): The estimated maximum diameter in kilometers.
                hazardous (bool): Indicates if the NEO is considered potentially hazardous.
                url_nasa (str): The URL to the NASA web page for this object.
                origin (str): either NASA for a NEO comming from the API or USER for a NEO created by a user.
                date_update (datetime): The date this record was last updated.
        Return:
                List of Neos
        """


