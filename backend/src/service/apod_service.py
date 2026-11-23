"""Service for FO8: NASA Astronomy Picture of the Day (APOD)."""

import os
from datetime import date, datetime

import requests
from dotenv import load_dotenv

from business_object.apod import ApodData
from utils.log_utils import get_logger, log

load_dotenv()
logger = get_logger(__name__)

APOD_URL = "https://api.nasa.gov/planetary/apod"

# Since the APOD website moved to science.nasa.gov, the NASA API sometimes answers
# with the logo of the website and the title "NASA Science" instead of the picture
# of the day (the description is still the right one).
NASA_PLACEHOLDER_TITLE = "NASA Science"
NASA_PLACEHOLDER_IMAGE = "nasa-logo"


def _is_placeholder(data: dict) -> bool:
    """True when NASA answered with its generic logo instead of the picture of the day."""
    return (
        NASA_PLACEHOLDER_IMAGE in data.get("url", "")
        or data.get("title", "").strip() == NASA_PLACEHOLDER_TITLE
    )


class ApodService:
    """Gets NASA's picture of the day so the user can view and export it."""

    @log
    def get_picture_of_the_day(self, day: date | None = None) -> ApodData:
        """Returns the APOD of `day` (today if None).

        When NASA answers with its generic logo instead of the picture of the day,
        the title and the media URL are left empty (see ApodData.image_available).

        Raises:
            requests.RequestException: If NASA is unreachable or answers an error.
        """
        params = {"api_key": os.getenv("NASA_API_KEY", "DEMO_KEY")}
        if day is not None:
            params["date"] = day.strftime("%Y-%m-%d")

        response = requests.get(APOD_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if _is_placeholder(data):
            # Do not show the NASA logo as if it were the picture of the day:
            # no title and no media, the page links to NASA's website instead
            logger.warning(f"NASA gave no picture for {data.get('date')}")
            data = {**data, "title": "", "url": ""}

        return ApodData(
            title=data.get("title", ""),
            date=datetime.strptime(data["date"], "%Y-%m-%d"),
            caption=data.get("explanation", ""),
            url=data.get("url", ""),
        )
