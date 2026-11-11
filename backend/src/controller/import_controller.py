from fastapi import APIRouter, Depends, HTTPException, status
from service.import_service import ImportService
from dao.import_dao import ImportDao
from utils.security import get_current_user, require_admin
from utils.log_utils import get_logger

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
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Reset failed: {str(e)}",)


@router.post("/import/update")
def sync_data_endpoint(current_user=Depends(get_current_user)):
    """Run the database update"""
    try:
        service = ImportService()
        result = service.import_update(user_id=current_user.user_id)
        return {"status": "success", "result": result}
    except Exception as e:
        logger.error(f"Error during data sync: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Sync failed: {str(e)}",
        )


@router.get("/import/last")
def get_last_import_endpoint(current_user=Depends(get_current_user)):
    """Return the last update date"""
    task = ImportDao().find_last_successful_import()
    if not task:
        return {"last_end_date": None}
    return {"last_end_date": str(task._end_date)}