from business_object.neo import Neo
from dao.db_connection import DBConnection
from utils.log_utils import get_logger, log
from utils.singleton import Singleton

logger = get_logger(__name__)


class NeoDao(metaclass=Singleton):
    """Class containing methods to access NEOs in the database."""

    @log
    def create(self, neo: Neo) -> bool:
        """Create or update a NEO in the database.

        Args:
            neo: Neo instance to persist.

        Returns:
            True if creation was successful, False otherwise.
        """
        res = None
        params = {
            "nasa_id": neo.nasa_id,
            "name": neo.name,
            "absolute_magnitude": neo.absolute_magnitude,
            "diameter_min": neo.diameter_min,
            "diameter_max": neo.diameter_max,
            "hazardous": neo.hazardous,
            "url_nasa": neo.url_nasa,
            "origin": neo.origin,
            "date_update": neo.date_update,
        }

        if neo.nasa_id:
            query = """
                INSERT INTO neo (
                    nasa_id, name, absolute_magnitude, diameter_min, diameter_max,
                    hazardous, url_nasa, origin, date_update
                ) VALUES (
                    %(nasa_id)s, %(name)s, %(absolute_magnitude)s, %(diameter_min)s, %(diameter_max)s,
                    %(hazardous)s, %(url_nasa)s, %(origin)s, %(date_update)s
                )
                ON CONFLICT (nasa_id) DO UPDATE SET
                    name = EXCLUDED.name,
                    absolute_magnitude = EXCLUDED.absolute_magnitude,
                    diameter_min = EXCLUDED.diameter_min,
                    diameter_max = EXCLUDED.diameter_max,
                    hazardous = EXCLUDED.hazardous,
                    url_nasa = EXCLUDED.url_nasa,
                    date_update = EXCLUDED.date_update
                RETURNING neo_id;
            """
        else:
            query = """
                INSERT INTO neo (
                    nasa_id, name, absolute_magnitude, diameter_min, diameter_max,
                    hazardous, url_nasa, origin, date_update
                ) VALUES (
                    %(nasa_id)s, %(name)s, %(absolute_magnitude)s, %(diameter_min)s, %(diameter_max)s,
                    %(hazardous)s, %(url_nasa)s, %(origin)s, %(date_update)s
                )
                RETURNING neo_id;
            """

        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(query, params)
                    res = cursor.fetchone()
        except Exception as e:
            logger.error(f"Error in NeoDao.create: {e}")
            raise

        if res:
            neo.neo_id = res["neo_id"] if isinstance(res, dict) else res[0]
            return True

        return False

    @log
    def find_by_id(self, neo_id: int) -> Neo | None:
        """Find a single NEO by its internal ID.

        Args:
            neo_id: The ID of the NEO.

        Returns:
            The Neo object if found, None otherwise.
        """
        query = "SELECT * FROM neo WHERE neo_id = %(neo_id)s;"
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(query, {"neo_id": neo_id})
                    row = cursor.fetchone()
                    if not row:
                        return None
                    return self._map_row_to_neo(row)
        except Exception as e:
            logger.error(f"Error in NeoDao.find_by_id: {e}")
            raise

    @log
    def find_all(self, limit: int = 100, offset: int = 0) -> list[Neo]:
        """Fetch all NEOs with pagination.

        Args:
            limit: Maximum records to return.
            offset: Number of records to skip.

        Returns:
            List of Neo objects.
        """
        query = "SELECT * FROM neo ORDER BY neo_id ASC LIMIT %(limit)s OFFSET %(offset)s;"
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(query, {"limit": limit, "offset": offset})
                    rows = cursor.fetchall() or []
                    return [self._map_row_to_neo(r) for r in rows]
        except Exception as e:
            logger.error(f"Error in NeoDao.find_all: {e}")
            raise

    @log
    def find(self, search_criteria: dict) -> list[Neo]:
        """Search for NEOs matching the provided criteria.

        Args:
            search_criteria: Dictionary of criteria and values.

        Returns:
            A list of matching Neo objects, or an empty list.
        """
        criteria_map = {
            "neo_id": ("n.neo_id = %(neo_id)s", lambda v: v),
            "nasa_id": ("n.nasa_id = %(nasa_id)s", lambda v: v),
            "name": ("n.name ILIKE %(name)s", lambda v: f"%{v}%"),
            "hazardous": ("n.hazardous = %(hazardous)s", lambda v: v),
            "diameter_min": ("n.diameter_min >= %(diameter_min)s", lambda v: float(v)),
            "diameter_max": ("n.diameter_max <= %(diameter_max)s", lambda v: float(v)),
            "origin": ("UPPER(n.origin) = UPPER(%(origin)s)", lambda v: v),
            "approach_day": ("a.approach_day = %(approach_day)s", lambda v: v),
            "start_date": ("a.approach_day >= %(start_date)s", lambda v: v),
            "end_date": ("a.approach_day <= %(end_date)s", lambda v: v),
        }

        query = "SELECT DISTINCT n.* FROM neo n WHERE 1=1"
        params = {}
        needs_approach = False

        for criterion, value in search_criteria.items():
            if value is None or criterion in ("sort_by", "order", "limit", "offset"):
                continue

            if criterion not in criteria_map:
                raise ValueError("Unknown search criterion")

            condition, transform_value = criteria_map[criterion]
            query += f" AND {condition}"
            params[criterion] = transform_value(value)

            if criterion in ("approach_day", "start_date", "end_date"):
                needs_approach = True

        if needs_approach:
            query = query.replace(
                "FROM neo n WHERE",
                "FROM neo n JOIN approach a ON n.neo_id = a.neo_id WHERE",
            )

        # Ordering
        sort_by = search_criteria.get("sort_by")
        order = search_criteria.get("order", "ASC").upper()
        if order not in ("ASC", "DESC"):
            order = "ASC"

        valid_sort_columns = {
            "neo_id": "n.neo_id",
            "name": "n.name",
            "diameter_min": "n.diameter_min",
            "diameter_max": "n.diameter_max",
            "hazardous": "n.hazardous",
            "date_update": "n.date_update",
        }
        order_col = valid_sort_columns.get(sort_by, "n.neo_id")
        query += f" ORDER BY {order_col} {order}"

        # Pagination
        limit = search_criteria.get("limit", 100)
        offset = search_criteria.get("offset", 0)
        query += " LIMIT %(limit)s OFFSET %(offset)s;"
        params["limit"] = limit
        params["offset"] = offset

        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(query, params)
                    rows = cursor.fetchall() or []
                    return [self._map_row_to_neo(row) for row in rows]
        except Exception as error:
            logger.error(f"Error in NeoDao.find: {error}")
            raise

    @log
    def delete(self, neo_id: int) -> bool:
        """Delete a NEO by ID.

        Args:
            neo_id: Internal ID of the NEO.

        Returns:
            True if deleted, False otherwise.
        """
        query = "DELETE FROM neo WHERE neo_id = %(neo_id)s;"
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(query, {"neo_id": neo_id})
                    return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error in NeoDao.delete: {e}")
            raise

    def _map_row_to_neo(self, row: dict) -> Neo:
        return Neo(
            neo_id=row["neo_id"],
            nasa_id=row.get("nasa_id"),
            name=row["name"],
            absolute_magnitude=row.get("absolute_magnitude"),
            diameter_min=row.get("diameter_min"),
            diameter_max=row.get("diameter_max"),
            hazardous=row.get("hazardous", False),
            url_nasa=row.get("url_nasa"),
            origin=row.get("origin", "USER"),
            date_update=row.get("date_update"),
        )
