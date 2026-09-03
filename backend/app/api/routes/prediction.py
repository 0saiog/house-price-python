"""`GET /health`, `GET /locations`, `POST /predict`."""

from __future__ import annotations

import logging

from fastapi import APIRouter, Request

from app.schemas.prediction import (
    HealthResponse,
    PredictionRequest,
    PredictionResponse,
    format_rupees,
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health(request: Request) -> HealthResponse:
    """Liveness, plus what the service has loaded."""
    engine = request.app.state.engine
    return HealthResponse(
        status="ok",
        model_loaded=True,
        model_name=engine.name,
        sklearn_version=engine.sklearn_version,
    )


@router.get("/locations", response_model=list[str])
def locations(request: Request) -> list[str]:
    """The cities the model was trained on.

    The frontend populates its dropdown from here rather than from a copy of
    `locations.json`, so the options can never list a city the loaded model does
    not actually know.
    """
    return request.app.state.engine.locations


@router.post("/predict", response_model=PredictionResponse)
def predict(payload: PredictionRequest, request: Request) -> PredictionResponse:
    """Price one property.

    A body that does not match the schema never reaches this function: FastAPI
    rejects it with 422 while validating `PredictionRequest`.
    """
    engine = request.app.state.engine
    price = engine.predict(payload)
    logger.info("predicted %s for %s, %.0f sqft", format_rupees(price), payload.location, payload.area_sqft)
    return PredictionResponse(
        predicted_price=price,
        predicted_price_formatted=format_rupees(price),
        location_known=engine.knows_location(payload.location),
    )
