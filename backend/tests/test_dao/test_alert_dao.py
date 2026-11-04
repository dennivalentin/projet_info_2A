import os
from unittest.mock import patch

import pytest

from business_object.alert import Alert
from dao.alert_dao import AlertDao
from dao.db_connection import DBConnection


@pytest.fixture(autouse=True)
def clean_alert_table():
    """Clean test alerts before and after each test"""

    with DBConnection().connection as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM alert WHERE label LIKE 'Pytest%' OR user_id = 1;"
            )

    yield

    with DBConnection().connection as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM alert WHERE label LIKE 'Pytest%' OR user_id = 1;"
            )


def test_create_ok():
    """Successfully create an Alert"""

    # GIVEN
    user_id = 1
    label = "test"
    distance_max = 10000
    diameter_min = 100
    hazardous_only = True

    # WHEN / THEN
    creation_ok = AlertDao().create(
        user_id=user_id,
        label=label,
        distance_max=distance_max,
        diameter_min=diameter_min,
        hazardous_only=hazardous_only,
    )

    assert creation_ok


def test_create_duplicate_ko():
    """Successfully create an Alert"""

    # GIVEN
    user_id = 1
    label = "test"
    label2 = "test2"
    distance_max = 10000
    diameter_min = 100
    hazardous_only = True

    # WHEN / THEN
    creation_ok = AlertDao().create(
        user_id=user_id,
        label=label,
        distance_max=distance_max,
        diameter_min=diameter_min,
        hazardous_only=hazardous_only,
    )

    creation_ok2 = AlertDao().create(
        user_id=user_id,
        label=label2,
        distance_max=distance_max,
        diameter_min=diameter_min,
        hazardous_only=hazardous_only,
    )

    assert creation_ok
    assert creation_ok2 is False


def test_find_by_user():
    """Find a player by an existing id"""

    # GIVEN
    user_id = 1
    AlertDao().create(user_id=user_id, label="Pytest Alert", diameter_min=50)

    # WHEN
    alert = AlertDao().find_by_user(user_id)

    # THEN
    assert alert is not None


def test_find_by_id_non_existing():
    """Find a player by a non-existing id"""

    # GIVEN
    user_id = 9999999999999

    # WHEN
    alert = AlertDao().find_by_user(user_id)

    # THEN
    assert alert is None


def test_find_by_id():
    """Find an alert by its id"""
    user_id = 1
    AlertDao().create(user_id=user_id, label="Pytest Find By ID", distance_max=2000)
    alerts = AlertDao().find_by_user(user_id)
    alert_id = alerts[0].alert_id

    # WHEN
    alert = AlertDao().find_by_id(alert_id)

    # THEN
    assert alert is not None


def test_create_ko():
    """Fail to create a Player (invalid elo and email)"""

    # GIVEN
    user_id = 1
    label = "test"
    distance_max = "not an int"
    diameter_min = 100
    hazardous_only = True

    # WHEN / THEN
    creation_ok = AlertDao().create(
        user_id=user_id,
        label=label,
        distance_max=distance_max,
        diameter_min=diameter_min,
        hazardous_only=hazardous_only,
    )

    assert creation_ok is False


def test_update_ok():
    """Successfully update a Player"""

    # GIVEN
    user_id = 1
    label = "Pytest"
    label1 = "Pytest label de base"
    new_distance_max = 100000
    diameter_min = 100
    hazardous_only = True

    AlertDao().create(
        user_id=user_id,
        label=label1,
        distance_max=new_distance_max,
        diameter_min=diameter_min,
        hazardous_only=hazardous_only,
    )

    alert_id = AlertDao().find_by_user(user_id)[0].alert_id

    alert = Alert(
        alert_id=alert_id,
        user_id=user_id,
        label=label,
        distance_max=new_distance_max,
        diameter_min=diameter_min,
        hazardous_only=hazardous_only,
    )

    # WHEN
    update_ok = AlertDao().update(alert)

    # THEN
    assert update_ok == 1


def test_update_ko():
    """Fail to update a Player (unknown id)"""

    # GIVEN
    user_id = 1
    label = "Pytest"
    new_distance_max = 100000
    diameter_min = 100
    hazardous_only = True

    AlertDao().create(
        user_id=user_id,
        label=label,
        distance_max=new_distance_max,
        diameter_min=diameter_min,
        hazardous_only=hazardous_only,
    )

    alert_id = AlertDao().find_by_user(user_id)[0].alert_id

    alert = Alert(
        alert_id=alert_id + 1,
        user_id=user_id,
        label=label,
        distance_max=new_distance_max,
        diameter_min=diameter_min,
        hazardous_only=hazardous_only,
    )

    # WHEN
    update_ok = AlertDao().update(alert)

    # THEN
    assert update_ok == 0


def test_delete_ok():
    """Successfully delete a Player"""

    # GIVEN
    user_id = 1
    AlertDao().create(user_id=user_id, label="Pytest Alert", diameter_min=50)
    alert_id = AlertDao().find_by_user(user_id)[0].alert_id

    # WHEN
    delete = AlertDao().delete(alert_id)

    # THEN
    assert delete


def test_delete_ko():
    """Fail to delete a Player (unknown id)"""

    # GIVEN
    user_id = 1
    AlertDao().create(user_id=user_id, label="Pytest Alert", diameter_min=50)
    alert_id = 999999999999999999

    # WHEN
    delete = AlertDao().delete(alert_id)

    # THEN
    assert not delete


if __name__ == "__main__":
    pytest.main([__file__])
