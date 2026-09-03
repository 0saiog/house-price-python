"""Turning an API request into the one-row frame the pipeline expects.

There is no encoding logic here on purpose. The exported pickle is a full
scikit-learn Pipeline, so imputation, scaling and one-hot encoding all happen
inside it with the statistics fitted during training. This module's only job is
to apply the *same* text normalisation the notebook applied - from the shared
`house_price` package - and to hand over a frame whose columns match training.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from app.schemas.prediction import PredictionRequest
from house_price.cleaning import (
    CATEGORICAL_FEATURES,
    NUMERIC_FEATURES,
    normalize_category,
    normalize_facing,
)


def to_frame(request: PredictionRequest) -> pd.DataFrame:
    """Build the single-row DataFrame the pipeline was trained on.

    Column names and order match ``NUMERIC_FEATURES + CATEGORICAL_FEATURES``
    exactly; a mismatch would make the ColumnTransformer either fail or, worse,
    line features up against the wrong columns.
    """
    floor_ratio = np.nan
    if request.floor_num is not None and request.total_floors:
        floor_ratio = request.floor_num / request.total_floors

    row = {
        "log_area_sqft": np.log1p(request.area_sqft),
        "bathroom": request.bathroom,
        "balcony": request.balcony,
        "car_parking": request.car_parking,
        "floor_num": request.floor_num,
        "total_floors": request.total_floors,
        "floor_ratio": floor_ratio,
        "is_carpet_area": float(request.is_carpet_area),
        "parking_covered": float(request.parking_covered),
        "overlooking_garden": float(request.overlooking_garden),
        "overlooking_pool": float(request.overlooking_pool),
        "overlooking_main_road": float(request.overlooking_main_road),
        "location": normalize_category(request.location),
        "furnishing": normalize_category(request.furnishing),
        "transaction": normalize_category(request.transaction),
        "ownership": normalize_category(request.ownership),
        "facing": normalize_facing(request.facing),
    }
    frame = pd.DataFrame([row], columns=NUMERIC_FEATURES + CATEGORICAL_FEATURES)
    # Missing optionals arrive as None; the pipeline's SimpleImputer expects NaN.
    return frame.astype({column: "float64" for column in NUMERIC_FEATURES})
