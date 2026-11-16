"""DAO tests on the test database (schema project_test_dao, data/pop_db_test.sql).

Seed data used here:
- users 999 "admin_test" and 998 "user_test"
- NEOs 999 "Test Asteroid 1" (hazardous) and 998 "Test Asteroid 2",
  each with one approach in the next days

Each test that writes data removes it at the end, so the tests stay independent.
"""

from datetime import date, datetime, timedelta

import psycopg2.errors
import pytest

from business_object.approach import Approach
from business_object.import_bo import Import
from business_object.neo import Neo
from business_object.user import User
from dao.approach_dao import ApproachDao
from dao.connection_dao import ConnectionDao
from dao.favourite_dao import FavouriteDao
from dao.import_dao import ImportDao
from dao.neo_dao import NeoDao
from dao.user_dao import UserDao

pytestmark = pytest.mark.usefixtures("test_database")

TEST_USER_ID = 998
TEST_NEO_ID = 999


# ---------------------------------------------------------------- UserDao


def test_find_user_by_username_and_email():
    assert UserDao().find_by_username("user_test").user_id == TEST_USER_ID
    assert UserDao().find_by_email("user_test@email.fr").username == "user_test"


def test_find_unknown_user_returns_none():
    assert UserDao().find_by_username("nobody") is None
    assert UserDao().find_by_id(123456) is None


def test_create_update_and_delete_user():
    # GIVEN a new user
    user = User(username="pytest_user", email="pytest@ensai.fr", password_hash="h")
    # WHEN / THEN
    assert UserDao().create(user) is True
    created = UserDao().find_by_username("pytest_user")
    created.role = "admin"
    assert UserDao().update(created) is True
    assert UserDao().find_by_id(created.user_id).role == "admin"
    assert UserDao().delete(created.user_id) is True
    assert UserDao().find_by_username("pytest_user") is None


def test_create_user_with_an_existing_username_fails():
    duplicate = User(username="user_test", email="other@ensai.fr", password_hash="h")
    with pytest.raises(psycopg2.errors.UniqueViolation):
        UserDao().create(duplicate)


def test_find_all_users_is_sorted_by_username():
    usernames = [u.username for u in UserDao().find_all()]
    assert usernames == sorted(usernames)
    assert "admin_test" in usernames


# ---------------------------------------------------------------- NeoDao


def test_find_neo_by_id():
    neo = NeoDao().find_by_id(TEST_NEO_ID)
    assert neo.name == "Test Asteroid 1"
    assert neo.hazardous is True


def test_search_neos_by_name_and_hazard():
    found = NeoDao().find({"name": "test asteroid", "hazardous": True})
    assert [n.neo_id for n in found] == [TEST_NEO_ID]


def test_search_neos_by_approach_period():
    found = NeoDao().find(
        {"start_date": date.today(), "end_date": date.today() + timedelta(days=7)}
    )
    assert {n.neo_id for n in found} >= {998, 999}


def test_search_with_an_unknown_criterion_fails():
    with pytest.raises(ValueError):
        NeoDao().find({"colour": "red"})


def test_create_user_neo_without_nasa_id_then_delete():
    neo = Neo(
        nasa_id=None,
        name="Pytest observation",
        absolute_magnitude=22.0,
        diameter_min=0.004,
        diameter_max=0.009,
        hazardous=False,
        url_nasa=None,
        origin="USER",
        date_update=datetime.now(),
    )
    assert NeoDao().create(neo) is True
    # small diameters are kept (NUMERIC(12, 6), not rounded to 0)
    assert float(NeoDao().find_by_id(neo.neo_id).diameter_min) == pytest.approx(0.004)
    assert NeoDao().delete(neo.neo_id) is True


# ---------------------------------------------------------------- ApproachDao


def test_find_approaches_of_a_neo():
    approaches = ApproachDao().find_by_neo_id(TEST_NEO_ID)
    assert len(approaches) == 1
    assert approaches[0].body == "Earth"


def test_create_approach_twice_the_same_day_updates_it():
    day = datetime.combine(date.today() + timedelta(days=30), datetime.min.time())
    first = Approach(neo_id=998, approach_date=day, distance=1e6, speed=1e4, body="Earth")
    second = Approach(neo_id=998, approach_date=day, distance=2e6, speed=1e4, body="Earth")

    assert ApproachDao().create(first) is True
    assert ApproachDao().create(second) is True  # same (neo, day): updated, not duplicated

    same_day = [a for a in ApproachDao().find_by_neo_id(998) if a.approach_day == day.date()]
    assert len(same_day) == 1
    assert same_day[0].distance == pytest.approx(2e6)


# ---------------------------------------------------------------- FavouriteDao


def test_add_list_and_remove_a_favourite():
    assert FavouriteDao().create(TEST_NEO_ID, TEST_USER_ID) is True
    assert TEST_NEO_ID in FavouriteDao().find_favourite_by_user(TEST_USER_ID)
    assert FavouriteDao().delete(TEST_NEO_ID, TEST_USER_ID) is True
    assert TEST_NEO_ID not in FavouriteDao().find_favourite_by_user(TEST_USER_ID)


def test_remove_a_favourite_that_does_not_exist():
    assert FavouriteDao().delete(TEST_NEO_ID, TEST_USER_ID) is False


# ---------------------------------------------------------------- ImportDao


def test_last_successful_import():
    task = Import(
        user_id=TEST_USER_ID,
        start_date=date(2026, 1, 1),
        end_date=date(2026, 1, 7),
        status="running",
    )
    ImportDao().create(task)
    task._status = "success"
    assert ImportDao().update(task) is True

    last = ImportDao().find_last_successful_import()
    assert last._end_date == date(2026, 1, 7)


def test_update_an_import_that_was_never_created():
    assert ImportDao().update(Import(start_date=date.today(), end_date=date.today())) is False


# ---------------------------------------------------------------- ConnectionDao


def test_record_and_list_connections():
    ConnectionDao().create(TEST_USER_ID, "pytest-token")
    connections = ConnectionDao().find_by_user(TEST_USER_ID)
    assert len(connections) >= 1


# ---------------------------------------------------------------- Safety


def test_the_tests_run_on_the_test_schema():
    """Guard: the DAO tests must never run on the application schema."""
    from dao.db_connection import DBConnection

    with DBConnection().connection as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT current_schema() AS schema;")
            assert cursor.fetchone()["schema"] == "project_test_dao"
