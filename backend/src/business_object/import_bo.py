from datetime import date, datetime


class Import:
    """Represents a database update task via the NASA API.

    Keeps track of import status, date ranges, and volume of data fetched.

    Attributes:
        _import_id (int | None): Unique identifier of the import log.
        _user_id (int | None): The ID of the admin who triggered the import.
        _start_date (datetime | date): Start date/time of the data retrieval period.
        _end_date (datetime | date): End date/time of the data retrieval period.
        _trigger_type (str): Trigger mode ('MANUAL' or 'BATCH').
        _status (str): Current status ('ON GOING', 'DONE', 'PARTIAL', 'FAIL').
        _nb_calls (int): Number of API calls made.
        _nb_neo (int): Number of Near-Earth Objects inserted or updated.
        _nb_approaches (int): Number of close approaches inserted or updated.
    """

    def __init__(
        self,
        start_date: datetime | date,
        end_date: datetime | date,
        user_id: int | None = None,
        trigger_type: str = "MANUAL",
        status: str = "ON GOING",
        nb_calls: int = 0,
        nb_neo: int = 0,
        nb_approaches: int = 0,
        import_id: int | None = None,
    ):
        self._import_id = import_id
        self._user_id = user_id
        self._start_date = start_date
        self._end_date = end_date
        self._trigger_type = trigger_type
        self._status = status
        self._nb_calls = nb_calls
        self._nb_neo = nb_neo
        self._nb_approaches = nb_approaches

    @property
    def import_id(self) -> int | None:
        return self._import_id

    @import_id.setter
    def import_id(self, value: int | None) -> None:
        self._import_id = value

    @property
    def user_id(self) -> int | None:
        return self._user_id

    @user_id.setter
    def user_id(self, value: int | None) -> None:
        self._user_id = value

    @property
    def start_date(self) -> datetime | date:
        return self._start_date

    @start_date.setter
    def start_date(self, value: datetime | date) -> None:
        self._start_date = value

    @property
    def end_date(self) -> datetime | date:
        return self._end_date

    @end_date.setter
    def end_date(self, value: datetime | date) -> None:
        self._end_date = value

    @property
    def trigger_type(self) -> str:
        return self._trigger_type

    @trigger_type.setter
    def trigger_type(self, value: str) -> None:
        self._trigger_type = value

    @property
    def status(self) -> str:
        return self._status

    @status.setter
    def status(self, value: str) -> None:
        self._status = value

    @property
    def nb_calls(self) -> int:
        return self._nb_calls

    @nb_calls.setter
    def nb_calls(self, value: int) -> None:
        self._nb_calls = int(value)

    @property
    def nb_neo(self) -> int:
        return self._nb_neo

    @nb_neo.setter
    def nb_neo(self, value: int) -> None:
        self._nb_neo = int(value)

    @property
    def nb_approaches(self) -> int:
        return self._nb_approaches

    @nb_approaches.setter
    def nb_approaches(self, value: int) -> None:
        self._nb_approaches = int(value)

    def to_dict(self) -> dict:
        return {
            "import_id": self._import_id,
            "user_id": self._user_id,
            "start_date": (
                self._start_date.isoformat()
                if hasattr(self._start_date, "isoformat")
                else str(self._start_date)
            ),
            "end_date": (
                self._end_date.isoformat()
                if hasattr(self._end_date, "isoformat")
                else str(self._end_date)
            ),
            "trigger_type": self._trigger_type,
            "status": self._status,
            "nb_calls": self._nb_calls,
            "nb_neo": self._nb_neo,
            "nb_approaches": self._nb_approaches,
        }

    def __repr__(self) -> str:
        return f"<Import id={self._import_id} status='{self._status}' calls={self._nb_calls} neos={self._nb_neo}>"

    def __str__(self) -> str:
        return f"Import #{self._import_id} [{self._status}] ({self._start_date} -> {self._end_date})"
