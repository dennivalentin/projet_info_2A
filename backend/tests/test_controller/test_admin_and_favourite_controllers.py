"""Controller tests: administration routes (F1), NASA import trigger and favourites.

The services are mocked and the logged-in user is replaced with
app.dependency_overrides: no database, no NASA call.
"""

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from business_object.connection import Connection
from business_object.user import User
from main import app
from utils.security import get_current_user

client = TestClient(app)

ADMIN = User(user_id=1, username="admin", email="admin@email.fr", role="admin")
ALICE = User(user_id=2, username="alice", email="alice@ensai.fr", role="user")


@pytest.fixture
def login_as():
    """login_as(user): every request is made by this user."""

    def _login(user):
        app.dependency_overrides[get_current_user] = lambda: user

    yield _login
    app.dependency_overrides.clear()


def test_admin_routes_are_forbidden_to_users(login_as):
    login_as(ALICE)
    assert client.get("/users/").status_code == 403
    assert client.put("/users/3/admin").status_code == 403
    assert client.delete("/users/3").status_code == 403
    assert client.get("/users/3/connections").status_code == 403
    assert client.post("/import/update").status_code == 403


@patch("controller.user_controller.UserService")
def test_admin_lists_users(user_service, login_as):
    login_as(ADMIN)
    user_service.return_value.list_users.return_value = [ADMIN, ALICE]

    res = client.get("/users/")

    assert res.status_code == 200
    assert [user["username"] for user in res.json()] == ["admin", "alice"]
    assert "password_hash" not in res.json()[0]


@patch("controller.user_controller.UserService")
def test_admin_promotes_a_user(user_service, login_as):
    login_as(ADMIN)
    assert client.put("/users/2/admin").status_code == 200
    user_service.return_value.make_admin.assert_called_once_with(2)


@patch("controller.user_controller.UserService")
def test_promote_unknown_user_gives_404(user_service, login_as):
    login_as(ADMIN)
    user_service.return_value.make_admin.side_effect = ValueError("The user could not be found")
    assert client.put("/users/42/admin").status_code == 404


@patch("controller.user_controller.UserService")
def test_admin_cannot_delete_own_account(user_service, login_as):
    login_as(ADMIN)
    assert client.delete("/users/1").status_code == 400
    user_service.return_value.delete_account.assert_not_called()


@patch("controller.user_controller.UserService")
def test_admin_reads_connection_history(user_service, login_as):
    login_as(ADMIN)
    user_service.return_value.connection_history.return_value = [
        Connection(connection_id=7, user_id=2, date=None)
    ]
    res = client.get("/users/2/connections")
    assert res.status_code == 200
    assert res.json()[0]["connection_id"] == 7


@patch("controller.import_controller.import_scheduler")
def test_admin_starts_the_nasa_update(scheduler, login_as):
    login_as(ADMIN)
    scheduler.start_import.return_value = False  # one is already running
    res = client.post("/import/update")
    assert res.json()["result"]["status"] == "running"
    scheduler.start_import.assert_called_once_with(1, refresh=True)


@patch("controller.import_controller.import_scheduler")
def test_reset_is_refused_during_an_import(scheduler, login_as):
    login_as(ADMIN)
    scheduler.is_running.return_value = True
    assert client.post("/reset_database").status_code == 409


@patch("controller.favourite_controller.FavouriteService")
def test_add_unknown_neo_to_favourites_gives_404(favourite_service, login_as):
    login_as(ALICE)
    favourite_service.return_value.add_favourite.side_effect = ValueError("NEO 9999 not found")
    res = client.post("/favourites/", json={"user_id": 2, "neo_id": 9999})
    assert res.status_code == 404


@patch("controller.favourite_controller.FavouriteService")
def test_add_favourite_twice_gives_409(favourite_service, login_as):
    login_as(ALICE)
    favourite_service.return_value.add_favourite.return_value = False
    assert client.post("/favourites/", json={"user_id": 2, "neo_id": 1}).status_code == 409
