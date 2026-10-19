from business_object.neo import Neo
from dao.db_connection import DBConnection
from utils.log_utils import get_logger, log
from utils.singleton import Singleton

logger = get_logger(__name__)


class NeoDao(metaclass=Singleton):
    """Class containing methods to access NEOS in the database."""

    @log
    def create(self, neo) -> bool:
        """Create a neo in the database.
        Args:
            Neo to create
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
    def find(self, search_criteria : dict) -> list[Neo] | None:
        """Seek a neo in the database.
        Args:
            search criterias
        Returns:
            NEOS corresponding to such criterias, None otherwise
        """
        res = None
        query = "SELECT * FROM neo WHERE 1=1"
        params = {}
        for e in search_criteria:
	        if search_criteria[e] is not None:
		        query += f" AND neo.{e} = %({e})s"
		        params[e] = search_criteria[e]
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        query,
                        params,
                    )
                    res = cursor.fetchall()
        except Exception as e:
            logger.error(e)
            raise
        NEOS = []

        if res:
            for e in res:
                neo = Neo(neo_id = e["neo_id"],
                        nasa_id=e["nasa_id"],
                        name = e["name"],
                        absolute_magnitude = e["absolute_magnitude"],
                        diameter_min = e["diameter_min"],
                        diameter_max = e["diameter_max"],
                        hazardous = e["hazardous"],
                        url_nasa = e["url_nasa"],
                        origin = e["origin"],
                        date_update = e["date_update"])
                NEOS.append(neo)
        return NEOS