from fastapi import APIRouter, HTTPException

from schema.user_model import UserCreateModel, UserLoginModel, UserReadModel
from service.user_service import UserService
from utils.log_utils import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.post("/", tags=["Login"])
def login(credentials: UserLoginModel):
    """Authenticates a user and generates a session token."""
    logger.info(f"Login attempt for: {credentials.username}")
    res = UserService().login(credentials.username, credentials.password)
    if res:
        user, token = res
        return {
            "user_id": user.user_id,
            "id_player": user.user_id,  # For backward-compatibility with UI
            "username": user.username,
            "role": user.role,
            "access_token": token,
        }
    raise HTTPException(status_code=401, detail="Invalid credentials")


@router.post("/register", response_model=UserReadModel, tags=["Login"])
def register(user_in: UserCreateModel):
    """Registers a new user account."""
    logger.info(f"Registration attempt for: {user_in.username}")
    try:
        user = UserService().create_account(
            username=user_in.username,
            email=user_in.email,
            password=user_in.password,
        )
        return UserReadModel(
            user_id=user.user_id,
            username=user.username,
            email=user.email,
            role=user.role,
            creation_date=user.creation_date,
        )
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
