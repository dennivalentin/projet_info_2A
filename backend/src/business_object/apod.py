from date import datetime


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
