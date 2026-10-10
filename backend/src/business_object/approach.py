from datetime import datetime


class Approach:
    """
    Class describing a NEO's approach, the distance, speed, and the like

    Attributes:
        _approach_id (int): The unique identifier of the approach event.
        _neo_id (int): The ID of the NEO making the approach.
        _approach_date (datetime): The exact date and time of the close approach.
        _distance (float): The distance from the celestial body.
        _speed (float): The relative velocity during the approach.
        _approach_day (datetime): The day of the approach (without specific time).
        _body (str): The celestial body being approached (e.g., 'Earth', 'Mars').
    """

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
        self._approach_date = approach_date
        self._distance = distance
        self._speed = speed
        self._body = body
