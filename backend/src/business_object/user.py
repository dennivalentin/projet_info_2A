from date import datetime


class User:
    """
    Class describing a user of the app

    Attributes:
        _user_id (int): The unique identifier of the user.
        _username (str): The username chosen by the user.
        _email (str): The email address associated with the account.
        _password_hash (str): The hashed password.
        _creation_date (datetime): The date and time the account was created.
        _role (str): The authorization level ('regular', 'admin').
    """

    def __init__(
        self,
        user_id: int,
        username: str,
        email: str,
        password_hash: str,
        creation_date: datetime,
        role: str,
    ):
        self._user_id = user_id
        self._username = username
        self._email = email
        self._password_hash = password_hash
        self._creation_date = creation_date
        self._role = role
