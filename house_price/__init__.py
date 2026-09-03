"""Domain code shared by the notebook and the API.

Keeping the column parsers here is what stops the service from cleaning a
listing differently than the notebook did. The scaler and the encoder live
inside the exported scikit-learn Pipeline for the same reason.
"""

from house_price.model import ClippedRegressor, SmearedRegressor
from house_price.cleaning import (
    AREA_UNITS,
    CATEGORICAL_FEATURES,
    NUMERIC_FEATURES,
    build_frame,
    normalize_category,
    normalize_facing,
    parse_amount,
    parse_area_sqft,
    parse_count,
    parse_floor,
    parse_overlooking,
    parse_parking,
    percentile,
)

__all__ = [
    "AREA_UNITS",
    "ClippedRegressor",
    "SmearedRegressor",
    "CATEGORICAL_FEATURES",
    "NUMERIC_FEATURES",
    "build_frame",
    "normalize_category",
    "normalize_facing",
    "parse_amount",
    "parse_area_sqft",
    "parse_count",
    "parse_floor",
    "parse_overlooking",
    "parse_parking",
    "percentile",
]
