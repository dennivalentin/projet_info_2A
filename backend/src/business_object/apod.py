from datetime import datetime


class ApodData:
    """
    Class for the Picture of The Day provided by the NASA

    Attributes:
        title (str): The title of the astronomy picture.
        date (datetime): The publication date of the picture.
        caption (str): The description or explanation provided by NASA.
        url (str): The direct URL to the image resource.
    """

    def __init__(self, title: str, date: datetime, caption: str, url: str):
        self.title = title
        self.date = date
        self.caption = caption
        self.url = url

    @property
    def title(self) -> str:
        return self._title

    @title.setter
    def title(self, value: str) -> None:
        self._title = value

    @property
    def date(self) -> datetime:
        return self._date

    @date.setter
    def date(self, value: datetime) -> None:
        self._date = value

    @property
    def caption(self) -> str:
        return self._caption

    @caption.setter
    def caption(self, value: str) -> None:
        self._caption = value

    @property
    def url(self) -> str:
        return self._url

    @url.setter
    def url(self, value: str) -> None:
        self._url = value

    def to_dict(self) -> dict:
        return {
            "title": self._title,
            "date": (
                self._date.isoformat()
                if hasattr(self._date, "isoformat")
                else str(self._date)
            ),
            "caption": self._caption,
            "url": self._url,
        }

    def __repr__(self) -> str:
        return f"<ApodData title='{self._title}' date='{self._date}'>"
