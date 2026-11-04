from dao.db_connection import DBConnection
from business_object.approach import Approach
from utils.log_utils import get_logger, log

logger = get_logger(__name__)


class ApproachDao:
    
    @log
    def create(self, approach: Approach) -> bool:
        """
        Create a NEO's approach in the approach table
        """
        query = """
            INSERT INTO approach (
                neo_id, approach_day, approach_date, body, distance, speed
            ) VALUES (
                %(neo_id)s, %(approach_day)s, %(approach_date)s, %(body)s, %(distance)s, %(speed)s
            )
            ON CONFLICT (neo_id, approach_day) DO UPDATE SET
                distance = EXCLUDED.distance,
                speed = EXCLUDED.speed
            RETURNING approach_id;
        """
        with DBConnection().connection as conn:
            with conn.cursor() as cur:
                cur.execute(
                    query,
                    {
                        "neo_id": approach._neo_id,
                        "approach_day": approach._approach_day,
                        "approach_date": approach._approach_date,
                        "body": approach._body,
                        "distance": approach._distance,
                        "speed": approach._speed,
                    },
                )
                res = cur.fetchone()
                if res:
                    approach_id = (
                        res["approach_id"] if isinstance(res, dict) else res[0]
                    )
                    approach._approach_id = approach_id
                    return True
        return False
    
    @log
    def find_by_neo_id(self, neo_id: int) -> list[Approach]:
        """Fetch all close approaches for a given NEO ordered by date.
        Args:
            neo_id: Internal ID of the NEO.
        Returns:
            List of Approach objects.
        """
        query = """
            SELECT * FROM approach
            WHERE neo_id = %(neo_id)s
            ORDER BY approach_day ASC;
        """
        try:
            with DBConnection().connection as conn:
                with conn.cursor() as cur:
                    cur.execute(query, {"neo_id": neo_id})
                    rows = cur.fetchall() or []
                    return [self._map_row_to_approach(row) for row in rows]
        except Exception as e:
            logger.error(f"Error in ApproachDao.find_by_neo_id: {e}")
            raise
    
    def _map_row_to_approach(self, row: dict) -> Approach:
        return Approach(
            approach_id=row["approach_id"],
            neo_id=row["neo_id"],
            approach_day=row["approach_day"],
            approach_date=row["approach_date"],
            distance=row["distance"],
            speed=row["speed"],
            body=row["body"],
        )
