"""Tests of StatisticsService (FO3). The DAO is replaced by fake answers: no database needed."""

from decimal import Decimal

import pytest

from dao.statistics_dao import StatisticsDao
from service.statistics_service import StatisticsService


@pytest.fixture
def fake_dao(monkeypatch):
    """Replaces the 3 DAO queries by fixed answers (restored after each test)."""
    monkeypatch.setattr(StatisticsDao, "global_summary", lambda self: {
        "nb_neos": 40,
        "hazardous_pct": Decimal("25.0"),
        "avg_distance_km": Decimal("7688000"),
        "median_distance_km": Decimal("3844000"),
    })
    monkeypatch.setattr(StatisticsDao, "approaches_per_month",
                        lambda self: [{"month": "2026-11", "nb_approaches": 30}])
    monkeypatch.setattr(StatisticsDao, "size_distribution",
                        lambda self: [{"size_class": "3. 140 m - 1 km", "nb_neos": 29}])


def test_decimals_are_converted_to_float(fake_dao):
    summary = StatisticsService().get_statistics()["summary"]
    assert summary["hazardous_pct"] == 25.0
    assert isinstance(summary["hazardous_pct"], float)


def test_median_in_lunar_distances(fake_dao):
    # 3 844 000 km = 10 lunar distances
    summary = StatisticsService().get_statistics()["summary"]
    assert summary["median_distance_ld"] == 10.0


def test_every_stat_is_justified(fake_dao):
    justifications = StatisticsService().get_statistics()["justifications"]
    for stat in ("approaches_per_month", "size_distribution", "hazardous_pct"):
        assert stat in justifications


def test_empty_database_no_crash(monkeypatch, fake_dao):
    # GIVEN an empty database: no median
    monkeypatch.setattr(StatisticsDao, "global_summary", lambda self: {
        "nb_neos": 0, "hazardous_pct": None, "avg_distance_km": None, "median_distance_km": None,
    })
    # WHEN / THEN: no crash, and no lunar distance
    summary = StatisticsService().get_statistics()["summary"]
    assert "median_distance_ld" not in summary
