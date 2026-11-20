"""F2 - Dashboard endpoint: GET /dashboard"""

from datetime import date

from fastapi import APIRouter, Depends, HTTPException

from service.dashboard_service import DashboardService
from utils.security import get_current_user

router = APIRouter()


@router.get("/", tags=["Dashboard"])
def get_dashboard(
    start: date | None = None,
    end: date | None = None,
    user=Depends(get_current_user),
):
    """Dashboard of the connected user (default period: next 7 days)."""
    user_id = user.user_id
    try:
        return DashboardService().get_dashboard(user_id, start, end)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
