"""Security utilities: password hashing, JWT generation, decoding, and FastAPI dependencies."""

import hashlib
import hmac
import os
from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from fastapi import Depends, Header, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer

from business_object.user import User


def _secret_key() -> str:
    key = os.getenv("JWT_SECRET_KEY")
    if not key:
        raise RuntimeError("JWT_SECRET_KEY  missing in .env")
    return key


def _algorithm() -> str:
    return os.getenv("JWT_ALGORITHM", "HS256")


ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login/token", auto_error=False)


def hash_password(password: str, salt: str = "") -> str:
    """Hashes a password using the SHA-256 algorithm.

    Args:
        password (str): The plain text password to be hashed.
        salt (str, optional): A string added to the password before hashing
            to protect against rainbow table attacks.

    Returns:
        str: The resulting hexadecimal hash string.
    """
    password_bytes = password.encode("utf-8") + salt.encode("utf-8")
    hash_object = hashlib.sha256(password_bytes)
    return hash_object.hexdigest()


def verify_password(plain_password: str, hashed_password: str, salt: str = "") -> bool:
    """Verifies a plain password against its SHA-256 hash.

    Args:
        plain_password (str): The plain text password.
        hashed_password (str): The expected hash.
        salt (str, optional): The salt used during hashing.

    Returns:
        bool: True if passwords match, False otherwise.
    """
    computed = hash_password(plain_password, salt)
    return hmac.compare_digest(computed, hashed_password)


def create_access_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
    """Generates a signed JWT access token.

    Args:
        data (dict): Payload data to encode in the token.
        expires_delta (timedelta, optional): Custom expiration duration.

    Returns:
        str: Encoded JWT string.
    """
    to_encode = data.copy()
    expire = datetime.now(UTC) + (
        expires_delta
        if expires_delta is not None
        else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update(
        {
            "exp": expire,
            "iat": datetime.now(UTC),
            "type": "access",
        }
    )
    return jwt.encode(to_encode, _secret_key(), algorithm=_algorithm())


def create_refresh_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
    """Generates a signed JWT refresh token.

    Args:
        data (dict): Payload data to encode in the token.
        expires_delta (timedelta, optional): Custom expiration duration.

    Returns:
        str: Encoded JWT string.
    """
    to_encode = data.copy()
    expire = datetime.now(UTC) + (
        expires_delta if expires_delta is not None else timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    )
    to_encode.update(
        {
            "exp": expire,
            "iat": datetime.now(UTC),
            "type": "refresh",
        }
    )
    return jwt.encode(to_encode, _secret_key(), algorithm=_algorithm())


def decode_token(token: str) -> dict[str, Any]:
    """Decodes and validates a JWT token signature and expiration.

    Args:
        token (str): The JWT string to decode.

    Returns:
        dict: The decoded token payload.

    Raises:
        HTTPException: 401 if token is expired or invalid.
    """
    try:
        payload = jwt.decode(token, _secret_key(), algorithms=[_algorithm()])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user(
    token_or_request: Any = None,
    bearer_token: str | None = Depends(oauth2_scheme),
    x_auth_token: str | None = Header(None, alias="X-Auth-Token"),
) -> User:
    """Authenticates the current user via JWT Bearer or legacy X-Auth-Token header.

    Args:
        token_or_request (Any): FastAPI Request or raw token passed directly.
        bearer_token (str | None): Token from Authorization: Bearer header.
        x_auth_token (str | None): Token from X-Auth-Token header.

    Returns:
        User: Authenticated user object.

    Raises:
        HTTPException: 401 if missing, invalid, or expired.
    """
    token = None

    if isinstance(token_or_request, str) and token_or_request:
        token = token_or_request
    elif bearer_token:
        token = bearer_token
    elif x_auth_token:
        token = x_auth_token
    elif isinstance(token_or_request, Request):
        auth_header = token_or_request.headers.get("authorization") or token_or_request.headers.get(
            "Authorization"
        )
        if auth_header:
            parts = auth_header.split(" ")
            if len(parts) == 2 and parts[0].lower() == "bearer":
                token = parts[1]
            elif len(parts) == 1:
                token = parts[0]
        if not token:
            token = token_or_request.headers.get("x-auth-token") or token_or_request.headers.get(
                "X-Auth-Token"
            )

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # If token starts with 'Bearer ', clean it up
    if token.startswith("Bearer "):
        token = token[7:].strip()

    # Try decoding JWT
    is_jwt = False
    try:
        payload = decode_token(token)
        is_jwt = True
    except HTTPException:
        # Could be an expired JWT or an invalid token
        payload = None

    if is_jwt and payload:
        if payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type: access token expected",
                headers={"WWW-Authenticate": "Bearer"},
            )

        username = payload.get("sub") or payload.get("username")
        if not username:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Retrieve user from database: a deleted user must not stay logged in
        from dao.user_dao import UserDao

        user = UserDao().find_by_username(username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return user

    # Fallback for legacy opaque tokens stored in DB
    try:
        from dao.user_dao import UserDao

        user = UserDao().find_by_token(token)
        if user:
            return user
    except Exception:
        pass

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid token",
        headers={"WWW-Authenticate": "Bearer"},
    )


# Backward compatibility alias
verify_token = get_current_user


def require_role(required_role: str):
    """Dependency factory checking that the current user has the required role."""

    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Forbidden: '{required_role}' role required",
            )
        return current_user

    return role_checker


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Dependency verifying that the current user is an administrator."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: Admin privileges required",
        )
    return current_user


def check_same_user(current_user: User, user_id: int) -> None:
    """Forbids a user to read or change the data of another user (admins can).

    Raises:
        HTTPException: 403 if current_user is neither the owner nor an admin.
    """
    if current_user.role != "admin" and current_user.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: you can only access your own data",
        )
