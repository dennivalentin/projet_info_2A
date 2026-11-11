from datetime import date, datetime
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from business_object.approach import Approach
from business_object.neo import Neo
from business_object.user import User
from main import app
from utils.security import get_current_user

client = TestClient(app)


@patch("controller.neo_controller.NeoService")
def test_search_neos_endpoint(mock_service_class):
    """Test POST /neo/search endpoint."""
    mock_service = MagicMock()
    mock_service_class.return_value = mock_service

    dummy_neo = Neo(
        neo_id=1,
        nasa_id="3542519",
        name="(2010 PK9)",
        absolute_magnitude=21.8,
        diameter_min=0.116,
        diameter_max=0.259,
        hazardous=True,
        url_nasa="https://ssd.jpl.nasa.gov",
        origin="NASA",
        date_update=datetime(2026, 10, 25, 12, 0),
    )
    mock_service.search.return_value = [dummy_neo]

    response = client.post("/neo/search", json={"name": "PK9", "hazardous": True})

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "(2010 PK9)"
    assert data[0]["hazardous"] is True


@patch("controller.neo_controller.NeoService")
def test_get_neo_detail_endpoint_found(mock_service_class):
    """Test GET /neo/{neo_id} when object exists."""
    mock_service = MagicMock()
    mock_service_class.return_value = mock_service

    mock_service.get_neo_details.return_value = {
        "neo_id": 42,
        "nasa_id": "3542519",
        "name": "Apophis",
        "absolute_magnitude": 19.7,
        "diameter_min": 0.34,
        "diameter_max": 0.45,
        "hazardous": True,
        "url_nasa": "https://ssd.jpl.nasa.gov",
        "origin": "NASA",
        "date_update": "2026-10-25T12:00:00",
        "approaches": [
            {
                "approach_id": 1,
                "neo_id": 42,
                "approach_day": "2029-04-13",
                "approach_date": "2029-04-13T21:46:00",
                "distance_km": 38000.0,
                "distance_au": 0.00025,
                "speed_km_h": 74300.0,
                "body": "Earth",
            }
        ],
    }

    response = client.get("/neo/42")

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Apophis"
    assert len(data["approaches"]) == 1
    assert data["approaches"][0]["distance_au"] == 0.00025


@patch("controller.neo_controller.NeoService")
def test_get_neo_detail_endpoint_not_found(mock_service_class):
    """Test GET /neo/{neo_id} when object does not exist."""
    mock_service = MagicMock()
    mock_service_class.return_value = mock_service
    mock_service.get_neo_details.return_value = None

    response = client.get("/neo/999999")

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@patch("controller.neo_controller.NeoService")
def test_create_user_neo_endpoint(mock_service_class):
    """Test POST /neo to create a user NEO."""
    mock_service = MagicMock()
    mock_service_class.return_value = mock_service

    created_neo = Neo(
        neo_id=10,
        nasa_id=None,
        name="Amateur-Observer-1",
        absolute_magnitude=22.0,
        diameter_min=0.15,
        diameter_max=0.35,
        hazardous=False,
        url_nasa=None,
        origin="USER",
        date_update=datetime(2026, 10, 25, 12, 0),
    )
    mock_service.create.return_value = created_neo

    payload = {
        "name": "Amateur-Observer-1",
        "absolute_magnitude": 22.0,
        "diameter_min": 0.15,
        "diameter_max": 0.35,
        "hazardous": False,
    }
    # Creating a NEO requires a logged-in user
    assert client.post("/neo", json=payload).status_code == 401

    app.dependency_overrides[get_current_user] = lambda: User(user_id=2, username="obs")
    try:
        response = client.post("/neo", json=payload)
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 201
    data = response.json()
    assert data["neo_id"] == 10
    assert data["name"] == "Amateur-Observer-1"
    assert data["origin"] == "USER"
