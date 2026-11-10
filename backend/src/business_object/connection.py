from datetime import datetime


class Connection:
    """
    Class used for a connection
    Allows administrators to consult the activity history.

    Attributes:
        _connection_id (int): The unique identifier of the connection log.
        _user_id (int): The ID of the user who logged in.
<<<<<<< HEAD
        _connection_date (datetime): The exact date and time of the login.
    """

    def __init__(self, connection_id: int, user_id: int, connection_date: datetime):
        self._connection_id = connection_id
        self._user_id = user_id
        self._connection_date = connection_date
=======
        _date (datetime): The exact date and time of the login.
    """

    def __init__(self, connection_id: int, user_id: int, date: datetime):
        self._connection_id = connection_id
        self._user_id = user_id
        self._date = date or datetime.now()

    @property
    def connection_id(self) -> int | None:
        return self._connection_id

    @connection_id.setter
    def connection_id(self, value: int | None) -> None:
        self._connection_id = value

    @property
    def user_id(self) -> int:
        return self._user_id

    @user_id.setter
    def user_id(self, value: int) -> None:
        self._user_id = value

    @property
    def date(self) -> datetime:
        return self._date

    @date.setter
    def date(self, value: datetime) -> None:
        self._date = value

    def to_dict(self) -> dict:
        return {
            "connection_id": self._connection_id,
            "user_id": self._user_id,
            "date": (
                self._date.isoformat()
                if hasattr(self._date, "isoformat")
                else str(self._date)
            ),
        }
