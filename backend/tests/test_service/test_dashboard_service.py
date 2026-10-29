"""Tests of DashboardService (F2). The DAO is replaced by fake answers: no database needed."""

from datetime import date, timedelta

import pytest

from dao.dashboard_dao import DashboardDao
from service.dashboard_service import DashboardService


@pytest.fixture
def fake_dao(monkeypatch):
    """Replaces the 4 DAO queries by fixed answers (restored after each test)."""
    monkeypatch.setattr(DashboardDao, "count_upcoming",
                        lambda self, start, end: {"nb_neos": 4, "nb_hazardous": 1})
    monkeypatch.setattr(DashboardDao, "find_upcoming_approaches",
                        lambda self, start, end: [{"name": "NEO A"}])
    monkeypatch.setattr(DashboardDao, "find_closest_approach",
                        lambda self, start, end: {"name": "NEO A", "distance": 1000})
    monkeypatch.setattr(DashboardDao, "find_favourites",
                        lambda self, user_id: [])


def test_default_period_is_next_7_days():
    start, end = DashboardService.check_period(None, None)
    assert start == date.today()
    assert end == date.today() + timedelta(days=7)


def test_end_before_start_raises_error():
    with pytest.raises(ValueError):
        DashboardService.check_period(date(2026, 11, 10), date(2026, 11, 1))


def test_hazardous_share(fake_dao):
    # GIVEN 4 NEOs, 1 hazardous (fake DAO)
    # WHEN
    result = DashboardService().get_dashboard(user_id=2)
    # THEN 1/4 = 25 %
    assert result["hazardous_share_pct"] == 25.0
    assert result["closest_approach"]["name"] == "NEO A"


def test_no_neo_no_division_by_zero(fake_dao, monkeypatch):
    # GIVEN an empty period
    monkeypatch.setattr(DashboardDao, "count_upcoming",
                        lambda self, start, end: {"nb_neos": 0, "nb_hazardous": 0})
    # WHEN / THEN: 0 %, no crash
    assert DashboardService().get_dashboard(user_id=2)["hazardous_share_pct"] == 0.0