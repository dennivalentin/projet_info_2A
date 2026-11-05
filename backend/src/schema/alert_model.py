from pydantic import BaseModel


class AlertCreateModel(BaseModel):
    user_id: int
    label: str
    diameter_min: float | None = None
    distance_max: float | None = None
    hazardous_only: bool = False
