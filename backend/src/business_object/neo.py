from datetime import datetime

class Neo:
    """Class describing a Near-Earth Object (NEO) in the app.

    Attributes:
        _neo_id (int | None): The internal unique identifier for the NEO, by default None.
        _nasa_id (str | None): The official identifier provided by NASA.
        _name (str): The name of the Near-Earth Object.
        _absolute_magnitude (float | None): The absolute magnitude of the NEO.
        _diameter_min (float | None): The estimated minimum diameter in kilometers.
        _diameter_max (float | None): The estimated maximum diameter in kilometers.
        _hazardous (bool): Indicates if the NEO is considered potentially hazardous.
        _url_nasa (str | None): The URL to the NASA web page for this object.
        _origin (str): Either 'NASA' for an API import or 'USER' for user creation.
        _date_update (datetime): The date this record was last updated.
    """

    def __init__(
        self,
        nasa_id: str | None,
        name: str,
        absolute_magnitude: float | None,
        diameter_min: float | None,
        diameter_max: float | None,
        hazardous: bool,
        url_nasa: str | None,
        origin: str,
        date_update: datetime,
        neo_id: int | None = None,
    ):
        self._neo_id = neo_id
        self._nasa_id = nasa_id
        self._name = name
        self._absolute_magnitude = absolute_magnitude
        self._diameter_min = diameter_min
        self._diameter_max = diameter_max
        self._hazardous = bool(hazardous)
        self._url_nasa = url_nasa
        self._origin = origin
        self._date_update = date_update

    @property
    def neo_id(self) -> int | None:
        return self._neo_id

    @neo_id.setter
    def neo_id(self, value: int | None) -> None:
        self._neo_id = value

    @property
    def nasa_id(self) -> str | None:
        return self._nasa_id

    @nasa_id.setter
    def nasa_id(self, value: str | None) -> None:
        self._nasa_id = value

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value

    @property
    def absolute_magnitude(self) -> float | None:
        return self._absolute_magnitude

    @absolute_magnitude.setter
    def absolute_magnitude(self, value: float | None) -> None:
        self._absolute_magnitude = value

    @property
    def diameter_min(self) -> float | None:
        return self._diameter_min

    @diameter_min.setter
    def diameter_min(self, value: float | None) -> None:
        self._diameter_min = value

    @property
    def diameter_max(self) -> float | None:
        return self._diameter_max

    @diameter_max.setter
    def diameter_max(self, value: float | None) -> None:
        self._diameter_max = value

    @property
    def hazardous(self) -> bool:
        return self._hazardous

    @hazardous.setter
    def hazardous(self, value: bool) -> None:
        self._hazardous = bool(value)

    @property
    def url_nasa(self) -> str | None:
        return self._url_nasa

    @url_nasa.setter
    def url_nasa(self, value: str | None) -> None:
        self._url_nasa = value

    @property
    def origin(self) -> str:
        return self._origin

    @origin.setter
    def origin(self, value: str) -> None:
        self._origin = value

    @property
    def date_update(self) -> datetime:
        return self._date_update

    @date_update.setter
    def date_update(self, value: datetime) -> None:
        self._date_update = value

    def to_dict(self) -> dict:
        return {
            "neo_id": self._neo_id,
            "nasa_id": self._nasa_id,
            "name": self._name,
            "absolute_magnitude": float(self._absolute_magnitude) if self._absolute_magnitude is not None else None,
            "diameter_min": float(self._diameter_min) if self._diameter_min is not None else None,
            "diameter_max": float(self._diameter_max) if self._diameter_max is not None else None,
            "hazardous": self._hazardous,
            "url_nasa": self._url_nasa,
            "origin": self._origin,
            "date_update": self._date_update.isoformat() if isinstance(self._date_update, datetime) else str(self._date_update),
        }

    def __repr__(self) -> str:
        return f"<Neo id={self._neo_id} name='{self._name}' origin='{self._origin}'>"
