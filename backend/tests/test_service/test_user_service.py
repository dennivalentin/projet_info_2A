"""Unit tests of UserService (the DAOs are mocked: no database needed)."""

from unittest.mock import MagicMock, patch

import pytest

from business_object.user import User
from service.user_service import UserService
from utils.security import decode_token, hash_password

ALICE = User(
    user_id=2,
    username="alice",
    email="alice@ensai.fr",
    password_hash=hash_password("alice_password", "alice"),
    role="user",
)


@pytest.fixture
def user_dao():
    """Replaces UserDao and ConnectionDao with mocks."""
    with (
        patch("service.user_service.UserDao") as user_dao_class,
        patch("service.user_service.ConnectionDao"),
    ):
        mock = MagicMock()
        user_dao_class.return_value = mock
        yield mock


def test_create_account_ok(user_dao):
    # GIVEN: the username and the email are free
    user_dao.find_by_username.side_effect = [None, ALICE]
    user_dao.find_by_email.return_value = None
    user_dao.create.return_value = True
    # WHEN
    user = UserService().create_account("alice", "alice@ensai.fr", "alice_password")
    # THEN: the password is stored hashed (salted with the username), with role "user"
    created = user_dao.create.call_args.args[0]
    assert created.password_hash == hash_password("alice_password", "alice")
    assert created.role == "user"
    assert user.username == "alice"


def test_create_account_username_already_used(user_dao):
    user_dao.find_by_username.return_value = ALICE
    with pytest.raises(ValueError, match="username"):
        UserService().create_account("alice", "other@ensai.fr", "pwd")
    user_dao.create.assert_not_called()


def test_create_account_email_already_used(user_dao):
    user_dao.find_by_username.return_value = None
    user_dao.find_by_email.return_value = ALICE
    with pytest.raises(ValueError, match="email"):
        UserService().create_account("alice2", "alice@ensai.fr", "pwd")


def test_create_account_dao_failure(user_dao):
    user_dao.find_by_username.return_value = None
    user_dao.find_by_email.return_value = None
    user_dao.create.return_value = False
    with pytest.raises(ValueError, match="creation failed"):
        UserService().create_account("bob", "bob@ensai.fr", "pwd")


def test_login_ok_returns_valid_tokens(user_dao):
    user_dao.find_by_username.return_value = ALICE

    user, access_token, refresh_token = UserService().login("alice", "alice_password")

    assert user.user_id == 2
    assert decode_token(access_token)["sub"] == "alice"
    assert decode_token(refresh_token)["type"] == "refresh"


def test_login_wrong_password(user_dao):
    user_dao.find_by_username.return_value = ALICE
    assert UserService().login("alice", "wrong") is None


def test_login_unknown_user(user_dao):
    user_dao.find_by_username.return_value = None
    assert UserService().login("nobody", "whatever") is None


def test_make_admin_unknown_user(user_dao):
    user_dao.find_by_id.return_value = None
    with pytest.raises(ValueError):
        UserService().make_admin(42)


def test_connection_history_of_unknown_user(user_dao):
    user_dao.find_by_id.return_value = None
    with pytest.raises(ValueError):
        UserService().connection_history(42)


def test_list_users(user_dao):
    user_dao.find_all.return_value = [ALICE]
    assert UserService().list_users() == [ALICE]


def test_refresh_gives_new_tokens(user_dao):
    # GIVEN: alice logged in
    user_dao.find_by_username.return_value = ALICE
    _, _, refresh_token = UserService().login("alice", "alice_password")

    # WHEN
    user, access_token, _ = UserService().refresh(refresh_token)

    # THEN
    assert user.username == "alice"
    assert decode_token(access_token)["type"] == "access"


def test_refresh_refuses_an_access_token(user_dao):
    user_dao.find_by_username.return_value = ALICE
    _, access_token, _ = UserService().login("alice", "alice_password")

    with pytest.raises(ValueError, match="refresh token expected"):
        UserService().refresh(access_token)


def test_refresh_refuses_an_invalid_token(user_dao):
    with pytest.raises(ValueError, match="Invalid or expired"):
        UserService().refresh("not.a.token")
