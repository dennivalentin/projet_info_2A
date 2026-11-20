"""FO3 - Statistics endpoint: GET /statistics"""

from fastapi import APIRouter, Depends

from service.statistics_service import StatisticsService
from utils.security import get_current_user

router = APIRouter()


@router.get("/", tags=["Statistics"])
def get_statistics(user=Depends(get_current_user)):
    """Statistics on NEOs and their approaches (logged-in users only)."""
    return StatisticsService().get_statistics()
