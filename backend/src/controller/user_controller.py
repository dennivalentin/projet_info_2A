"""F1 - Administration of the user accounts: list, promote, delete, connection history.

Every route is reserved to administrators.
"""

from fastapi import APIRouter, Depends, HTTPException, status

from schema.user_model import UserReadModel
from service.user_service import UserService
from utils.log_utils import get_logger
from utils.security import require_admin

router = APIRouter(prefix="/users", tags=["Users (admin)"])
logger = get_logger(__name__)


@router.get("/", response_model=list[UserReadModel])
def list_users(admin=Depends(require_admin)):
    """List all the accounts."""
    return [UserReadModel.from_user(user) for user in UserService().list_users()]


@router.put("/{user_id}/admin")
def promote_to_admin(user_id: int, admin=Depends(require_admin)):
    """Give the administrator role to a user."""
    logger.info(f"Admin {admin.username} promotes user_id={user_id}")
    try:
        UserService().make_admin(user_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    return {"message": "User promoted to administrator"}


@router.delete("/{user_id}")
def delete_user(user_id: int, admin=Depends(require_admin)):
    """Delete an account (with its favourites, alerts and connections)."""
    if user_id == admin.user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot delete your own account",
        )
    logger.info(f"Admin {admin.username} deletes user_id={user_id}")
    try:
        UserService().delete_account(user_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    return {"message": "User deleted"}


@router.get("/{user_id}/connections")
def connection_history(user_id: int, admin=Depends(require_admin)):
    """Login history of a user, latest first."""
    try:
        connections = UserService().connection_history(user_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    return [connection.to_dict() for connection in connections]
