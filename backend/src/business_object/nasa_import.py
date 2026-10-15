from datetime import datetime


class Import:
    """
    Represents a database update task via the NASA API.
    Keeps track of the import status, date ranges, and data volume.

    Attributes:
        _user_id (int): The ID of the admin who triggered the import.
        _start_date (datetime): The start date/time of the data retrieval period.
        _end_date (datetime): The end date of the data/time retrieval period.
        _trigger_type (str): How the import was triggered ('manual' or 'auto').
        _status (str): The current status of the import ('running', 'success' or 'failed').
        _nb_calls (int): The number of API calls made during this import.
        _nb_neo (int): The number of Near-Earth Objects imported.
        _nb_approaches (int): The number of close approaches imported.
    """

    def __init__(
        self,
        user_id: int,
        start_date: datetime,
        end_date: datetime,
        trigger_type: str,
        status: str,
        nb_calls: int,
        nb_neo: int,
        nb_approaches: int,
    ):
        self._user_id = user_id
        self._start_date = start_date
        self._end_date = end_date
        self._trigger_type = trigger_type
        self._status = status
        self._nb_calls = nb_calls
        self._nb_neo = nb_neo
        self._nb_approaches = nb_approaches
