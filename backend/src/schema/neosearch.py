from datetime import date, datetime

from pydantic import BaseModel, Field, model_validator


class NeoSearchCriteria(BaseModel):
    """Search criteria model for filtering NEOs."""

    neo_id: int | None = None
    nasa_id: str | None = None
    name: str | None = None
    hazardous: bool | None = None
    diameter_min: float | None = None
    diameter_max: float | None = None
    origin: str | None = None
    approach_day: date | None = None
    start_date: date | None = None
    end_date: date | None = None
    sort_by: str | None = None
    order: str = "ASC"
    limit: int = Field(default=100, ge=1, le=500)
    offset: int = Field(default=0, ge=0)


class NeoCreateRequest(BaseModel):
    """Payload to create a new user-observed NEO (diameters in km)."""

    name: str = Field(..., min_length=1, max_length=100)
    absolute_magnitude: float | None = Field(default=None, ge=-10, le=40)
    diameter_min: float | None = Field(default=None, gt=0, le=1000)
    diameter_max: float | None = Field(default=None, gt=0, le=1000)
    hazardous: bool = False

    @model_validator(mode="after")
    def check_diameters(self):
        """The minimum diameter cannot be larger than the maximum diameter."""
        if (
            self.diameter_min is not None
            and self.diameter_max is not None
            and self.diameter_min > self.diameter_max
        ):
            raise ValueError("diameter_min cannot be larger than diameter_max")
        return self


class ApproachModel(BaseModel):
    """Schema representing a close approach."""

    approach_id: int | None = None
    neo_id: int
    approach_day: date
    approach_date: datetime
    distance_km: float
    distance_au: float
    speed_km_h: float
    body: str


class NeoModel(BaseModel):
    """Schema representing basic NEO data."""

    neo_id: int | None = None
    nasa_id: str | None = None
    name: str
    absolute_magnitude: float | None = None
    diameter_min: float | None = None
    diameter_max: float | None = None
    hazardous: bool = False
    url_nasa: str | None = None
    origin: str = "USER"
    date_update: datetime | str | None = None


class NeoDetailModel(NeoModel):
    """Schema representing complete NEO details including approaches."""

    approaches: list[ApproachModel] = []
