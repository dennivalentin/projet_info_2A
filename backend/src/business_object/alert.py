from datetime import datetime

from business_object.neo import Neo


class Alert:
    """Class describing an alert configured by a user.

    Attributes:
        _alert_id (int | None): The unique identifier of the alert.
        _user_id (int): The ID of the user who created the alert.
        _label (str): Descriptive label or tracked object name.
        _distance_max (float | None): The maximum approach distance threshold (in km).
        _diameter_min (float | None): The minimum diameter threshold to trigger the alert (in km).
        _hazardous_only (bool): If True, only potentially hazardous NEOs trigger this alert.
        _active (bool): Indicates whether the alert is currently active.
        _creation_date (datetime): The timestamp when the alert was created.
        _last_eval_date (datetime | None): Timestamp of the last evaluation.
    """

    def __init__(
        self,
        user_id: int,
        alert_id: int | None = None,
        label: str | None = None,
        distance_max: float | None = None,
        diameter_min: float | None = None,
        hazardous_only: bool = False,
        active: bool = True,
        creation_date: datetime | None = None,
        last_eval_date: datetime | None = None,
    ):
        self._alert_id = alert_id
        self._user_id = user_id
        self._label = label
        self._distance_max = distance_max
        self._diameter_min = diameter_min
        self._hazardous_only = bool(hazardous_only)
        self._active = active
        self._creation_date = creation_date or datetime.now()
        self._last_eval_date = last_eval_date

    @property
    def alert_id(self) -> int | None:
        return self._alert_id

    @alert_id.setter
    def alert_id(self, value: int | None) -> None:
        self._alert_id = value

    @property
    def user_id(self) -> int:
        return self._user_id

    @user_id.setter
    def user_id(self, value: int) -> None:
        self._user_id = value

    @property
    def label(self) -> str:
        return self._label

    @label.setter
    def label(self, value: str) -> None:
        self._label = value

    @property
    def distance_max(self) -> float | None:
        return self._distance_max

    @distance_max.setter
    def distance_max(self, value: float | None) -> None:
        self._distance_max = float(value) if value is not None else None

    @property
    def max_distance(self) -> float | None:
        return self._distance_max

    @max_distance.setter
    def max_distance(self, value: float | None) -> None:
        self._distance_max = float(value) if value is not None else None

    @property
    def diameter_min(self) -> float | None:
        return self._diameter_min

    @diameter_min.setter
    def diameter_min(self, value: float | None) -> None:
        self._diameter_min = float(value) if value is not None else None

    @property
    def min_diameter(self) -> float | None:
        return self._diameter_min

    @min_diameter.setter
    def min_diameter(self, value: float | None) -> None:
        self._diameter_min = float(value) if value is not None else None

    @property
    def hazardous_only(self) -> bool:
        return self._hazardous_only

    @hazardous_only.setter
    def hazardous_only(self, value: bool) -> None:
        self._hazardous_only = bool(value)

    @property
    def active(self) -> bool:
        return self._active

    @active.setter
    def active(self, value: bool) -> None:
        self._active = bool(value)

    @property
    def is_active(self) -> bool:
        return self._active

    @is_active.setter
    def is_active(self, value: bool) -> None:
        self._active = bool(value)

    @property
    def creation_date(self) -> datetime:
        return self._creation_date

    @creation_date.setter
    def creation_date(self, value: datetime) -> None:
        self._creation_date = value

    @property
    def last_eval_date(self) -> datetime | None:
        return self._last_eval_date

    @last_eval_date.setter
    def last_eval_date(self, value: datetime | None) -> None:
        self._last_eval_date = value

    def to_dict(self) -> dict:
        return {
            "alert_id": self._alert_id,
            "user_id": self._user_id,
            "label": self._label,
            "distance_max": self._distance_max,
            "diameter_min": self._diameter_min,
            "hazardous_only": self._hazardous_only,
            "active": self._active,
            "creation_date": (
                self._creation_date.isoformat()
                if hasattr(self._creation_date, "isoformat")
                else str(self._creation_date)
            ),
            "last_eval_date": (
                self._last_eval_date.isoformat()
                if self._last_eval_date and hasattr(self._last_eval_date, "isoformat")
                else (str(self._last_eval_date) if self._last_eval_date else None)
            ),
        }

    def __repr__(self) -> str:
        return f"<Alert id={self._alert_id} user={self._user_id} label='{self._label}' active={self._active}>"

    def __str__(self) -> str:
        return f"Alert #{self._alert_id} (User: {self._user_id}) - {self._label} [Active: {self._active}]"


'''
from datetime import datetime


class Alert:
    """
    Class describing the alert that could be send to the user

    Attributes:
        _alert_id (int): The unique identifier of the alert.
        _user_id (int): The ID of the user who created the alert.
        _label (str): Description of the alert
        _diameter_min (float): The minimum diameter threshold to trigger the alert.
        _distance_max (float): The maximum approach distance threshold.
        _hazardous_only(bool): Allows to filter the neo in the alert by only hazardous one
        _active (bool): Indicates whether the alert is currently active or dismissed.
        _creation_date: The moment when the alert has been created
        _last_eval_date: The last time when the alert hasbeen checked
    """

    def __init__(
        self,
        alert_id: int,
        user_id: int = None,
        label: str = None,
        diameter_min: float = None,
        distance_max: float = None,
        hazardous_only: bool = None,
        active: bool = None,
        creation_date: datetime = None,
        last_eval_date: datetime = None,
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

    def __repr__(self):
        beg = f"""Alert n° {self._alert_id} from user : {self._user_id}. Criteria :
        {self._label}"""

        if self._diameter_min is not None:
            beg += f" | Minimum diameter : {self._diameter_min}"

        if self._distance_max is not None:
            beg += f" | Maximum distance : {self._distance_max}"

        if self._hazardous_only is not None:
            beg += f" | Hazardous : {self._hazardous_only}"

        beg += f" | Active = {self._active}"

        return beg

    def __str__(self):
        beg = f"""Alert n° {self._alert_id} from user : {self._user_id}. Criteria :
        {self._label}"""

        if self._diameter_min is not None:
            beg += f" | Minimum diameter : {self._diameter_min}"

        if self._distance_max is not None:
            beg += f" | Maximum distance : {self._distance_max}"

        if self._hazardous_only is not None:
            beg += f" | Hazardous : {self._hazardous_only}"

        beg += f" | Active = {self._active}"

        return beg
'''
