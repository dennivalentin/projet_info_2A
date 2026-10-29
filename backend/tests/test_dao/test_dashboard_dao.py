"""Tests of DashboardDao (F2). They need the database to contain approaches."""

from datetime import date, timedelta

import pytest

from dao.dashboard_dao import DashboardDao

START = date.today()
END = date.today() + timedelta(days=7)


def _has_data() -> bool:
    """True if the DB is reachable and contains approaches for the next 7 days."""
    try:
        return DashboardDao().count_upcoming(START, END)["nb_neos"] > 0
    except Exception:
        return False


# Skip all the tests of this file if there is no data (e.g. on a teammate's empty DB, or in CI)
pytestmark = pytest.mark.skipif(not _has_data(), reason="No approach data in the database")


def test_upcoming_approaches_are_sorted():
    # WHEN
    approaches = DashboardDao().find_upcoming_approaches(START, END)
    # THEN: the soonest approach comes first
    dates = [a["approach_date"] for a in approaches]
    assert len(dates) > 0
    assert dates == sorted(dates)


def test_upcoming_approaches_are_in_the_period():
    for a in DashboardDao().find_upcoming_approaches(START, END):
        assert START <= a["approach_date"].date() <= END


def test_count_hazardous_not_more_than_total():
    counts = DashboardDao().count_upcoming(START, END)
    assert 0 <= counts["nb_hazardous"] <= counts["nb_neos"]


def test_closest_approach_is_the_minimum():
    # GIVEN
    dao = DashboardDao()
    all_distances = [a["distance"] for a in dao.find_upcoming_approaches(START, END)]
    # WHEN
    closest = dao.find_closest_approach(START, END)
    # THEN: its distance is the smallest of the period
    assert closest["distance"] == min(all_distances)


def test_closest_approach_empty_period():
    # A period with no data -> None, not a crash
    assert DashboardDao().find_closest_approach(date(1900, 1, 1), date(1900, 1, 2)) is None


def test_favourites_unknown_user():
    # A user with no favourites -> empty list
    assert DashboardDao().find_favourites(999999) == []