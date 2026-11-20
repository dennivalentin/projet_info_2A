from business_object.alert import Alert
from dao.alert_dao import AlertDao
from utils.log_utils import log
from utils.singleton import Singleton


class AlertService(metaclass=Singleton):
    """Business logic of the alerts: creation, notifications, activation."""

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

        if not hazardous_only and diameter_min is None and distance_max is None:
            raise ValueError("At least one criterion should be submitted to create an alert")

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
        """Returns the new notifications of a user, and marks them as shown.

        A notification is given once: the alerts that matched are marked as
        evaluated, and the next call only returns approaches recorded since.

        Parameters
        ----------
            user_id : user that needs to be informed

        Return
        ------
            list[str] : the notification messages (empty if there is nothing new)
        """
        matching_approaches = AlertDao().find_matching_approaches_for_user(user_id)
        list_notif = [self._message(item) for item in matching_approaches]

        for alert_id in {item["alert_id"] for item in matching_approaches}:
            self.last_eval_update(alert_id)

        return list_notif

    @staticmethod
    def _message(item: dict) -> str:
        """Text of one notification, e.g.
        "[Close ones] HAZARDOUS 99942 Apophis on 2029-04-13: distance 31,000 km <= 100,000 km"
        """
        notif = f"[{item.get('label', 'Alert')}] "
        if item.get("hazardous_only") is True:
            notif += "HAZARDOUS "
        notif += item["neo_name"]
        approach_date = item.get("approach_date")
        if approach_date is not None and hasattr(approach_date, "strftime"):
            notif += f" on {approach_date.strftime('%Y-%m-%d')}"

        details = []
        if item.get("diameter_min") is not None:
            details.append(
                f"diameter {float(item['diameter_max']):.3f} km"
                f" >= {float(item['diameter_min']):.3f} km"
            )
        if item.get("distance_max") is not None:
            details.append(
                f"distance {float(item['distance']):,.0f} km <= {float(item['distance_max']):,.0f} km"
            )
        if details:
            notif += ": " + ", ".join(details)
        return notif

    def list_alert_user(self, user_id) -> list[Alert]:
        """Finds the alerts of a user

        Parameters
        ----------
            user_id : alert of this user

        Return
        ------
            list[Alert] : list of alerts (empty if none)
        """
        return AlertDao().find_by_user(user_id)

    def find_by_id(self, alert_id: int) -> Alert | None:
        """Finds an alert by its id (None if it does not exist)."""
        return AlertDao().find_by_id(alert_id)

    def turn_on_off(self, alert_id: int) -> bool:
        """Turns an alert off if it is active, and on otherwise.

        Args:
            alert_id: The alert to switch.

        Returns:
            bool: True if the alert was switched, False if it does not exist.
        """
        alert = AlertDao().find_by_id(alert_id)
        if alert is None:
            return False
        alert.active = not alert.active
        return AlertDao().update(alert)

    def last_eval_update(self, alert_id: int) -> bool:
        """Records that the alert has just been evaluated (last_eval_date = now).

        Args:
            alert_id: The alert to update.

        Returns:
            bool: True if the alert was updated, False if it does not exist.
        """
        return AlertDao().mark_evaluated(alert_id)

    def delete(self, alert_id: int) -> bool:
        """Deletes an alert.

        Returns:
            bool: True if an alert was deleted.
        """
        return AlertDao().delete(alert_id)
