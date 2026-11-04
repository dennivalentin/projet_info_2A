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
    def create(
        self,
        user_id: int,
        label: str,
        diameter_min: float | None = None,
        distance_max: float | None = None,
        hazardous_only: bool = False,
    ) -> bool:
        """Create an alert
        Parameters
        ----------
            user_id : User associated with that alert
            label : caption made by the user
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
                        "INSERT INTO alert(user_id, label, diameter_min, distance_max, hazardous_only, active, last_eval_date) "
                        "SELECT %(user_id)s, %(label)s, %(diameter_min)s, %(distance_max)s, %(hazardous_only)s, TRUE, NULL  "
                        """WHERE NOT EXISTS (
                            SELECT 1 FROM alert
                            WHERE user_id = %(user_id)s
                            AND diameter_min IS NOT DISTINCT FROM %(diameter_min)s
                            AND distance_max IS NOT DISTINCT FROM %(distance_max)s
                            AND hazardous_only = %(hazardous_only)s
                        )
                        RETURNING alert_id;""",
                        {
                            "user_id": user_id,
                            "label": label,
                            "diameter_min": diameter_min,
                            "distance_max": distance_max,
                            "hazardous_only": hazardous_only,
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
                        "SELECT a.alert_id, a.label, a.distance_max, a.diameter_min, a.hazardous_only, n.neo_id, n.name AS neo_name, app.approach_date, app.distance, n.diameter_max   "
                        "FROM alert a "
                        "CROSS JOIN neo n "
                        "JOIN approach app ON app.neo_id = n.neo_id   "
                        "WHERE a.user_id = %(user_id)s  "
                        "AND a.active IS TRUE "
                        "AND (app.body = 'Earth' OR app.body IS NULL)  "
                        "AND (a.hazardous_only IS FALSE OR n.hazardous IS TRUE)  "
                        "AND (a.distance_max IS NULL OR app.distance <= a.distance_max)  "
                        "AND (a.diameter_min IS NULL OR n.diameter_max >= a.diameter_min)   "
                        "AND app.approach_date >= CURRENT_DATE  "
                        "ORDER BY app.approach_date ASC;",
                        {"user_id": user_id},
                    )
                    res = cursor.fetchall()

                    if res is not None:
                        return list(res)
                    else:
                        return []

        except Exception as e:
            logger.error(e)
            return []

    @log
    def update(self, alert: Alert) -> bool:
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
                        "       label = COALESCE(%(label)s, label), "
                        "       distance_max = COALESCE(%(distance_max)s, distance_max),                                      "
                        "       diameter_min = COALESCE(%(diameter_min)s, diameter_min),                                          "
                        "       hazardous_only = COALESCE(%(hazardous_only)s, hazardous_only),"
                        "       active = COALESCE(%(active)s, active),  "
                        "       last_eval_date= COALESCE(%(today)s, last_eval_date)"
                        " WHERE alert_id = %(alert_id)s;                              ",
                        {
                            "alert_id": alert.alert_id,
                            "user_id": alert.user_id,
                            "label": alert.label,
                            "diameter_min": alert.diameter_min,
                            "distance_max": alert.distance_max,
                            "hazardous_only": alert.hazardous_only,
                            "active": alert.active,
                            "today": alert.last_eval_date,
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
                        "SELECT alert_id, user_id, label, distance_max, diameter_min, hazardous_only, active, creation_date, last_eval_date   "
                        "FROM alert                               "
                        " WHERE user_id = %(user_id)s                ",
                        {"user_id": user_id},
                    )
                    res = cursor.fetchall()
        except Exception as e:
            logger.error(e)
            raise

        list_alert = None

        if res:
            list_alert = []
            for row in res:
                alert = Alert(
                    alert_id=row["alert_id"],
                    user_id=row["user_id"],
                    label=row["label"],
                    distance_max=row["distance_max"],
                    diameter_min=row["diameter_min"],
                    hazardous_only=row["hazardous_only"],
                    creation_date=row["creation_date"],
                    active=row["active"],
                    last_eval_date=row["last_eval_date"],
                )

                list_alert.append(alert)

        return list_alert

    def find_by_id(self, alert_id) -> Alert:
        """find an alert by its id
        Parameters
        ----------
            alert_id : id of this alert
        Returns
        -------
            Alert
        """
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT alert_id, user_id, label, distance_max, diameter_min, hazardous_only, active, creation_date, last_eval_date   "
                        "FROM alert                               "
                        " WHERE alert_id = %(alert_id)s                ",
                        {"alert_id": alert_id},
                    )
                    res = cursor.fetchone()
        except Exception as e:
            logger.error(e)
            raise

        if res:
            alert = Alert(
                alert_id=res["alert_id"],
                user_id=res["user_id"],
                label=res["label"],
                distance_max=res["distance_max"],
                diameter_min=res["diameter_min"],
                hazardous_only=res["hazardous_only"],
                creation_date=res["creation_date"],
                active=res["active"],
                last_eval_date=res["last_eval_date"],
            )
        else:
            return None

        return alert
