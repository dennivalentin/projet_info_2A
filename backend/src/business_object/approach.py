from datetime import date, datetime


class Approach:
    """Class describing a NEO's close approach.

    Attributes:
        _approach_id (int | None): The unique identifier of the approach event.
        _neo_id (int): The ID of the NEO making the approach.
        _approach_date (datetime): The exact date and time of the close approach.
        _distance (float): The distance from the celestial body in kilometers.
        _speed (float): The relative velocity during the approach in km/h.
        _approach_day (date): The day of the approach.
        _body (str): The celestial body being approached (e.g., 'Earth', 'Mars').
    """

    #  Astronomical Unit (AU) in kilometers
    KM_PER_AU = 149597870.7

    def __init__(
        self,
        neo_id: int,
        approach_date: datetime,
        distance: float,
        speed: float,
        body: str,
        approach_id: int | None = None,
    ):
        self._approach_id = approach_id
        self._neo_id = neo_id
        self._approach_day = None
        self._approach_date = approach_date
        self._distance = float(distance) if distance is not None else 0.0
        self._speed = float(speed) if speed is not None else 0.0
        self._body = body

    @property
    def approach_id(self) -> int | None:
        return self._approach_id

    @approach_id.setter
    def approach_id(self, value: int | None) -> None:
        self._approach_id = value

    @property
    def neo_id(self) -> int:
        return self._neo_id

    @neo_id.setter
    def neo_id(self, value: int) -> None:
        self._neo_id = value

    @property
    def approach_day(self) -> date:
        return self._approach_date.date()  # noqa: E101, W191

    @approach_day.setter
    def approach_day(self, value: date) -> None:
        self._approach_day = value

    @property
    def approach_date(self) -> datetime:
        return self._approach_date

    @approach_date.setter
    def approach_date(self, value: datetime) -> None:
        self._approach_date = value

    @property
    def distance(self) -> float:
        return self._distance

    @distance.setter
    def distance(self, value: float) -> None:
        self._distance = float(value)

    @property
    def distance_au(self) -> float:
        """Distance converted to Astronomical Units (AU)."""
        return round(self._distance / self.KM_PER_AU, 5)

    @property
    def speed(self) -> float:
        return self._speed

    @speed.setter
    def speed(self, value: float) -> None:
        self._speed = float(value)

    @property
    def body(self) -> str:
        return self._body

    @body.setter
    def body(self, value: str) -> None:
        self._body = value

    def to_dict(self) -> dict:
        return {
            "approach_id": self._approach_id,
            "neo_id": self._neo_id,
            "approach_day": self._approach_day.isoformat() if hasattr(self._approach_day, "isoformat") else str(self._approach_day),
            "approach_date": self._approach_date.isoformat() if hasattr(self._approach_date, "isoformat") else str(self._approach_date),
            "distance_km": self._distance,
            "distance_au": self.distance_au,
            "speed_km_h": self._speed,
            "body": self._body,
        }

    def __repr__(self) -> str:
        return f"<Approach id={self._approach_id} neo={self._neo_id} day={self._approach_day}>"
