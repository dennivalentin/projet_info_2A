
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
        alert_id: int | None = None,
        user_id: int = 1,
        label: str | None = None,
        distance_max: float | None = None,
        diameter_min: float | None = None,
        hazardous_only: bool = False,
        active: bool = True,
        creation_date: datetime | None = None,
        last_eval_date: datetime | None = None,
        # Backward-compatibility aliases
        neo_id: int | None = None,
        obj_neo: Neo | None = None,
        min_diameter: float | None = None,
        max_distance: float | None = None,
        is_active: bool | None = None,
    ):
        self._alert_id = alert_id
        self._user_id = user_id
        self._label = label or (f"NEO-{neo_id}" if neo_id is not None else "Alert")
        self._distance_max = distance_max if distance_max is not None else max_distance
        self._diameter_min = diameter_min if diameter_min is not None else min_diameter
        self._hazardous_only = bool(hazardous_only)
        self._active = active if is_active is None else is_active
        self._creation_date = creation_date or datetime.now()
        self._last_eval_date = last_eval_date
        self._neo_id = neo_id
        self._object = obj_neo

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

    @property
    def neo_id(self) -> int | None:
        return self._neo_id

    @neo_id.setter
    def neo_id(self, value: int | None) -> None:
        self._neo_id = value

    @property
    def obj_neo(self) -> Neo | None:
        return self._object

    @obj_neo.setter
    def obj_neo(self, value: Neo | None) -> None:
        self._object = value

    def to_dict(self) -> dict:
        return {
            "alert_id": self._alert_id,
            "user_id": self._user_id,
            "label": self._label,
            "distance_max": self._distance_max,
            "diameter_min": self._diameter_min,
            "hazardous_only": self._hazardous_only,
            "active": self._active,
            "creation_date": self._creation_date.isoformat() if hasattr(self._creation_date, "isoformat") else str(self._creation_date),
            "last_eval_date": self._last_eval_date.isoformat() if self._last_eval_date and hasattr(self._last_eval_date, "isoformat") else (str(self._last_eval_date) if self._last_eval_date else None),
            "neo_id": self._neo_id,
        }

    def __repr__(self) -> str:
        return f"<Alert id={self._alert_id} user={self._user_id} label='{self._label}' active={self._active}>"

    def __str__(self) -> str:
        return f"Alert #{self._alert_id} (User: {self._user_id}) - {self._label} [Active: {self._active}]"
