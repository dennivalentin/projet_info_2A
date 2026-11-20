"""Authentication and user management controller for NEO-Watch.

Implements JWT login, OAuth2 password form flow, token refresh, user registration,
and profile retrieval following OAuth2/JWT best practices.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from business_object.user import User
from schema.user_model import (
    RefreshTokenRequest,
    Token,
    UserCreateModel,
    UserLoginModel,
    UserReadModel,
)
from service.user_service import UserService
from utils.log_utils import get_logger
from utils.security import get_current_user

router = APIRouter()
logger = get_logger(__name__)


def _token_response(user: User, access_token: str, refresh_token: str) -> Token:
    """Answer of the login and refresh endpoints: the two tokens and the user."""
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",  # nosec B106
        user_id=user.user_id,
        username=user.username,
        role=user.role,
    )


@router.post("/", response_model=Token, tags=["Login"])
def login(credentials: UserLoginModel):
    """Authenticates a user via JSON credentials and returns JWT tokens."""
    logger.info(f"Login attempt for: {credentials.username}")
    res = UserService().login(credentials.username, credentials.password)
    if res:
        user, access_token, refresh_token = res
        return _token_response(user, access_token, refresh_token)
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


@router.post("/token", response_model=Token, tags=["Login"])
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """OAuth2 password form login endpoint for Swagger UI and OAuth2 clients."""
    logger.info(f"OAuth2 form login attempt for: {form_data.username}")
    res = UserService().login(form_data.username, form_data.password)
    if res:
        user, access_token, refresh_token = res
        return _token_response(user, access_token, refresh_token)
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )


@router.post("/refresh", response_model=Token, tags=["Login"])
def refresh_token(body: RefreshTokenRequest):
    """Exchanges a valid refresh token for new tokens (the access token lasts 30 min)."""
    try:
        user, access_token, refresh_token = UserService().refresh(body.refresh_token)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        ) from e
    return _token_response(user, access_token, refresh_token)


@router.get("/me", response_model=UserReadModel, tags=["Login"])
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """Returns the profile of the currently authenticated user."""
    return UserReadModel.from_user(current_user)


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
        return UserReadModel.from_user(user)
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve)) from ve
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        ) from e
