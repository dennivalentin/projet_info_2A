from datetime import datetime


class Search:
    """Stores criteria and history for a user search.

    Kept for thirty days in the database to allow activity tracking.

    Attributes:
        _search_id (int | None): The unique identifier of the search record.
        _user_id (int): The ID of the user who performed the search.
        _search_date (datetime): The date and time of the search.
        _criteria (str): The search parameters or keywords used, as readable text.
        _neo_id (int | None): The ID of the NEO selected/viewed (if applicable).
    """

    def __init__(
        self,
        user_id: int = 1,
        criteria: str = "",
        search_date: datetime | None = None,
        neo_id: int | None = None,
        search_id: int | None = None,
    ):
        self._search_id = search_id
        self._user_id = user_id
        self._search_date = search_date or datetime.now()
        self._criteria = criteria
        self._neo_id = neo_id

    @property
    def search_id(self) -> int | None:
        return self._search_id

    @search_id.setter
    def search_id(self, value: int | None) -> None:
        self._search_id = value

    @property
    def user_id(self) -> int:
        return self._user_id

    @user_id.setter
    def user_id(self, value: int) -> None:
        self._user_id = value

    @property
    def search_date(self) -> datetime:
        return self._search_date

    @search_date.setter
    def search_date(self, value: datetime) -> None:
        self._search_date = value

    @property
    def criteria(self) -> str:
        return self._criteria

    @criteria.setter
    def criteria(self, value: str) -> None:
        self._criteria = value

    @property
    def neo_id(self) -> int | None:
        return self._neo_id

    @neo_id.setter
    def neo_id(self, value: int | None) -> None:
        self._neo_id = value

    def to_dict(self) -> dict:
        return {
            "search_id": self._search_id,
            "user_id": self._user_id,
            "search_date": self._search_date.isoformat() if hasattr(self._search_date, "isoformat") else str(self._search_date),
            "criteria": self._criteria,
            "neo_id": self._neo_id,
        }

    def __repr__(self) -> str:
        return f"<Search id={self._search_id} user={self._user_id} criteria='{self._criteria}'>"

    def __str__(self) -> str:
        return f"Search #{self._search_id} (User: {self._user_id}, Criteria: {self._criteria})"
