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
def find(self, search_criteria: dict) -> list[Neo]:
    """Search for NEOs matching the provided criteria.

    Args:
        search_criteria: Dictionary of criteria and values.

    Returns:
        A list of matching Neo objects, or an empty list.

    Raises:
        ValueError: If a criterion is unknown.
    """

    criteria_map = {
        "neo_id": (
            "n.neo_id = %(neo_id)s",
            lambda value: value,
        ),
        "nasa_id": (
            "n.nasa_id = %(nasa_id)s",
            lambda value: value,
        ),
        "name": (
            "n.name ILIKE %(name)s",
            lambda value: f"%{value}%",
        ),
        "hazardous": (
            "n.hazardous = %(hazardous)s",
            lambda value: value,
        ),
        "diameter_min": (
            "n.diameter_min >= %(diameter_min)s",
            lambda value: value,
        ),
        "diameter_max": (
            "n.diameter_max <= %(diameter_max)s",
            lambda value: value,
        ),
        "date_update": (
            "n.date_update = %(date_update)s",
            lambda value: value,
        ),
        "origin": (
            "n.origin = %(origin)s",
            lambda value: f"%{value}%",
        ),
        "absolute_magnitude": (
            "n.absolute_magnitude = %(absolute_magnitude)s",
            lambda value: value,
        ),
        "approach_day": (
            "a.approach_day = %(approach_day)s",
            lambda value: value,
        ),
    }

    query = "SELECT DISTINCT n.* FROM neo n WHERE 1=1"
    params = {}
    needs_approach = False

    for criterion, value in search_criteria.items():
        if criterion not in criteria_map:
            raise ValueError(f"Unknown search criterion: {criterion}")

        if value is None:
            continue

        condition, transform_value = criteria_map[criterion]
        query += f" AND {condition}"
        params[criterion] = transform_value(value)

        if criterion == "approach_day":
            needs_approach = True

    if needs_approach:
        query = query.replace(
            "FROM neo n WHERE",
            "FROM neo n " "JOIN approach a ON n.neo_id = a.neo_id WHERE",
        )

    try:
        with DBConnection().connection as connection:
            with connection.cursor() as cursor:
                print("SQL:", query)
                print("params:", params)

                cursor.execute(query, params)
                rows = cursor.fetchall()

    except Exception as error:
        logger.error(error)
        raise

    neos = []

    for row in rows:
        neo = Neo(
            neo_id=row["neo_id"],
            nasa_id=row["nasa_id"],
            name=row["name"],
            absolute_magnitude=row["absolute_magnitude"],
            diameter_min=row["diameter_min"],
            diameter_max=row["diameter_max"],
            hazardous=row["hazardous"],
            url_nasa=row["url_nasa"],
            origin=row["origin"],
            date_update=row["date_update"],
        )
        neos.append(neo)

    return neos
