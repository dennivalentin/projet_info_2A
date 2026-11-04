"""F2 - Database queries for the user dashboard."""

from datetime import date

from dao.db_connection import DBConnection
from utils.singleton import Singleton


class DashboardDao(metaclass=Singleton):
    """Reads the approach, neo and favourite tables to build the dashboard."""

    def _run(self, query: str, params: dict) -> list[dict]:
        """Runs a SELECT query and returns the rows as a list of dicts."""
        with DBConnection().connection as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, params)
                return [dict(row) for row in cursor.fetchall()]

    def find_upcoming_approaches(self, start: date, end: date) -> list[dict]:
        """Query 1: approaches between two dates, soonest first."""
        query = """
            SELECT n.name, a.approach_date, a.distance
            FROM approach a
            JOIN neo n ON n.neo_id = a.neo_id
            WHERE a.approach_day BETWEEN %(start)s AND %(end)s
            ORDER BY a.approach_date;
        """
        return self._run(query, {"start": start, "end": end})

    def count_upcoming(self, start: date, end: date) -> dict:
        """Query 2: number of NEOs and of hazardous NEOs between two dates."""
        query = """
            SELECT
                COUNT(DISTINCT a.neo_id) AS nb_neos,
                COUNT(DISTINCT a.neo_id) FILTER (WHERE n.hazardous) AS nb_hazardous
            FROM approach a
            JOIN neo n ON n.neo_id = a.neo_id
            WHERE a.approach_day BETWEEN %(start)s AND %(end)s;
        """
        return self._run(query, {"start": start, "end": end})[0]

    def find_closest_approach(self, start: date, end: date) -> dict | None:
        """Query 3: the closest approach between two dates."""
        query = """
            SELECT n.name, a.approach_date, a.distance, n.hazardous
            FROM approach a
            JOIN neo n ON n.neo_id = a.neo_id
            WHERE a.approach_day BETWEEN %(start)s AND %(end)s
            ORDER BY a.distance ASC
            LIMIT 1;
        """
        rows = self._run(query, {"start": start, "end": end})
        return rows[0] if rows else None

    def find_favourites(self, user_id: int) -> list[dict]:
        """Query 4: the user's favourites with their next approach."""
        query = """
            SELECT n.name, MIN(a.approach_date) AS next_approach
            FROM favourite f
            JOIN neo n ON n.neo_id = f.neo_id
            LEFT JOIN approach a
                ON a.neo_id = n.neo_id AND a.approach_day >= CURRENT_DATE
            WHERE f.user_id = %(user_id)s
            GROUP BY n.name
            ORDER BY next_approach;
        """
        return self._run(query, {"user_id": user_id})
