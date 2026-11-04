from dao.alert_dao import AlertDao
from business_object.alert import Alert
from utils.log_utils import log
from utils.singleton import Singleton
from datetime import datetime


class AlertService(metaclass=Singleton):

    @log
    def create_alert(
        self,
        user_id: int,
        label: str,
        diameter_min: float | None = None,
        distance_max: float | None = None,
        hazardous_only: bool = False,
    ) -> bool:
        """Create an alert according to what the user want to see

        Parameters
        ----------
            user_id: user who is asking
            label: str : caption of the alert
            diameter_min: float | None : A possible size of a neo to be notified about
            distance_max: float | None : Below that possible distance a notification is sent
            hazardous_only : bool : If the user wants to see only hazardous Neo

        Return
        ------
            bool, True if well created, False otherwise
        """

        if hazardous_only is None and diameter_min is None and distance_max is None:
            raise ValueError(
                "At least one criterion should be submitted to create an alert"
            )

        if (diameter_min is not None and diameter_min <= 0) or (
            distance_max is not None and distance_max <= 0
        ):
            raise ValueError("Give a positive value")

        return AlertDao().create(
            user_id=user_id,
            label=label,
            diameter_min=diameter_min,
            distance_max=distance_max,
            hazardous_only=hazardous_only,
        )

    def check_send_notification(self, user_id: int) -> list[str]:
        """Method to check if a notification has to be sent according to the user

        Parameters
        ----------
            user_id : user that needs to be informed

        Return
        ------
            list[str] : list of alert messages
        """

        matching_approaches = AlertDao().find_matching_approaches_for_user(user_id)
        list_notif = []

        for item in matching_approaches:
            neo_name = item["neo_name"]

            if item.get("hazardous_only") is True:
                notif = f"HAZARDOUS | {neo_name}"
            else:
                notif = f"{neo_name}"

            if item["diameter_min"] is not None:
                notif += f" : diameter of the neo {item['diameter_max']}>= {item['diameter_min']}"
            if item["distance_max"] is not None:
                notif += f" : distance from Earth is {item['distance']} <= {item['distance_max']}"

            list_notif.append(notif)

        alert_ids_updated = set()
        if len(list_notif) != 0:
            for item in matching_approaches:
                if item["alert_id"] not in alert_ids_updated:
                    AlertService().last_eval_update(item["alert_id"])
                    alert_ids_updated.add(item["alert_id"])
            return list_notif
        else:
            return ["No alert detected"]

    def list_alert_user(self, user_id) -> list[Alert]:
        """find the alert by user

        Parameters
        ----------
            user_id : alert of this user

        Return
        ------
            list[Alert] : list of alerts
        """
        alerts = AlertDao().find_by_user(user_id)
        return alerts

    def turn_on_off(self, alert_id) -> bool:
        """method in order to turn off an alert if it is active, and on otherwise

        Parameters
        ----------
            alert_id : Alert that we want to turn off

        Return
        ------
            bool : True if the changement has been done, False if the alert does not exists
        """

        alert = AlertDao().find_by_id(alert_id)
        if alert is None:
            return False
        status = alert.active

        if status:
            AlertDao().update(
                Alert(
                    alert_id=alert.alert_id,
                    user_id=alert.user_id,
                    label=alert.label,
                    distance_max=alert.distance_max,
                    diameter_min=alert.diameter_min,
                    hazardous_only=alert.hazardous_only,
                    active=False,
                    creation_date=alert.creation_date,
                    last_eval_date=alert.last_eval_date,
                )
            )
        else:
            AlertDao().update(
                Alert(
                    alert_id=alert.alert_id,
                    user_id=alert.user_id,
                    label=alert.label,
                    distance_max=alert.distance_max,
                    diameter_min=alert.diameter_min,
                    hazardous_only=alert.hazardous_only,
                    active=True,
                    creation_date=alert.creation_date,
                    last_eval_date=alert.last_eval_date,
                )
            )

        return True

    def last_eval_update(self, alert_id) -> bool:
        """update the last eval date
        Parameters
        ----------
            alert_id : Alert that we want to update

        Return
        ------
            bool : True if the changement has been done, False if the alert does not exists
        """

        alert = AlertDao().find_by_id(alert_id)
        if alert is None:
            return False

        AlertDao().update(
            Alert(
                alert_id=alert.alert_id,
                user_id=alert.user_id,
                label=alert.label,
                distance_max=alert.distance_max,
                diameter_min=alert.diameter_min,
                hazardous_only=alert.hazardous_only,
                active=alert.active,
                creation_date=alert.creation_date,
                last_eval_date=datetime.today(),
            )
        )

        return True

    def delete(self, alert_id) -> bool:
        AlertDao().delete(alert_id)
