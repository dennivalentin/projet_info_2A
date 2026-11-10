from fastapi import APIRouter, HTTPException

from schema.alert_model import AlertCreateModel
from service.alert_service import AlertService
from utils.log_utils import get_logger

router = APIRouter(prefix="/alerts", tags=["Alerts"])
logger = get_logger(__name__)


@router.post("/", status_code=201)
def create_alert(param: AlertCreateModel):
    """Create a new alert for a user"""
    service = AlertService()
    logger.info(f"Creating alert '{param.label}' for user_id={param.user_id}")
    try:
        res = service.create_alert(
            user_id=param.user_id,
            label=param.label,
            diameter_min=param.diameter_min,
            distance_max=param.distance_max,
            hazardous_only=param.hazardous_only,
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    if not res:
        raise HTTPException(
            status_code=400,
            detail="Error, alert not created",
        )
    return {"message": "Alert created"}


@router.get("/user/{user_id}")
def list_alerts_by_user(user_id: int):
    """List of all the alert of a user"""
    service = AlertService()
    logger.info(f"Listing alerts for user_id={user_id}")
    alerts = service.list_alert_user(user_id)
    return [alert.to_dict() for alert in alerts]


@router.get("/user/{user_id}/notifications")
def check_notifications(user_id: int):
    """Check and return if an alert is triggered"""
    service = AlertService()
    logger.info(f"Checking notifications for user_id={user_id}")
    notifications = service.check_send_notification(user_id)
    return {"notifications": notifications}


@router.patch("/{alert_id}/toggle")
def alert_status(alert_id: int):
    """Turn on/off an alert"""
    service = AlertService()
    logger.info(f"Toggling alert_id={alert_id}")
    success = service.turn_on_off(alert_id)
    if not success:
        raise HTTPException(status_code=404, detail="Alert not found")
    return {"message": "Status updated"}


@router.delete("/{alert_id}")
def delete_alert(alert_id: int):
    """Delete an alert"""
    service = AlertService()
    logger.info(f"Deleting alert_id={alert_id}")
    service.delete(alert_id)
    return {"message": "Alert deleted"}
