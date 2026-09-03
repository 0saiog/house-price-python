"""Service entry point.

    uvicorn app.main:app --reload    # from backend/

Loads the model once, at startup, and serves.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import prediction
from app.core.config import settings
from app.services.inference import Engine
from app.utils.logging_config import configure

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load the model once, before the first request.

    Doing this at startup rather than per request means a missing model stops
    the process immediately with a clear message, instead of surfacing as a 500
    on the first call.
    """
    configure(settings.log_level)
    app.state.engine = Engine(settings.model_path, settings.locations_path)
    yield


app = FastAPI(
    title="House Price Prediction API",
    description="Predicts Indian residential property prices from a scikit-learn pipeline.",
    version="1.0.0",
    lifespan=lifespan,
)

# Restricted to the configured origin rather than "*": the only browser that
# needs to call this is the project's own frontend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.allowed_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(prediction.router)
