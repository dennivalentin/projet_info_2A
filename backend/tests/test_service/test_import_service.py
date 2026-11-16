"""Unit tests of ImportService.

The NASA API (requests.get), the DAOs and time.sleep are mocked:
no network, no database and no waiting.
"""

from datetime import date, timedelta
from unittest.mock import MagicMock, patch

import pytest

from business_object.import_bo import Import
from service import import_service
from service.import_service import ImportService

NASA_ITEM = {
    "id": "3542519",
    "name": "(2010 PK9)",
    "absolute_magnitude_h": 21.8,
    "estimated_diameter": {
        "kilometers": {"estimated_diameter_min": 0.116, "estimated_diameter_max": 0.259}
    },
    "is_potentially_hazardous_asteroid": True,
    "nasa_jpl_url": "https://ssd.jpl.nasa.gov",
    "close_approach_data": [
        {
            "close_approach_date": "2026-11-11",
            "close_approach_date_full": "2026-Nov-11 17:25",
            "orbiting_body": "Earth",
            "miss_distance": {"kilometers": "4985600.5"},
            "relative_velocity": {"kilometers_per_hour": "54200.1"},
        }
    ],
}


def _response(status_code: int, feed: dict | None = None) -> MagicMock:
    response = MagicMock(status_code=status_code, text="error")
    response.json.return_value = {"near_earth_objects": feed or {}}
    return response


@pytest.fixture
def mocks():
    """Mocks the NASA API, the DAOs and the pauses of ImportService."""
    with (
        patch.object(import_service.requests, "get") as get,
        patch.object(import_service.time, "sleep"),
        patch("service.import_service.NeoDao") as neo_dao,
        patch("service.import_service.ApproachDao") as approach_dao,
        patch("service.import_service.ImportDao") as import_dao,
    ):
        neo_dao.return_value.create.return_value = True
        approach_dao.return_value.create.return_value = True
        yield {"get": get, "import_dao": import_dao.return_value}


def test_import_one_day_ok(mocks):
    # GIVEN: NASA returns one NEO with one approach
    mocks["get"].return_value = _response(200, {"2026-11-11": [NASA_ITEM]})
    # WHEN
    result = ImportService().import_neo_range(date(2026, 11, 11), date(2026, 11, 11))
    # THEN
    assert result == {"status": "success", "nb_calls": 1, "nb_neo": 1, "nb_approaches": 1}
    saved_task = mocks["import_dao"].update.call_args.args[0]
    assert saved_task._status == "success"


def test_import_splits_the_period_in_windows_of_7_days(mocks):
    mocks["get"].return_value = _response(200)
    # 20 days -> windows [0-7], [8-15], [16-19]
    result = ImportService().import_neo_range(date(2026, 1, 1), date(2026, 1, 20))
    assert result["nb_calls"] == 3


def test_import_retries_after_a_rate_limit(mocks):
    """A 429 is followed by a pause, then the same window is requested again."""
    mocks["get"].side_effect = [_response(429), _response(200, {"2026-11-11": [NASA_ITEM]})]

    result = ImportService().import_neo_range(date(2026, 11, 11), date(2026, 11, 11))

    assert result["status"] == "success"
    assert result["nb_calls"] == 2


def test_import_gives_up_when_the_rate_limit_never_resets(mocks):
    mocks["get"].return_value = _response(429)

    with pytest.raises(RuntimeError, match="rate limit"):
        ImportService().import_neo_range(date(2026, 11, 11), date(2026, 11, 11))

    # The import is recorded as failed instead of staying "running"
    saved_task = mocks["import_dao"].update.call_args.args[0]
    assert saved_task._status == "failed"
    assert saved_task._nb_calls == import_service.MAX_RATE_LIMIT_RETRIES + 1


def test_import_api_error_raises_and_is_recorded(mocks):
    mocks["get"].return_value = _response(500)

    with pytest.raises(RuntimeError, match="500"):
        ImportService().import_neo_range(date(2026, 11, 11), date(2026, 11, 11))

    assert mocks["import_dao"].update.call_args.args[0]._status == "failed"


def test_approach_without_exact_time_is_dated_at_midnight():
    data = dict(NASA_ITEM["close_approach_data"][0], close_approach_date_full=None)
    approach = ImportService._approach_from_nasa(data, neo_id=1)
    assert approach.approach_date.hour == 0
    assert approach.distance == pytest.approx(4985600.5)


def test_import_update_is_up_to_date(mocks):
    last = Import(user_id=1, start_date=date.today(), end_date=date.today() + timedelta(days=400))
    mocks["import_dao"].find_last_successful_import.return_value = last

    assert ImportService().import_update()["status"] == "up_to_date"
    mocks["get"].assert_not_called()


def test_import_update_without_previous_import_runs_the_full_import(mocks):
    mocks["import_dao"].find_last_successful_import.return_value = None
    with patch.object(ImportService, "import_all", return_value={"status": "success"}) as full:
        ImportService().import_update(user_id=5)
    full.assert_called_once_with(user_id=5)
