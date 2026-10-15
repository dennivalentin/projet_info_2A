from datetime import datetime


class Alert:
    """
    Class describing a threshold alert defined by a user.
    The alert is a filter applied to every NEO: a NEO matches it when it satisfies
    all the thresholds that are set. It is evaluated in SQL when the user logs in.

    Attributes:
        _alert_id (int): The unique identifier of the alert.
        _user_id (int): The ID of the user who created the alert.
        _label (str): The name given to the alert by the user.
        _distance_max (float | None): The maximum approach distance in km (None = no threshold).
        _diameter_min (float | None): The minimum diameter in km (None = no threshold).
        _hazardous_only (bool): True if only potentially hazardous NEOs match the alert.
        _active (bool): Indicates whether the alert is currently active.
        _creation_date (datetime): The date and time the alert was created.
        _last_eval_date (datetime | None): The last time the alert was evaluated.
    """

    def __init__(
        self,
        alert_id: int,
        user_id: int,
        label: str,
        distance_max: float | None,
        diameter_min: float | None,
        hazardous_only: bool,
        active: bool,
        creation_date: datetime,
        last_eval_date: datetime | None,
    ):
        self._alert_id = alert_id
        self._user_id = user_id
        self._label = label
        self._distance_max = distance_max
        self._diameter_min = diameter_min
        self._hazardous_only = hazardous_only
        self._active = active
        self._creation_date = creation_date
        self._last_eval_date = last_eval_date
