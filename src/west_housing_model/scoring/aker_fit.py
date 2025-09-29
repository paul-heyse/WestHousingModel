"""Aker Fit scoring engine.

Computes Aker Fit on a 0..100 scale from four pillar indices in 0..1 using
configurable weights. The function is pure and performs simple input hygiene:
- Missing pillars are treated as 0.0
- Pillar values are clamped to [0, 1]
- Output is rounded to nearest integer and clamped to [0, 100]
"""

from __future__ import annotations

from typing import Any, Mapping, Optional

import pandas as pd
from pandera import Column, DataFrameSchema

DEFAULT_PILLAR_WEIGHTS: Mapping[str, float] = {
    "pillar_uc": 0.25,
    "pillar_oa": 0.25,
    "pillar_ij": 0.25,
    "pillar_sc": 0.25,
}


PILLAR_SCHEMA: Any = DataFrameSchema(  # type: ignore[no-untyped-call]
    {
        "pillar_uc": Column(float, nullable=True, required=False),
        "pillar_oa": Column(float, nullable=True, required=False),
        "pillar_ij": Column(float, nullable=True, required=False),
        "pillar_sc": Column(float, nullable=True, required=False),
    },
    coerce=True,
    strict=False,
)


def validate_pillars(frame: pd.DataFrame) -> pd.DataFrame:
    """Validate pillar inputs with Pandera schema (lazy)."""

    return PILLAR_SCHEMA.validate(frame, lazy=True)


def _coerce_and_clamp(series: pd.Series, *, lower: float = 0.0, upper: float = 1.0) -> pd.Series:
    s = pd.to_numeric(series, errors="coerce").astype(float)
    return s.clip(lower=lower, upper=upper).fillna(0.0)


def _pillar(series_or_none: Optional[pd.Series]) -> pd.Series:
    if series_or_none is None:
        # Caller provides a DataFrame; when missing, construct a zero series of
        # appropriate length downstream. Here we return an empty Series to be
        # replaced by the caller.
        return pd.Series([], dtype=float)
    return _coerce_and_clamp(series_or_none)


def compute_aker_fit(
    pillars: pd.DataFrame,
    *,
    weights: Optional[Mapping[str, float]] = None,
    validate: bool = False,
) -> pd.Series:
    """Compute Aker Fit 0..100 from pillar indices (0..1).

    Parameters
    - pillars: DataFrame with columns `pillar_uc`, `pillar_oa`, `pillar_ij`, `pillar_sc` (any subset)
    - weights: optional mapping of weights for each pillar, will be merged over defaults
    """

    frame = validate_pillars(pillars) if validate else pillars

    w: dict[str, float] = dict(DEFAULT_PILLAR_WEIGHTS)
    if weights:
        w.update(weights)
    denom = float(sum(w.values()) or 1.0)

    # Build series for each pillar; if missing, use zero series.
    index = frame.index
    uc = (
        _pillar(frame["pillar_uc"]) if "pillar_uc" in frame.columns else pd.Series(0.0, index=index)
    )
    oa = (
        _pillar(frame["pillar_oa"]) if "pillar_oa" in frame.columns else pd.Series(0.0, index=index)
    )
    ij = (
        _pillar(frame["pillar_ij"]) if "pillar_ij" in frame.columns else pd.Series(0.0, index=index)
    )
    sc = (
        _pillar(frame["pillar_sc"]) if "pillar_sc" in frame.columns else pd.Series(0.0, index=index)
    )

    weighted = (
        uc * float(w["pillar_uc"])
        + oa * float(w["pillar_oa"])
        + ij * float(w["pillar_ij"])
        + sc * float(w["pillar_sc"])
    ) / denom
    return (weighted * 100.0).round().clip(lower=0, upper=100).astype("Int64")


__all__ = ["compute_aker_fit", "DEFAULT_PILLAR_WEIGHTS", "validate_pillars", "PILLAR_SCHEMA"]
