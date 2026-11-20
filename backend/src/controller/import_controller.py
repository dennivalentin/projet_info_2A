from fastapi import APIRouter, Depends, HTTPException, status

from service import import_scheduler
from service.import_service import ImportService
from utils.log_utils import get_logger
from utils.reset_database import ResetDatabase
from utils.security import get_current_user, require_admin

router = APIRouter(tags=["Database and Imports"])
logger = get_logger(__name__)


@router.post("/reset_database")
def reset_database_endpoint(current_user=Depends(require_admin)):
    """Reset the database (admin only, refused while a NASA import is running)"""
    if import_scheduler.is_running():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A NASA import is running: wait for its end before resetting",
        )
    try:
        ResetDatabase().run()
        return {"status": "success", "message": "Database reset successfully"}
    except Exception as e:
        logger.error(f"Error during database reset: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Reset failed: {str(e)}",
        ) from e


@router.post("/import/update")
def sync_data_endpoint(current_user=Depends(require_admin)):
    """Start the NASA update in the background (admin only, returns immediately).

    The same update also runs automatically every day (see import_scheduler).
    """
    try:
        started = import_scheduler.start_import(current_user.user_id, refresh=True)
    except Exception as e:
        logger.error(f"Error starting data sync: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Sync failed: {str(e)}",
        ) from e
    return {"status": "success", "result": {"status": "started" if started else "running"}}


@router.get("/import/status")
def get_import_status(current_user=Depends(get_current_user)):
    """Tell whether a NASA import is currently running."""
    return {"running": import_scheduler.is_running()}


@router.get("/import/last")
def get_last_import_endpoint(current_user=Depends(get_current_user)):
    """Return the last update date"""
    last_import = ImportService().find_last_import()
    if last_import is None:
        return {"last_end_date": None}
    return {"last_end_date": str(last_import.end_date)}
