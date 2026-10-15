from datetime import date, datetime


class Approach:
    """
    Class describing a NEO's approach, the distance, speed, and the like

    Attributes:
        _approach_id (int): The unique identifier of the approach event.
        _neo_id (int): The ID of the NEO making the approach.
        _approach_day (date): The day of the approach (without specific time).
        _approach_date (datetime): The exact date and time of the close approach.
        _distance (float): The distance from the celestial body, in km.
        _speed (float): The relative velocity during the approach, in km/h.
        _body (str): The celestial body being approached (e.g., 'Earth', 'Mars').
    """

    def __init__(
        self,
        approach_id: int,
        neo_id: int,
        approach_day: date,
        approach_date: datetime,
        distance: float,
        speed: float,
        body: str,
    ):
        self._approach_id = approach_id
        self._neo_id = neo_id
        self._approach_day = approach_day
        self._approach_date = approach_date
        self._distance = distance
        self._speed = speed
        self._body = body
