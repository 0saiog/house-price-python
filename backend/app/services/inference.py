"""Loading the trained pipeline, and running it."""

from __future__ import annotations

import json
import logging
from pathlib import Path

import joblib
import sklearn

from app.schemas.prediction import PredictionRequest
from app.services.preprocessing import to_frame

logger = logging.getLogger(__name__)


class ModelNotAvailable(RuntimeError):
    """The pickle or the location list could not be loaded."""


class Engine:
    """The loaded pipeline and the cities it knows.

    Loaded once at startup, never per request: unpickling on every call would
    dominate the latency and re-read the file each time.
    """

    def __init__(self, model_path: Path, locations_path: Path) -> None:
        try:
            self.model = joblib.load(model_path)
        except (OSError, ValueError) as exc:
            raise ModelNotAvailable(
                f"cannot load {model_path} ({exc}). "
                "Run notebooks/house_price_model.ipynb first."
            ) from exc
        try:
            self.locations: list[str] = json.loads(Path(locations_path).read_text())
        except OSError as exc:
            raise ModelNotAvailable(f"cannot read {locations_path} ({exc})") from exc

        self.name = type(self.model).__name__
        self.sklearn_version = sklearn.__version__
        logger.info(
            "model loaded: %s, %d locations, scikit-learn %s",
            self.name,
            len(self.locations),
            self.sklearn_version,
        )

    def predict(self, request: PredictionRequest) -> float:
        """Predict a price in rupees."""
        return float(self.model.predict(to_frame(request))[0])

    def knows_location(self, location: str) -> bool:
        """Whether the model saw this city while training."""
        return location.strip().lower() in self.locations
