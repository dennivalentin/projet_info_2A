"""Unit tests of ApodService (the NASA API is mocked: no network needed)."""

from datetime import date
from unittest.mock import MagicMock, patch

import pytest
import requests

from service.apod_service import ApodService


@patch("service.apod_service.requests.get")
def test_picture_of_a_given_day(mock_get):
    # GIVEN
    mock_get.return_value = MagicMock(
        json=MagicMock(
            return_value={
                "title": "Dwarf galaxy",
                "date": "2026-11-11",
                "explanation": "A small galaxy.",
                "url": "https://apod.nasa.gov/image.jpg",
            }
        )
    )
    # WHEN
    apod = ApodService().get_picture_of_the_day(date(2026, 11, 11))
    # THEN
    assert apod.title == "Dwarf galaxy"
    assert apod.date.year == 2026
    assert mock_get.call_args.kwargs["params"]["date"] == "2026-11-11"


@patch("service.apod_service.requests.get")
def test_nasa_error_is_raised(mock_get):
    """A NASA error (e.g. 429 rate limit) is raised for the controller to turn into a 503."""
    mock_get.return_value.raise_for_status.side_effect = requests.HTTPError("429")
    with pytest.raises(requests.HTTPError):
        ApodService().get_picture_of_the_day()
