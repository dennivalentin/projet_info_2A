from datetime import date

from pydantic import BaseModel, ConfigDict


class Approach(BaseModel):
    creation_date: date
    distance: float
    speed: float


class NeoIn(BaseModel):
    """A NEO as it is imported from NASA database."""

    id: str
    name: str
    diameter_min: float
    diameter_max: float
    hazardous: bool
    url_nasa: str | None = None
    approaches: list[Approach] = []


class NeoOut(BaseModel):
    """A NEO as we return it to the frontend."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    diameter_min: float
    diameter_max: float
    hazardous: bool
    source: str  # "nasa" ou "user"
    url_nasa: str | None = None


class NeoSearchCriteria(BaseModel):
    name: str | None = None
    neo_id: str | None = None
    diameter_min: float | None = None
    diameter_max: float | None = None
    hazardous: bool | None = None
    approach_from: date | None = None
    approach_to: date | None = None
    sort_by: str = "name"
    order: str = "asc"
