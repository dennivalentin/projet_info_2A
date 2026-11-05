from datetime import date
from pydantic import BaseModel, ConfigDict


class ApproachIn(BaseModel):
    date: date
    distance_km: float
    velocity_kms: float


class NeoIn(BaseModel):
    """Un NEO tel qu'on l'importe depuis la NASA."""

    id: str
    name: str
    diameter_min_m: float
    diameter_max_m: float
    is_hazardous: bool
    nasa_jpl_url: str | None = None
    approaches: list[ApproachIn] = []


class NeoOut(BaseModel):
    """Un NEO tel qu'on le renvoie au frontend."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    diameter_min_m: float
    diameter_max_m: float
    is_hazardous: bool
    source: str  # "nasa" ou "user"
    nasa_jpl_url: str | None = None


class NeoSearchCriteria(BaseModel):
    name: str | None = None
    neo_id: str | None = None
    diameter_min_m: float | None = None
    diameter_max_m: float | None = None
    hazardous: bool | None = None
    approach_from: date | None = None
    approach_to: date | None = None
    sort_by: str = "name"
    order: str = "asc"
