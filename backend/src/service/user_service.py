import hmac

from fastapi import HTTPException

from business_object.connection import Connection
from business_object.user import User
from dao.connection_dao import ConnectionDao
from dao.user_dao import UserDao
from utils.log_utils import get_logger, log
from utils.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
)

logger = get_logger(__name__)


class UserService:
    """Business logic related to user accounts"""

    @log
    def create_account(self, username: str, email: str, password: str) -> User:
        """Creates a new account with the 'user' role.

        Args:
            username: The chosen username.
            email: The email address.
            password: The plain password.

        Returns:
            The created User object.
        """
        if UserDao().find_by_username(username):
            raise ValueError("The username is already used")
        elif UserDao().find_by_email(email):
            raise ValueError("The email is already used")

        new_user = User(
            user_id=None,
            username=username,
            email=email,
            password_hash=hash_password(password, username),
            creation_date=None,
            role="user",
        )

        if not UserDao().create(new_user):
            raise ValueError("Account creation failed")

        return UserDao().find_by_username(username)

    @log
    def login(self, username: str, password: str) -> tuple[User, str, str] | None:
        """Authenticates a user and records the connection.

        Args:
            username: The username.
            password: The plain password.

        Returns:
            Tuple of (User, access_token, refresh_token) if successful, None otherwise.
        """

        user = UserDao().find_by_username(username)
        if user is None:
            return None

        pwd_hash = hash_password(password, username)
        if not hmac.compare_digest(user.password_hash, pwd_hash):
            return None

        acc_tok, ref_tok = self._create_tokens(user)

        # The connection history is only informative: a failure must not block the login
        try:
            ConnectionDao().create(user.user_id, acc_tok)
        except Exception as e:
            logger.warning(f"Connection of user {user.user_id} not recorded: {e}")

        return user, acc_tok, ref_tok

    @log
    def refresh(self, refresh_token: str) -> tuple[User, str, str]:
        """Gives new tokens in exchange for a valid refresh token.

        Args:
            refresh_token: The refresh token received at login.

        Returns:
            Tuple of (User, access_token, refresh_token).

        Raises:
            ValueError: If the token is invalid, expired, not a refresh token,
                or if its user no longer exists.
        """
        try:
            payload = decode_token(refresh_token)
        except HTTPException:
            raise ValueError("Invalid or expired refresh token") from None

        if payload.get("type") != "refresh":
            raise ValueError("Invalid token type: refresh token expected")

        user = UserDao().find_by_username(payload.get("sub"))
        if user is None:
            raise ValueError("User not found")

        access_token, new_refresh_token = self._create_tokens(user)
        return user, access_token, new_refresh_token

    @staticmethod
    def _create_tokens(user: User) -> tuple[str, str]:
        """Creates the access token and the refresh token of a user."""
        payload = {
            "sub": user.username,
            "user_id": user.user_id,
            "role": user.role,
        }
        return create_access_token(payload), create_refresh_token(payload)

    @log
    def make_admin(self, user_id: int) -> bool:
        """Change the role from 'user' to 'admin'."""
        user = UserDao().find_by_id(user_id)
        if user is None:
            raise ValueError("The user could not be found")

        user.role = "admin"
        return UserDao().update(user)

    @log
    def delete_account(self, user_id: int) -> bool:
        """Delete a user account."""
        user = UserDao().find_by_id(user_id)
        if user is None:
            raise ValueError("The user could not be found")

        return UserDao().delete(user.user_id)

    @log
    def list_users(self) -> list[User]:
        """All the accounts, sorted by username (administration, F1)."""
        return UserDao().find_all()

    @log
    def connection_history(self, user_id: int) -> list[Connection]:
        """The logins of a user, latest first (administration, F1).

        Raises:
            ValueError: If the user does not exist.
        """
        if UserDao().find_by_id(user_id) is None:
            raise ValueError("The user could not be found")
        return ConnectionDao().find_by_user(user_id)
