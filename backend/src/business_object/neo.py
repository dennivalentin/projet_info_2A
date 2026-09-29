from date import datetime


class Neo:
    """
    Class describing a NEO in the app

    Attributes:
        _neo_id (int): The internal unique identifier for the NEO.
        _nasa_id (str): The official identifier provided by NASA.
        _name (str): The name of the Near-Earth Object.
        _absolute_magnitude (float): The absolute magnitude of the NEO.
        _diameter_min (float): The estimated minimum diameter in kilometers.
        _diameter_max (float): The estimated maximum diameter in kilometers.
        _hazardious (bool): Indicates if the NEO is considered potentially hazardous.
        _url_nasa (str): The URL to the NASA web page for this object.
        _custom (bool): True if the NEO was created by a user, False if from NASA.
        _date_update (datetime): The date this record was last updated.
    """

    def __init__(
        self,
        neo_id: int,
        nasa_id: str,
        name: str,
        absolute_magnitude: float,
        diameter_min: float,
        diameter_max: float,
        hazardious: bool,
        url_nasa: str,
        custom: bool,
        date_update: datetime,
    ):
        self._neo_id = neo_id
        self._nasa_id = nasa_id
        self._name = name
        self._absolute_magnitude = absolute_magnitude
        self._diameter_min = diameter_min
        self._diameter_max = diameter_max
        self._hazardious = hazardious
        self._url_nasa = url_nasa
        self._custom = custom
        self._date_update = date_update
