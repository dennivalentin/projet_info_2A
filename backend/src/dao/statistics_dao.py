"""FO3 - Database queries for the statistics page."""

from dao.db_connection import DBConnection
from utils.singleton import Singleton


class StatisticsDao(metaclass=Singleton):
    """Aggregate queries (GROUP BY, AVG, ...) on the approach and neo tables."""

    def _run(self, query: str) -> list[dict]:
        """Runs a SELECT query and returns the rows as a list of dicts."""
        with DBConnection().connection as connection:
            with connection.cursor() as cursor:
                cursor.execute(query)
                return [dict(row) for row in cursor.fetchall()]

    def approaches_per_month(self) -> list[dict]:
        """Query 1: number of approaches per month."""
        query = """
            SELECT TO_CHAR(approach_day, 'YYYY-MM') AS month,
                   COUNT(*) AS nb_approaches
            FROM approach
            GROUP BY month
            ORDER BY month;
        """
        return self._run(query)

    def size_distribution(self) -> list[dict]:
        """Query 2: number of NEOs per size class (mean estimated diameter, in km)."""
        query = """
            SELECT CASE
                       WHEN (diameter_min + diameter_max) / 2 < 0.025 THEN '1. < 25 m'
                       WHEN (diameter_min + diameter_max) / 2 < 0.14  THEN '2. 25 m - 140 m'
                       WHEN (diameter_min + diameter_max) / 2 < 1     THEN '3. 140 m - 1 km'
                       ELSE '4. > 1 km'
                   END AS size_class,
                   COUNT(*) AS nb_neos
            FROM neo
            GROUP BY size_class
            ORDER BY size_class;
        """
        return self._run(query)

    def global_summary(self) -> dict:
        """Query 3: number of NEOs, % hazardous, mean and median distance."""
        query = """
            SELECT COUNT(DISTINCT a.neo_id) AS nb_neos,
                   ROUND(100.0 * COUNT(DISTINCT a.neo_id) FILTER (WHERE n.hazardous)
                         / NULLIF(COUNT(DISTINCT a.neo_id), 0), 1) AS hazardous_pct,
                   ROUND(AVG(a.distance)) AS avg_distance_km,
                   ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY a.distance)::numeric)
                       AS median_distance_km
            FROM approach a
            JOIN neo n ON n.neo_id = a.neo_id;
        """
        return self._run(query)[0]
