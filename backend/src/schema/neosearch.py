from pydantic import BaseModel
from datetime import datetime

class NeoSearch(BaseModel):
    nasa_id: str | None
    name: str | None
    absolute_magnitude: float | None
    diameter_min: float | None
    diameter_max: float | None
    hazardous: bool | None
    url_nasa: str | None
    origin: str | None
    date_update: datetime  | None
    neo_id: int | None