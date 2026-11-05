"""Tests of StatisticsDao (FO3). The database connection is mocked: no database needed."""

from unittest.mock import MagicMock, patch

from dao.statistics_dao import StatisticsDao


def _fake_db(rows):
    """Builds a fake DBConnection whose cursor returns the given rows."""
    cursor = MagicMock()
    cursor.fetchall.return_value = rows
    connection = MagicMock()
    connection.cursor.return_value.__enter__.return_value = cursor
    db = MagicMock()
    db.return_value.connection.__enter__.return_value = connection
    return db, cursor


def test_approaches_per_month():
    # GIVEN a fake database returning 2 months
    rows = [
        {"month": "2026-10", "nb_approaches": 31},
        {"month": "2026-11", "nb_approaches": 30},
    ]
    db, cursor = _fake_db(rows)

    # WHEN
    with patch("dao.statistics_dao.DBConnection", db):
        result = StatisticsDao().approaches_per_month()

    # THEN the rows are returned, and the SQL groups by month
    assert result == rows
    query = cursor.execute.call_args.args[0]
    assert "GROUP BY month" in query


def test_size_distribution():
    rows = [{"size_class": "3. 140 m - 1 km", "nb_neos": 29}]
    db, cursor = _fake_db(rows)

    with patch("dao.statistics_dao.DBConnection", db):
        result = StatisticsDao().size_distribution()

    assert result == rows
    assert "CASE" in cursor.execute.call_args.args[0]


def test_global_summary_returns_one_dict():
    rows = [{"nb_neos": 40, "hazardous_pct": 25.0}]
    db, cursor = _fake_db(rows)

    with patch("dao.statistics_dao.DBConnection", db):
        result = StatisticsDao().global_summary()

    # THEN a single dict (not a list), and the SQL avoids division by zero
    assert result == {"nb_neos": 40, "hazardous_pct": 25.0}
    assert "NULLIF" in cursor.execute.call_args.args[0]
