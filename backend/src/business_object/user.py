from datetime import datetime


class User:
    """
    Class describing a user of the app

    Attributes:
        _user_id (int): The unique identifier of the user.
        _username (str): The username chosen by the user.
        _email (str): The email address associated with the account.
        _password_hash (str): The hashed password.
        _creation_date (datetime): The date and time the account was created.
        _role (str): The authorization level ('user' or 'admin').
    """

    def __init__(
        self,
        user_id: int | None,
        username: str,
        email: str,
        password_hash: str,
        creation_date: datetime | None,
        role: str,
    ):
        self._user_id = user_id
        self._username = username
        self._email = email
        self._password_hash = password_hash
        self._creation_date = creation_date
        self._role = role

    def __str__(self) -> str:
        """Readable representation of user

        Returns:
            str: the id, username and role of the user
        """
        return f"user id={self._user_id}, username={self._username}, role={self._role})"

    @property
    def user_id(self) -> int | None:
        return self._user_id

    @property
    def username(self) -> str:
        return self._username

    @property
    def email(self) -> str:
        return self._email

    @property
    def password_hash(self) -> str:
        return self._password_hash

    @property
    def creation_date(self) -> datetime | None:
        return self._creation_date

    @property
    def role(self) -> str:
        return self._role
