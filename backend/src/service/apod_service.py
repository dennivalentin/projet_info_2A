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


class ApodService:
    """Gets NASA's picture of the day so the user can view and export it."""

    @log
    def get_picture_of_the_day(self, day: date | None = None) -> ApodData:
        """Return the APOD of `day` (today if None)."""
        params = {"api_key": os.getenv("NASA_API_KEY", "DEMO_KEY")}
        if day is not None:
            params["date"] = day.strftime("%Y-%m-%d")

        response = requests.get(APOD_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        return ApodData(
            title=data.get("title", ""),
            date=datetime.strptime(data["date"], "%Y-%m-%d"),
            caption=data.get("explanation", ""),
            url=data.get("url", ""),
        )
