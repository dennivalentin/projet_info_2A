"""FO3 - Statistics endpoint: GET /statistics"""

from fastapi import APIRouter, Depends

from service.statistics_service import StatisticsService
from utils.security import verify_token

router = APIRouter()


@router.get("/", tags=["Statistics"])
def get_statistics(user=Depends(verify_token)):
    """Statistics on NEOs and their approaches (logged-in users only)."""
    return StatisticsService().get_statistics()
