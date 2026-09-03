"""Turning this dataset's text columns into numbers.

Every rule here came from profiling the actual file rather than from the column
descriptions: ``Amount(in rupees)`` is ``"42 Lac"`` / ``"1.40 Cr"`` / ``"Call for
Price"``, areas carry ten different units, ``Floor`` is ``"3 out of 10"`` with
``"Ground"`` and basements mixed in, and ``Car Parking`` is ``"1 Covered,"``.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

#: One lakh, in rupees.
LAC = 100_000.0
#: One crore, in rupees.
CR = 10_000_000.0

#: Square feet per unit, for every area unit that appears in the file.
AREA_UNITS: dict[str, float] = {
    "sqft": 1.0,
    "sqyrd": 9.0,
    "sqm": 10.7639104,
    "acre": 43_560.0,
    "marla": 272.25,
    "kanal": 5_445.0,
    "ground": 2_400.0,
    "cent": 435.6,
    "bigha": 27_000.0,
    "biswa1": 1_350.0,
    "biswa2": 1_350.0,
    "aankadam": 72.0,
    "guntha": 1_089.0,
    "hectare": 107_639.104,
    "rood": 10_890.0,
    "chatak": 180.0,
    "perch": 272.25,
    "are": 1_076.39104,
}

#: Numeric model inputs, in a fixed order.
NUMERIC_FEATURES = [
    "log_area_sqft",
    "bathroom",
    "balcony",
    "car_parking",
    "floor_num",
    "total_floors",
    "floor_ratio",
    "is_carpet_area",
    "parking_covered",
    "overlooking_garden",
    "overlooking_pool",
    "overlooking_main_road",
]

#: One-hot encoded model inputs, in a fixed order.
CATEGORICAL_FEATURES = ["location", "furnishing", "transaction", "ownership", "facing"]


def parse_amount(raw: object) -> float | None:
    """Parse ``"42 Lac"``, ``"1.40 Cr"`` or ``"3,50,000"`` into rupees.

    Returns ``None`` for ``"Call for Price"``, blanks and anything else
    unparseable: a listing with no usable price cannot be a training row.
    """
    if not isinstance(raw, str):
        return None
    s = raw.strip().lower()
    if not s or "call" in s:
        return None
    if s.endswith("lac"):
        multiplier, number = LAC, s[:-3]
    elif s.endswith("cr"):
        multiplier, number = CR, s[:-2]
    else:
        multiplier, number = 1.0, s
    try:
        n = float(number.replace(",", "").strip())
    except ValueError:
        return None
    return n * multiplier if math.isfinite(n) and n > 0 else None


def parse_area_sqft(raw: object) -> float | None:
    """Parse ``"1200 sqft"``, ``"140 sqyrd"``, ``"90 sqm"`` into square feet.

    An unrecognised unit returns ``None`` rather than a silently wrong number.
    """
    if not isinstance(raw, str):
        return None
    parts = raw.strip().lower().split()
    if not parts:
        return None
    try:
        n = float(parts[0].replace(",", ""))
    except ValueError:
        return None
    unit = parts[1] if len(parts) > 1 else "sqft"
    factor = AREA_UNITS.get(unit)
    if factor is None:
        return None
    sqft = n * factor
    return sqft if math.isfinite(sqft) and sqft > 0 else None


@dataclass(frozen=True)
class Floor:
    """Parsed ``Floor``: the storey, and how many the building has."""

    number: int | None = None
    total: int | None = None


def parse_floor(raw: object) -> Floor:
    """Parse ``"3 out of 10"``, ``"Ground out of 4"``, ``"Basement"``, ``"2"``."""
    if not isinstance(raw, str):
        return Floor()
    s = raw.strip().lower()
    if not s:
        return Floor()
    head, _, tail = s.partition(" out of ")
    head = head.strip()
    named = {"ground": 0, "lower basement": -2, "basement": -1, "upper basement": -1}
    if head in named:
        number = named[head]
    else:
        try:
            number = int(head)
        except ValueError:
            number = None
    try:
        total = int(tail.strip()) if tail else None
    except ValueError:
        total = None
    return Floor(number, total)


def parse_count(raw: object) -> float | None:
    """Parse a small count column such as ``Bathroom`` or ``Balcony``.

    ``"> 10"`` becomes 11, which keeps the ordering meaningful without inventing
    a precise value the file does not have.
    """
    if not isinstance(raw, str):
        return None
    s = raw.strip()
    if not s:
        return None
    if s.startswith(">"):
        try:
            return float(s[1:].strip()) + 1.0
        except ValueError:
            return None
    try:
        return float(s)
    except ValueError:
        return None


@dataclass(frozen=True)
class Parking:
    """Parsed ``Car Parking``: how many spaces, and whether any is covered."""

    count: float | None = None
    covered: bool = False


def parse_parking(raw: object) -> Parking:
    """Parse ``"1 Covered"``, ``"2 Open"``, ``"1 Covered,"``."""
    if not isinstance(raw, str):
        return Parking()
    s = raw.strip().rstrip(",").strip().lower()
    if not s:
        return Parking()
    try:
        count = float(s.split()[0])
    except (ValueError, IndexError):
        count = None
    return Parking(count, "covered" in s)


def parse_overlooking(raw: object) -> tuple[bool, bool, bool]:
    """The three things ``overlooking`` can mention, as independent flags.

    The column is a comma-separated set in an inconsistent order, so one-hot
    encoding the raw string would make 20 categories out of 3 facts.
    """
    s = raw.lower() if isinstance(raw, str) else ""
    return "garden" in s, "pool" in s, "main road" in s


def normalize_facing(raw: object) -> str:
    """Normalise ``facing``, which spells one direction two ways."""
    if not isinstance(raw, str):
        return "missing"
    s = raw.strip().lower().replace("-", "").replace(" ", "")
    return s or "missing"


def normalize_category(raw: object) -> str:
    """Normalise a categorical value, mapping blanks to their own category."""
    if not isinstance(raw, str):
        return "missing"
    return raw.strip().lower() or "missing"


def percentile(sorted_values: np.ndarray, p: float) -> float:
    """The value at a percentile, by nearest rank.

    Deliberately not ``numpy.percentile``: this matches the Rust
    implementation's definition exactly, so the two projects trim the same rows
    and their row counts can be compared.
    """
    if len(sorted_values) == 0:
        return float("nan")
    idx = int(round((p / 100.0) * (len(sorted_values) - 1)))
    return float(sorted_values[min(idx, len(sorted_values) - 1)])


@dataclass
class CleaningLog:
    """What cleaning removed, for the notebook's write-up."""

    total: int = 0
    no_price: int = 0
    no_area: int = 0
    duplicates: int = 0
    outliers: int = 0
    from_carpet: int = 0
    ppsf_low: float = float("nan")
    ppsf_high: float = float("nan")

    def as_rows(self) -> list[tuple[str, int]]:
        """The cleaning funnel, as table rows."""
        kept = self.total - self.no_price - self.no_area - self.duplicates - self.outliers
        return [
            ("raw", self.total),
            ("dropped: no usable price", -self.no_price),
            ("dropped: no usable area", -self.no_area),
            ("dropped: duplicate listings", -self.duplicates),
            ("dropped: price-per-sqft outliers", -self.outliers),
            ("kept", kept),
        ]


#: Columns whose equality defines "the same listing", for de-duplication.
_DEDUP_KEY = ["price", *NUMERIC_FEATURES, *CATEGORICAL_FEATURES]


def build_frame(raw: pd.DataFrame, dedup: bool = True) -> tuple[pd.DataFrame, CleaningLog]:
    """Clean every row, optionally de-duplicate, and trim price-per-sqft outliers.

    ``dedup`` is not optional in practice: three fifths of this file is repeat
    listings, and a listing on both sides of the split turns the test set into a
    memory test. It is a parameter only so the notebook can measure what leaving
    them in would have cost.
    """
    log = CleaningLog(total=len(raw))
    df = pd.DataFrame(index=raw.index)

    df["price"] = raw["Amount(in rupees)"].map(parse_amount)

    # Carpet area is the honest number; super area includes shared space, so
    # prefer carpet and flag which one each row used.
    carpet = raw["Carpet Area"].map(parse_area_sqft)
    super_area = raw["Super Area"].map(parse_area_sqft)
    df["is_carpet_area"] = carpet.notna().astype(float)
    area = carpet.fillna(super_area)

    floors = raw["Floor"].map(parse_floor)
    parking = raw["Car Parking"].map(parse_parking)
    overlooking = raw["overlooking"].map(parse_overlooking)

    df["bathroom"] = raw["Bathroom"].map(parse_count)
    df["balcony"] = raw["Balcony"].map(parse_count)
    df["car_parking"] = parking.map(lambda p: p.count)
    df["parking_covered"] = parking.map(lambda p: float(p.covered))
    df["floor_num"] = floors.map(lambda f: f.number)
    df["total_floors"] = floors.map(lambda f: f.total)
    df["overlooking_garden"] = overlooking.map(lambda o: float(o[0]))
    df["overlooking_pool"] = overlooking.map(lambda o: float(o[1]))
    df["overlooking_main_road"] = overlooking.map(lambda o: float(o[2]))

    df["location"] = raw["location"].map(normalize_category)
    df["furnishing"] = raw["Furnishing"].map(normalize_category)
    df["transaction"] = raw["Transaction"].map(normalize_category)
    df["ownership"] = raw["Ownership"].map(normalize_category)
    df["facing"] = raw["facing"].map(normalize_facing)

    # Drop rows with no target, then rows with no area, counting each separately.
    no_price = df["price"].isna()
    log.no_price = int(no_price.sum())
    df, area = df[~no_price], area[~no_price]

    no_area = area.isna()
    log.no_area = int(no_area.sum())
    df, area = df[~no_area], area[~no_area]

    df["area_sqft"] = area
    df["log_area_sqft"] = np.log1p(area)
    df["floor_ratio"] = np.where(
        df["total_floors"].notna() & (df["total_floors"] > 0),
        df["floor_num"] / df["total_floors"],
        np.nan,
    )
    df["price_per_sqft"] = df["price"] / df["area_sqft"]
    log.from_carpet = int(df["is_carpet_area"].sum())

    if dedup:
        before = len(df)
        df = df.drop_duplicates(subset=_DEDUP_KEY)
        log.duplicates = before - len(df)

    # Trim absurd rates from both tails: a 1,000 rupee/sqft flat in Mumbai and a
    # 900,000 rupee/sqft one are both data entry, not signal.
    rates = np.sort(df["price_per_sqft"].to_numpy())
    log.ppsf_low = percentile(rates, 1.0)
    log.ppsf_high = percentile(rates, 99.0)
    before = len(df)
    df = df[df["price_per_sqft"].between(log.ppsf_low, log.ppsf_high)]
    log.outliers = before - len(df)

    return df.reset_index(drop=True), log
