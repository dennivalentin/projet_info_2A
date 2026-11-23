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

    @property
    def image_available(self) -> bool:
        """True when NASA gave the media of the day (False: only the description is known)."""
        return bool(self._url)

    @property
    def nasa_page_url(self) -> str:
        """Page of this picture on NASA's APOD website (one page per day)."""
        return f"https://apod.nasa.gov/apod/ap{self._date:%y%m%d}.html"

    def to_dict(self) -> dict:
        """Returns the object as a dict (JSON-friendly) for the API responses."""
        return {
            "title": self._title,
            "date": (
                self._date.isoformat() if hasattr(self._date, "isoformat") else str(self._date)
            ),
            "caption": self._caption,
            "url": self._url,
            "image_available": self.image_available,
            "nasa_page_url": self.nasa_page_url,
        }

    def __repr__(self) -> str:
        return f"<ApodData title='{self._title}' date='{self._date}'>"
