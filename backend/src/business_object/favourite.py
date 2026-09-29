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
        self._date_added = date_added