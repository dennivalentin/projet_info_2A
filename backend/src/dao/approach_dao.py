from dao.db_connection import DBConnection
from business_object.approach import Approach


class ApproachDao:
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
