import threading

from fastapi import APIRouter, Depends, HTTPException, status

from dao.import_dao import ImportDao
from service.import_service import ImportService
from utils.log_utils import get_logger
from utils.security import get_current_user, require_admin

router = APIRouter(tags=["Database and Imports"])
logger = get_logger(__name__)


@router.post("/reset_database")
def reset_database_endpoint(current_user=Depends(require_admin)):
    """Reset the database (admin only)"""
    try:
        service = ImportService()
        service.reset_database()
        return {"status": "success", "message": "Database reset successfully"}
    except Exception as e:
        logger.error(f"Error during database reset: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Reset failed: {str(e)}",
        )


# Only one NASA import at a time: the first import covers 3 years
# (~140 API calls, much longer than any HTTP timeout), so it runs in the background.
_import_lock = threading.Lock()


def _run_import_in_background(user_id: int) -> None:
    try:
        result = ImportService().import_update(user_id=user_id)
        logger.info(f"Background import finished: {result}")
    except Exception as e:
        logger.error(f"Error during data sync: {e}")
    finally:
        _import_lock.release()


@router.post("/import/update")
def sync_data_endpoint(current_user=Depends(get_current_user)):
    """Start the database update in the background (returns immediately)."""
    if not _import_lock.acquire(blocking=False):
        return {"status": "success", "result": {"status": "running"}}

    try:
        threading.Thread(
            target=_run_import_in_background,
            args=(current_user.user_id,),
            daemon=True,
        ).start()
    except Exception as e:
        _import_lock.release()
        logger.error(f"Error starting data sync: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Sync failed: {str(e)}",
        )
    return {"status": "success", "result": {"status": "started"}}


@router.get("/import/status")
def get_import_status(current_user=Depends(get_current_user)):
    """Tell whether a NASA import is currently running."""
    return {"running": _import_lock.locked()}


@router.get("/import/last")
def get_last_import_endpoint(current_user=Depends(get_current_user)):
    """Return the last update date"""
    task = ImportDao().find_last_successful_import()
    if not task:
        return {"last_end_date": None}
    return {"last_end_date": str(task._end_date)}
