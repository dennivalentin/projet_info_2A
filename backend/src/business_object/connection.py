from datetime import datetime


class Connection:
    """
    Class used for a connection
    Allows administrators to consult the activity history.

    Attributes:
        _connection_id (int): The unique identifier of the connection log.
        _user_id (int): The ID of the user who logged in.
        _connection_date (datetime): The exact date and time of the login.
    """

    def __init__(self, connection_id: int, user_id: int, connection_date: datetime):
        self._connection_id = connection_id
        self._user_id = user_id
        self._connection_date = connection_date
