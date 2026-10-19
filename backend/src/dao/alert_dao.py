from dao.db_connection import DBConnection
from utils.log_utils import get_logger, log
from utils.singleton import Singleton
from datetime import datetime
from dotenv import load_dotenv


load_dotenv()
logger = get_logger(__name__)

class AlertDao(metaclass=Singleton):
    """Class containing methods to access Alerts in the database."""

    @log
    def create(self, user_id: int, neo_id: int | None, min_diameter: float | None = None, max_distance: float | None = None, hazardous_only: bool = False) -> bool:
        """Create an alert
        Parameters
        ----------
            neo_id : Neo that the user wants to be notified about
            user_id : User associated with that alert
            min_diameter : Diameter minimum, above it a notification will be sent
            max_distance : Distance maximum, below it a notification will be sent
            hazardous_only : Does the user want to see only hazardous Neo's according to the critera 
        Returns
        -------
            True if creation is successful, False otherwise
        """
        res = None

        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "INSERT INTO alert(user_id, neo_id, min_diameter, max_distance, hazardous_only) VALUES "
                        "(%(user_id)s, %(neo_id)s, %(min_diameter)s, %(max_distance)s, %(hazardous_only)s) "
                        "RETURNING neo_id;",
                        {
                            "neo_id": neo_id,
                            "user_id": user_id,
                            "min_diameter": min_diameter,
                            "max_distance": max_distance,
                            "hazardous_only": hazardous_only
                        },
                    )
                    res = cursor.fetchone()
        except Exception as e:
            logger.error(e)
            raise

        created = False
        if res:
            created = True

        return created
    
    @log
    def delete(self, neo_id, user_id) -> bool:
        """Delete a favourite
        Parameters
        ----------
            neo_id : Neo that the user wants to mark as favourite
            user_id : user with that favourite
        Returns
        -------
            True if deleting is successful, False otherwise
        """
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "DELETE FROM favourite                               "
                        " WHERE user_id = %(user_id)s and neo_id = %(neo_id)s                 ",
                        {"user_id": user_id, "neo_id": neo_id},
                    )
                    res = cursor.rowcount
        except Exception as e:
            logger.error(e)
            raise

        return res > 0