from date import datetime


class Search:
    """
    Stores criteria for a search.

    Attributes:
        _search_id (int): The unique identifier of the search record.
        _user_id (int): The ID of the user who performed the search.
        _search_date (datetime): The date and time of the search.
        _criteria (str): The search parameters or keywords used.
        _neo_id (int): The ID of the NEO selected from the search results (if any).
    """
    def __init__(self, search_id: int, user_id: int, search_date: datetime, criteria: str, neo_id: int):
        self._search_id = search_id
        self._user_id = user_id
        self._search_date = search_date
        self._criteria = criteria
        self._neo_id = neo_id