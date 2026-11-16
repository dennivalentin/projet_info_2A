"""Unit tests of FavouriteService (the DAOs are mocked: no database needed)."""

from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from business_object.approach import Approach
from service.favourite_service import FavouriteService


@pytest.fixture
def daos():
    """Replaces the three DAOs used by FavouriteService with mocks."""
    with (
        patch("service.favourite_service.FavouriteDao") as favourite_dao,
        patch("service.favourite_service.NeoDao") as neo_dao,
        patch("service.favourite_service.ApproachDao") as approach_dao,
    ):
        mocks = {
            "favourite": MagicMock(),
            "neo": MagicMock(),
            "approach": MagicMock(),
        }
        favourite_dao.return_value = mocks["favourite"]
        neo_dao.return_value = mocks["neo"]
        approach_dao.return_value = mocks["approach"]
        yield mocks


def _approach(day: int, distance: float) -> Approach:
    return Approach(
        neo_id=7,
        approach_date=datetime(2026, 11, day, 12, 0),
        distance=distance,
        speed=50000.0,
        body="Earth",
    )


def test_add_favourite_ok(daos):
    # GIVEN
    daos["favourite"].create.return_value = True
    # WHEN
    added = FavouriteService().add_favourite(neo_id=7, user_id=2)
    # THEN
    assert added is True
    daos["favourite"].create.assert_called_once_with(7, 2)


def test_add_favourite_ko(daos):
    """The DAO refuses (e.g. already a favourite): the service says False."""
    daos["favourite"].create.return_value = False
    assert FavouriteService().add_favourite(neo_id=7, user_id=2) is False


def test_remove_favourite_ko_when_nothing_deleted(daos):
    daos["favourite"].delete.return_value = False
    assert FavouriteService().remove_favourite(neo_id=7, user_id=2) is False


def test_list_all_favourite_by_user_returns_the_neos(daos):
    # GIVEN: two favourites
    daos["favourite"].find_favourite_by_user.return_value = [7, 8]
    daos["neo"].find_by_id.side_effect = lambda neo_id: f"neo-{neo_id}"
    # WHEN
    neos = FavouriteService().list_all_favourite_by_user(2)
    # THEN
    assert neos == ["neo-7", "neo-8"]


def test_approaches_favourite_groups_by_neo(daos):
    daos["favourite"].find_favourite_by_user.return_value = [7]
    daos["approach"].find_by_neo_id.return_value = [_approach(10, 1e6)]

    result = FavouriteService().approches_favourite(2)

    assert list(result) == [7]
    assert len(result[7]) == 1


def test_graph_favourite_returns_a_png_data_url(daos):
    daos["favourite"].find_favourite_by_user.return_value = [7]
    daos["approach"].find_by_neo_id.return_value = [_approach(10, 1e6), _approach(12, 2e6)]

    image = FavouriteService().graph_favourite(user_id=2, neo_id=7)

    assert image.startswith("data:image/png;base64,")


def test_graph_favourite_without_approach_raises(daos):
    daos["favourite"].find_favourite_by_user.return_value = [7]
    daos["approach"].find_by_neo_id.return_value = []

    with pytest.raises(ValueError):
        FavouriteService().graph_favourite(user_id=2, neo_id=7)


def test_graph_of_a_neo_that_is_not_a_favourite_raises(daos):
    daos["favourite"].find_favourite_by_user.return_value = [7]

    with pytest.raises(KeyError):
        FavouriteService().graph_favourite(user_id=2, neo_id=999)
