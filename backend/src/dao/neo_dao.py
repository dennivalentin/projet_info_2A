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
                        "INSERT INTO player(neo_id, nasa_id, name, absolute_magnitude, diameter_min, diameter_max, hazardious, url_nasa, custom, date_update) VALUES "
                        "(%(neo_id)s, %(nasa_id)s, %(name)s, %(absolute_magnitude)s, %(diameter_min)s, %(diameter_max)s, %(hazardious)s, %(url_nasa)s, %(custom)s, %(date_update)s) "
                        "RETURNING id_player;",
                        {
                            "neo_id": neo._neo_id,
                            "nasa_id": neo._nasa_id,
                            "name": neo._name,
                            "absolute_magnitude": neo.absolute_magnitude,
                            "diameter_min": neo._diameter_min,
                            "diameter_max": neo.__diameter_max,
                            "hazardious": neo._hazardious,
                            "url_nasa": neo._url_nasa,
                            "custom": neo._custom,
                            "date_update": neo._date_update
                        },
                    )
                    res = cursor.fetchone()
        except Exception as e:
            logger.error(e)
            raise

        created = False
        if res:
            neo._neo_id = res["neo_id"]
            created = True

        return created