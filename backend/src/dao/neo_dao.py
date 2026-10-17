from business_object.neo import Neo
from dao.db_connection import DBConnection
from utils.log_utils import get_logger, log
from utils.singleton import Singleton

logger = get_logger(__name__)


class NeoDao(metaclass=Singleton):
    """Class containing methods to access Players in the database."""

    @log
    def create(self, neo) -> bool:
        """Create a player in the database.
        Args:
            Player to create
        Returns:
            True if creation is successful, False otherwise
        """
        res = None

        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "INSERT INTO neo(nasa_id, name, absolute_magnitude, diameter_min, diameter_max, hazardous, url_nasa, origin, date_update) VALUES "
                        "(%(nasa_id)s, %(name)s, %(absolute_magnitude)s, %(diameter_min)s, %(diameter_max)s, %(hazardous)s, %(url_nasa)s, %(origin)s, %(date_update)s) "
                        "ON CONFLICT (nasa_id) DO UPDATE SET name = EXCLUDED.name, date_update = EXCLUDED.date_update "
                        "RETURNING neo_id;",
                        {
                            "neo_id": neo._neo_id,
                            "nasa_id": neo._nasa_id,
                            "name": neo._name,
                            "absolute_magnitude": neo._absolute_magnitude,
                            "diameter_min": neo._diameter_min,
                            "diameter_max": neo._diameter_max,
                            "hazardous": neo._hazardous,
                            "url_nasa": neo._url_nasa,
                            "origin": neo._origin,
                            "date_update": neo._date_update,
                        },
                    )
                    res = cursor.fetchone()
        except Exception as e:
            logger.error(e)
            raise

        created = False

        if res:
            neo._neo_id = res["neo_id"] if isinstance(res, dict) else res[0]
            created = True

        return created
    
    @log
    def find_by_id(self, neo_id: int) -> Neo:
        """Find a player by their id.
        Args:
            neo_id (int): The ID of the Neo to find
        Returns:
            Neo matching the given id
        """
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT *                            "
                        "  FROM neo                       "
                        " WHERE neo_id = %(neo_id)s;   ",
                        {"neo_id": neo_id},
                    )
                    res = cursor.fetchone()
        except Exception as e:
            logger.error(e)
            raise

        neo = None
        if res:
            neo = Neo(
                nasa_id= res["nasa_id"],
                name= res["name"],
                absolute_magnitude= res["absolute_magnitude"],
                diameter_min= res["diameter_min"],
                diameter_max= res["diameter_max"],
                hazardous= res["hazardous"],
                url_nasa= res["url_nasa"],
                origin= res["origin"],
                date_update= res["date_update"],
                neo_id= res["neo_id"],
            )

        return neo
