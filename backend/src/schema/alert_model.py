from pydantic import BaseModel


class AlertCreateModel(BaseModel):
    """Payload to create an alert (at least one criterion is required)."""

    user_id: int
    label: str
    diameter_min: float | None = None
    distance_max: float | None = None
    hazardous_only: bool = False
