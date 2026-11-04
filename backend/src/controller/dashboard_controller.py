"""F2 - Dashboard endpoint: GET /dashboard"""

from datetime import date

from fastapi import APIRouter, Depends, HTTPException

from service.dashboard_service import DashboardService
from utils.security import verify_token

router = APIRouter()


@router.get("/", tags=["Dashboard"])
def get_dashboard(
    start: date | None = None,
    end: date | None = None,
    user=Depends(verify_token),
):
    """Dashboard of the connected user (default period: next 7 days)."""
    # verify_token gives back the connected user (User after Sofia's F1, Player before)
    user_id = getattr(user, "user_id", None) or user.id_player
    try:
        return DashboardService().get_dashboard(user_id, start, end)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
