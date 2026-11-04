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

    def __repr__(self):
        return f"Neo : {self._neo_id}, approach on {self._approach_day} by {self._body}"
