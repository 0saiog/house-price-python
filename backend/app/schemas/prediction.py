"""Request and response bodies.

The request mirrors the model's input features. Everything the pipeline can
impute is optional, so a caller who does not know the balcony count sends
nothing and gets the training median rather than being forced to invent a zero.
"""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, Field, field_validator, model_validator


class PredictionRequest(BaseModel):
    """A property to price."""

    location: Annotated[str, Field(min_length=1, description="City, as listed by GET /locations")]
    area_sqft: Annotated[float, Field(gt=0, le=1_000_000, description="Floor area in square feet")]
    furnishing: Literal["Furnished", "Semi-Furnished", "Unfurnished"] = "Semi-Furnished"
    transaction: Literal["Resale", "New Property"] = "Resale"
    is_carpet_area: bool = True
    bathroom: Annotated[float | None, Field(ge=0)] = None
    balcony: Annotated[float | None, Field(ge=0)] = None
    car_parking: Annotated[float | None, Field(ge=0)] = None
    parking_covered: bool = False
    floor_num: float | None = None
    total_floors: Annotated[float | None, Field(ge=0)] = None
    ownership: str | None = None
    facing: str | None = None
    overlooking_garden: bool = False
    overlooking_pool: bool = False
    overlooking_main_road: bool = False

    @field_validator("location")
    @classmethod
    def _not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("location must not be blank")
        return value

    @model_validator(mode="after")
    def _floor_within_building(self) -> "PredictionRequest":
        """A cross-field rule pydantic cannot express one field at a time."""
        if self.floor_num is not None and self.total_floors is not None:
            if self.floor_num > self.total_floors:
                raise ValueError("floor_num cannot be above total_floors")
        return self


class PredictionResponse(BaseModel):
    """The predicted price."""

    predicted_price: float
    predicted_price_formatted: str
    currency: str = "INR"
    location_known: bool


class HealthResponse(BaseModel):
    """Service liveness and what it has loaded."""

    status: str
    model_loaded: bool
    model_name: str
    sklearn_version: str


def format_rupees(value: float) -> str:
    """Format rupees in Indian listing shorthand."""
    if value >= 1e7:
        return f"{value / 1e7:.2f} Cr"
    if value >= 1e5:
        return f"{value / 1e5:.2f} Lac"
    return f"{value:.0f}"
