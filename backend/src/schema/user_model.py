from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from business_object.user import User


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

    @classmethod
    def from_user(cls, user: User) -> "UserReadModel":
        """Public information of a user (never the password hash).

        Raises:
            ValueError: If the user is not saved in the database yet (no id).
        """
        if user.user_id is None:
            raise ValueError("The user is not saved in the database")
        return cls(
            user_id=user.user_id,
            username=user.username,
            email=user.email,
            role=user.role,
            creation_date=user.creation_date,
        )


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
    username: str | None = None
    role: str | None = None


class RefreshTokenRequest(BaseModel):
    """Schema for token refresh request."""

    refresh_token: str
