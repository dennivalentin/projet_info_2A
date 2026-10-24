from datetime import datetime

from dotenv import load_dotenv

from dao.db_connection import DBConnection
from utils.log_utils import get_logger, log
from utils.singleton import Singleton
from business_object.alert import Alert

load_dotenv()
logger = get_logger(__name__)

class AlertDao(metaclass=Singleton):
    """Class containing methods to access Alerts in the database."""

    @log
    def create(self, user_id: int, neo_id: int | None, diameter_min: float | None = None, distance_max: float | None = None, hazardous_only: bool = False) -> bool:
        """Create an alert
        Parameters
        ----------
            neo_id : Neo that the user wants to be notified about
            user_id : User associated with that alert
            diameter_min : Diameter minimum, above it a notification will be sent
            distance_max : Distance maximum, below it a notification will be sent
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
                        "INSERT INTO alert(user_id, neo_id, diameter_min, distance_max, hazardous_only, active) VALUES "
                        "(%(user_id)s, %(neo_id)s, %(diameter_min)s, %(distance_max)s, %(hazardous_only)s, TRUE) "
                        "RETURNING alert_id;",
                        {
                            "neo_id": neo_id,
                            "user_id": user_id,
                            "diameter_min": diameter_min,
                            "distance_max": distance_max,
                            "hazardous_only": hazardous_only
                        },
                    )
                    res = cursor.fetchone()
        except Exception as e:
            logger.error(e)
            return False

        created = False
        if res is not None:
            created = True

        return created
    
    @log
    def delete(self, alert_id) -> bool:
        """Delete an alert
        Parameters
        ----------
            alert_id : Alert that has to be suppressed
        Returns
        -------
            True if deleting is successful, False otherwise
        """
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "DELETE FROM alert                               "
                        " WHERE alert_id = %(alert_id)s                ",
                        {"alert_id": alert_id},
                    )
                    res = cursor.rowcount
        except Exception as e:
            logger.error(e)
            raise

        return res > 0
    
    @log
    def find_matching_approaches_for_user(self, user_id: int) -> list[dict]:
        """Find all upcoming approaches matching active alerts for a given user.

        Parameters
        ----------
        user_id : id of the user whose alerts need to be checked

        Returns
        -------
            list[dict] : list of matching events with NEO and approach details
        """
    
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT a.alert_id, a.distance_max, a.diameter_min, a.hazardous_only, n.neo_id, n.name AS neo_name, app.approach_date, app.distance, n.diameter_max   "
                        "FROM alert a "
                        "JOIN neo n ON (a.neo_id IS NULL OR a.neo_id = n.neo_id) "
                        "JOIN approach app ON app.neo_id = n.neo_id   "
                        "WHERE a.user_id = %(user_id)s  "
                        "AND a.active IS TRUE "
                        "AND (app.body = 'Earth' OR app.body IS NULL)  "
                        "AND (a.hazardous_only IS FALSE OR n.is_potentially_hazardous IS TRUE)  "
                        "AND (a.distance_max IS NULL OR app.distance <= a.distance_max)  "
                        "AND (a.diameter_min IS NULL OR n.diameter_max >= a.diameter_min)   "
                        "AND app.approach_date >= CURRENT_DATE  "
                        "ORDER BY app.approach_date ASC;",
                        {"user_id": user_id})
                    res = cursor.fetchall()

                    if res is not None:
                        return list(res)
                    else: 
                        return []

        except Exception as e:
            logger.error(e)
            return []
    

    @log
    def update(self, alert) -> bool:
        """Update an alert in the database.
        Args:
            Alert to be updated
        Returns:
            True if update is successful, False otherwise
        """
        nb_affected_rows = 0

        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "UPDATE alert                                                  "
                        "   SET alert_id = %(alert_id)s,                                "
                        "       user_id = COALESCE(%(user_id)s, user_id),            "
                        "       diameter_min = COALESCE(%(diameter_min)s, diameter_min),                                          "
                        "       distance_max = COALESCE(%(distance_max)s, distance_max),                                      "
                        "       hazardous_only = COALESCE(%(hazardous_only)s, hazardous_only),"
                        "       active = COALESCE(%(active)s, active)"
                        " WHERE alert_id = %(alert_id)s;                              ",
                        {
                            "alert_id" : alert_id,
                            "user_id": user_id,
                            "diameter_min": diameter_min,
                            "distance_max": distance_max,
                            "hazardous_only": hazardous_only,
                            "active": active
                        },
                    )
                    nb_affected_rows = cursor.rowcount
        except Exception as e:
            logger.error(e)
            raise

        return nb_affected_rows == 1
    
    def find_by_user(self, user_id) -> list[Alert]:
        """find an alert of an user
        Parameters
        ----------
            user_id : alert of this user
        Returns
        -------
            list[Alert]
        """
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT alert_id, user_id, label, distance_max, diameter_min, hazardous_only, creation_date, last_eval_date"
                        "FROM alert                               "
                        " WHERE user_id = %(user_id)s                ",
                        {"user_id": user_id},
                    )
                    res = cursor.fetchall
        except Exception as e:
            logger.error(e)
            raise

        list_alert = []

        if res:
            for row in res:
                alert = Alert(
                    alert_id= row["alert_if"], 
                    user_id = row["user_id"], 
                    label = row["label"], 
                    distance_max = row["distance_max"], 
                    diameter_min = row["diameter_min"], 
                    hazardous_only = row["diameter_min"], 
                    creation_date = row["creation_date"], 
                    last_eval_date = row["last_eval_date"]
                )

                list_alert.append(alert)

        return list_alert
    
    def find_by_id(self, alert_id):