from date import datetime


class Favourite:
    """
    Class making the link between a user and one of his favourite NEO

    Attributes:
        _neo_id (int): The ID of the favorited NEO.
        _user_id (int): The ID of the user.
        _date_added (datetime): The date and time the NEO was added to favorites.
    """

    def __init__(self, neo_id: int, user_id: int, date_added: datetime):
        self._neo_id = neo_id
        self._user_id = user_id
        self._date_added = date_added or datetime.now()


  @property
    def neo_id(self) -> int:
        return self._neo_id
    @neo_id.setter
    def neo_id(self, value: int) -> None:
        self._neo_id = value
    @property
    def user_id(self) -> int:
        return self._user_id
    @user_id.setter
    def user_id(self, value: int) -> None:
        self._user_id = value
    @property
    def date_added(self) -> datetime:
        return self._date_added
    @date_added.setter
    def date_added(self, value: datetime) -> None:
        self._date_added = value
    def to_dict(self) -> dict:
        return {
            "neo_id": self._neo_id,
            "user_id": self._user_id,
            "date_added": self._date_added.isoformat() if hasattr(self._date_added, "isoformat") else str(self._date_added),
        }
    def __repr__(self) -> str:
        return f"<Favourite user={self._user_id} neo={self._neo_id} date='{self._date_added}'>"
    def __str__(self) -> str:
        return f"Favourite: User {self._user_id} -> NEO {self._neo_id}"
