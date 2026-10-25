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

    def find_all_by_neo(self, neo_id: int) -> list[Approach]:
        """
        Finds all the approach avalaible for a precise Neo

        Parameters
        ----------
            neo_id : Id of the asked Neo

        Return
        ------
            list[Approach] : list of all approaches
        """

        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT *                               "
                        "  FROM approach                           "
                        "WHERE neo_id = %(neo_id)s",
                        {"neo_id": neo_id},
                    )
                    res = cursor.fetchall()
        except Exception as e:
            logger.error(e)
            raise

        list_approaches = []

        if res:
            for row in res:
                approach = Approach(
                    neo_id=row["neo_id"],
                    approach_date=row["approach_date"],
                    approach_day=row["approach_day"],
                    distance=row["distance"],
                    speed=row["speed"],
                    body=row["body"],
                    approach_id=row["approach_id"],
                )

                list_approaches.append(approach)

        return list_approaches
