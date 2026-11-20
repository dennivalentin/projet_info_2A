from datetime import datetime
from unittest.mock import MagicMock

import pytest

from business_object.approach import Approach
from business_object.neo import Neo
from dao.approach_dao import ApproachDao
from dao.neo_dao import NeoDao
from service.neo_service import NeoService


def test_created_neo_is_a_user_neo():
    """A declared NEO has the origin USER and no NASA id, and its name is cleaned."""
    # GIVEN
    neo_dao = MagicMock(spec=NeoDao)  # injected: the NeoDao singleton is not modified
    neo_dao.create.return_value = True

    # WHEN
    neo = NeoService(neo_dao=neo_dao).create(name="  caillou  ", diameter_min=0.2)

    # THEN
    assert neo.name == "caillou"
    assert neo.origin == "USER"
    assert neo.nasa_id is None
    neo_dao.create.assert_called_once_with(neo)


def test_neo_service_create_success():
    """Test successful creation of a user NEO."""
    mock_neo_dao = MagicMock(spec=NeoDao)
    mock_neo_dao.create.return_value = True

    service = NeoService(neo_dao=mock_neo_dao)
    neo = service.create(
        name="2026-TestAst",
        diameter_min=0.12,
        diameter_max=0.34,
        absolute_magnitude=21.0,
        hazardous=False,
    )

    assert neo is not None
    assert neo.name == "2026-TestAst"
    assert neo.origin == "USER"
    assert neo.hazardous is False
    assert mock_neo_dao.create.called


def test_neo_service_create_failure():
    """Test creation failure when DAO returns False."""
    mock_neo_dao = MagicMock(spec=NeoDao)
    mock_neo_dao.create.return_value = False

    service = NeoService(neo_dao=mock_neo_dao)
    neo = service.create(name="FailingAsteroid")

    assert neo is None


def test_neo_service_search():
    """Test searching NEOs via criteria."""
    mock_neo_dao = MagicMock(spec=NeoDao)
    dummy_neo = Neo(
        neo_id=1,
        nasa_id="12345",
        name="Apophis",
        absolute_magnitude=19.7,
        diameter_min=0.34,
        diameter_max=0.45,
        hazardous=True,
        url_nasa="https://nasa.gov",
        origin="NASA",
        date_update=datetime.now(),
    )
    mock_neo_dao.find.return_value = [dummy_neo]

    service = NeoService(neo_dao=mock_neo_dao)
    results = service.search({"name": "Apop", "hazardous": True})

    assert len(results) == 1
    assert results[0].name == "Apophis"
    assert results[0].hazardous is True
    mock_neo_dao.find.assert_called_once_with({"name": "Apop", "hazardous": True})


def test_neo_service_get_details():
    """Test retrieving full NEO details including approaches."""
    mock_neo_dao = MagicMock(spec=NeoDao)
    mock_approach_dao = MagicMock(spec=ApproachDao)

    dummy_neo = Neo(
        neo_id=42,
        nasa_id="99999",
        name="Bennu",
        absolute_magnitude=20.1,
        diameter_min=0.49,
        diameter_max=0.51,
        hazardous=True,
        url_nasa=None,
        origin="NASA",
        date_update=datetime.now(),
    )
    dummy_approach = Approach(
        approach_id=101,
        neo_id=42,
        approach_date=datetime(2026, 11, 15, 12, 0),
        distance=750000.0,
        speed=45000.0,
        body="Earth",
    )

    mock_neo_dao.find_by_id.return_value = dummy_neo
    mock_approach_dao.find_by_neo_id.return_value = [dummy_approach]

    service = NeoService(neo_dao=mock_neo_dao, approach_dao=mock_approach_dao)
    details = service.get_neo_details(42)

    assert details is not None
    assert details["neo_id"] == 42
    assert details["name"] == "Bennu"
    assert len(details["approaches"]) == 1
    assert details["approaches"][0]["distance_km"] == 750000.0
    assert details["approaches"][0]["distance_au"] > 0
    assert details["approaches"][0]["body"] == "Earth"


@pytest.mark.parametrize(
    "diameters",
    [{"diameter_min": -1.0}, {"diameter_max": 0.0}, {"diameter_min": 0.5, "diameter_max": 0.1}],
)
def test_neo_service_create_refuses_invalid_diameters(diameters):
    """A diameter must be positive, and the minimum cannot exceed the maximum."""
    mock_neo_dao = MagicMock(spec=NeoDao)
    with pytest.raises(ValueError):
        NeoService(neo_dao=mock_neo_dao).create(name="Bad", **diameters)
    mock_neo_dao.create.assert_not_called()
