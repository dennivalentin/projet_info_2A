"""FO8 - Picture of the day endpoint: GET /apod"""

from datetime import date

import requests
from fastapi import APIRouter, Depends, HTTPException

from service.apod_service import ApodService
from utils.security import verify_token

router = APIRouter()


@router.get("/", tags=["APOD"])
def get_apod(day: date | None = None, user=Depends(verify_token)):
    """NASA's picture of the day (today, or `day`) - logged-in users only."""
    try:
        return ApodService().get_picture_of_the_day(day).to_dict()
    except requests.RequestException as e:
        # NASA down or rate limit reached (429) -> clear error instead of a crash
        raise HTTPException(status_code=503, detail=f"NASA APOD unavailable: {e}")
