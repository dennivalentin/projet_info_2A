from unittest.mock import MagicMock, patch

import pytest

from service.alert_service import AlertService


@pytest.fixture
def mock_alert_dao():
    """Mock singleton AlertDao to isolate service tests from database."""
    with patch("service.alert_service.AlertDao") as mock_dao_class:
        mock_instance = MagicMock()
        mock_dao_class.return_value = mock_instance
        yield mock_instance


def test_check_and_send_notification(mock_alert_dao):
    """Test something is sent if there is at least one match"""
    user_id = 1
    mock_alert_dao.find_matching_approaches_for_user.return_value = [
        {
            "alert_id": 42,
            "neo_name": "Apophis",
            "hazardous_only": False,
            "diameter_min": 0.3,
            "diameter_max": 0.45,
            "distance_max": 40000.0,
            "distance": 31000.0,
        }
    ]

    result = AlertService().check_send_notification(user_id)

    # THEN
    assert len(result) == 1
