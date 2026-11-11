from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserCreateModel(BaseModel):
    """Schema for registering a new user."""

    username: str = Field(..., min_length=3, max_length=30)
    email: EmailStr
    password: str = Field(..., min_length=6)


class UserReadModel(BaseModel):
    """Schema for returning public user information."""

    user_id: int
    username: str
    email: EmailStr
    role: str
    creation_date: datetime | str | None = None


class UserLoginModel(BaseModel):
    """Schema for user login credentials."""

    username: str
    password: str


class Token(BaseModel):
    """Schema for authentication token response."""

    access_token: str
    refresh_token: str | None = None
    token_type: str = "bearer"
    user_id: int | None = None
    id_player: int | None = None  # Backward-compatibility for Streamlit UI
    username: str | None = None
    role: str | None = None


class TokenData(BaseModel):
    """Schema for data extracted from JWT token."""

    username: str | None = None
    user_id: int | None = None
    role: str | None = None


class RefreshTokenRequest(BaseModel):
    """Schema for token refresh request."""

    refresh_token: str
