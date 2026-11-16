from unittest.mock import MagicMock, patch

import pytest

from business_object.alert import Alert
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


def test_no_match_gives_no_alert_message(mock_alert_dao):
    mock_alert_dao.find_matching_approaches_for_user.return_value = []
    assert AlertService().check_send_notification(1) == ["No alert detected"]


def test_create_alert_ok(mock_alert_dao):
    mock_alert_dao.create.return_value = True
    assert AlertService().create_alert(user_id=2, label="Big ones", diameter_min=1.0) is True


def test_create_alert_without_any_criterion_is_refused(mock_alert_dao):
    with pytest.raises(ValueError, match="criterion"):
        AlertService().create_alert(user_id=2, label="Nothing")
    mock_alert_dao.create.assert_not_called()


def test_create_alert_with_negative_value_is_refused(mock_alert_dao):
    with pytest.raises(ValueError, match="positive"):
        AlertService().create_alert(user_id=2, label="Wrong", distance_max=-5)


def test_turn_on_off_switches_an_active_alert_off(mock_alert_dao):
    mock_alert_dao.find_by_id.return_value = Alert(alert_id=3, user_id=2, label="x", active=True)

    assert AlertService().turn_on_off(3) is True

    saved = mock_alert_dao.update.call_args.args[0]
    assert saved.active is False
    assert saved.label == "x"  # the other fields are kept


def test_turn_on_off_unknown_alert(mock_alert_dao):
    mock_alert_dao.find_by_id.return_value = None
    assert AlertService().turn_on_off(3) is False
    mock_alert_dao.update.assert_not_called()
