


"""Authentication and user management controller for NEO-Watch.

Implements JWT login, OAuth2 password form flow, token refresh, user registration,
and profile retrieval following OAuth2/JWT best practices.
"""

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

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
from utils.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_current_user,
    oauth2_scheme,
)

router = APIRouter()
logger = get_logger(__name__)


@router.post("/", response_model=Token, tags=["Login"])
def login(credentials: UserLoginModel):
    """Authenticates a user via JSON credentials and returns JWT tokens."""
    logger.info(f"Login attempt for: {credentials.username}")
    res = UserService().login(credentials.username, credentials.password)
    if res:
        user, access_token, refresh_token = res
        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            user_id=user.user_id,
            id_player=user.user_id,
            username=user.username,
            role=user.role,
        )
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
        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            user_id=user.user_id,
            id_player=user.user_id,
            username=user.username,
            role=user.role,
        )
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )


@router.post("/refresh", response_model=Token, tags=["Login"])
def refresh_token(
    request: Request,
    body: RefreshTokenRequest | None = None,
    bearer_token: str | None = Depends(oauth2_scheme),
    x_refresh_token: str | None = Header(None, alias="X-Refresh-Token"),
):
    """Exchanges a valid refresh token for a fresh access token."""
    raw_token = None
    if body and body.refresh_token:
        raw_token = body.refresh_token
    elif x_refresh_token:
        raw_token = x_refresh_token
    elif bearer_token:
        raw_token = bearer_token
    elif request:
        auth_header = request.headers.get("authorization") or request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            raw_token = auth_header[7:].strip()

    if not raw_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Refresh token required in request body or Authorization header",
        )

    try:
        payload = decode_token(raw_token)
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if payload.get("type") and payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type: refresh token expected",
            headers={"WWW-Authenticate": "Bearer"},
        )

    username = payload.get("sub") or payload.get("username")
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    from dao.user_dao import UserDao

    user = UserDao().find_by_username(username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    new_payload = {
        "sub": user.username,
        "user_id": user.user_id,
        "role": user.role,
    }
    new_access_token = create_access_token(new_payload)
    new_refresh_token = create_refresh_token(new_payload)

    return Token(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        user_id=user.user_id,
        id_player=user.user_id,
        username=user.username,
        role=user.role,
    )


@router.get("/me", response_model=UserReadModel, tags=["Login"])
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """Returns the profile of the currently authenticated user."""
    return UserReadModel(
        user_id=current_user.user_id,
        username=current_user.username,
        email=current_user.email,
        role=current_user.role,
        creation_date=current_user.creation_date,
    )


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
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )
