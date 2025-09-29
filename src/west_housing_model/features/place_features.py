"""Place-level feature builders (pure, deterministic) with schema validation.

This module provides two layers of helpers:
1) Low-level utilities to compute pillar indices from component metrics
2) Orchestration that assembles the canonical `place_features` table and validates it

All functions are pure and do not perform any I/O. Provenance sidecars can be
derived alongside outputs using the helper returned by `make_provenance_sidecar`.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, MutableMapping, Optional

import numpy as np
import pandas as pd

from west_housing_model.data.catalog import validate_table
from west_housing_model.scoring.aker_fit import compute_aker_fit
from west_housing_model.settings import get_pillar_weights


def _percentile(series: pd.Series) -> pd.Series:
    """Compute rank-based percentiles in [0, 1] with mid-rank handling.

    NaNs are preserved.
    """

    s = series.astype(float)
    mask = s.notna()
    if mask.sum() == 0:
        return s
    ranks = s[mask].rank(method="average", pct=True)
    out = pd.Series(index=s.index, dtype=float)
    out.loc[mask] = ranks
    out.loc[~mask] = np.nan
    return out


def _normalize_component(series: pd.Series, *, higher_is_better: bool = True) -> pd.Series:
    """Normalize a component to [0, 1] using percentiles.

    If `higher_is_better` is False, the scale is inverted.
    """

    pct = _percentile(series)
    if higher_is_better:
        return pct
    return 1.0 - pct


def compute_pillars(
    components: pd.DataFrame,
    *,
    uc_cols: Mapping[str, bool],
    oa_cols: Mapping[str, bool],
    ij_cols: Mapping[str, bool],
    sc_cols: Mapping[str, bool],
) -> pd.DataFrame:
    """Compute pillar indices (0..1) from component columns.

    Parameters map column name -> higher_is_better flag.
    Columns not present are ignored.
    """

    def pillar_from(mapping: Mapping[str, bool]) -> pd.Series:
        normalized: list[pd.Series] = []
        for col, hib in mapping.items():
            if col in components.columns:
                normalized.append(_normalize_component(components[col], higher_is_better=hib))
        if not normalized:
            return pd.Series(np.nan, index=components.index, dtype=float)
        arr = pd.concat(normalized, axis=1)
        return arr.mean(axis=1, skipna=True)

    result = pd.DataFrame(index=components.index)
    result["pillar_uc"] = pillar_from(uc_cols)
    result["pillar_oa"] = pillar_from(oa_cols)
    result["pillar_ij"] = pillar_from(ij_cols)
    result["pillar_sc"] = pillar_from(sc_cols)
    return result


def compute_aker_market_fit(
    pillars: pd.DataFrame, *, weights: Optional[Mapping[str, float]] = None
) -> pd.Series:
    """Compute Aker Market Fit on 0..100 scale from pillar indices (0..1)."""

    base_weights = dict(get_pillar_weights())
    if weights:
        base_weights.update(weights)

    frame = pillars.reindex(columns=list(base_weights.keys()))
    scores = compute_aker_fit(frame, weights=base_weights)
    return scores


@dataclass(frozen=True)
class Provenance:
    """Provenance mapping for output columns."""

    columns: Mapping[str, Mapping[str, Any]]


def make_provenance_sidecar(
    *,
    source_by_column: Mapping[str, str],
    as_of_by_column: Mapping[str, str | None],
    transformation_by_column: Optional[Mapping[str, str]] = None,
) -> Provenance:
    entries: MutableMapping[str, Mapping[str, Any]] = {}
    for col, source in source_by_column.items():
        entries[col] = {
            "source_id": source,
            "as_of": as_of_by_column.get(col),
            "transformation": (transformation_by_column or {}).get(col, "percentile->mean"),
        }
    return Provenance(columns=dict(entries))


def assemble_place_features(
    base: pd.DataFrame,
    pillars: pd.DataFrame,
    *,
    as_of: Optional[pd.Timestamp] = None,
) -> pd.DataFrame:
    """Assemble canonical place_features and validate.

    base must contain: place_id, geo_level, geo_code, name, source_id
    pillars must contain: pillar_uc, pillar_oa, pillar_ij, pillar_sc
    """

    # Start with required base columns
    combined = base[["place_id", "geo_level", "geo_code", "name", "source_id"]].copy(deep=True)
    # Pass through context components if present
    for passthrough in ("public_land_acres_30min", "broadband_gbps_flag"):
        if passthrough in base.columns:
            combined[passthrough] = base[passthrough]
    # Join pillar indices
    combined = combined.join(pillars[["pillar_uc", "pillar_oa", "pillar_ij", "pillar_sc"]])
    if as_of is not None:
        combined["as_of"] = as_of
    else:
        # Ensure as_of exists for schema validation; allow NA when not supplied
        if "as_of" not in combined.columns:
            combined["as_of"] = pd.NaT
    # Compute Aker Fit using scoring engine (keeps return type Int64)
    weights = get_pillar_weights()
    combined["aker_market_fit"] = compute_aker_market_fit(
        combined[["pillar_uc", "pillar_oa", "pillar_ij", "pillar_sc"]],
        weights=weights,
    )
    return validate_table("place_features", combined)


def build_place_features_from_components(
    base: pd.DataFrame,
    components: pd.DataFrame,
    *,
    as_of: Optional[pd.Timestamp] = None,
) -> pd.DataFrame:
    """High-level helper: components -> pillars -> place_features (validated).

    The `components` frame is expected to include columns referenced in the
    four pillar mappings below. Missing columns are ignored.
    """

    uc_cols = {
        # Higher is better
        "amenities_15min_walk_count": True,
        "grocery_10min_drive_count": True,
        # Lower is better
        "avg_walk_time_to_top3_amenities": False,
        "intersection_density": True,
        # Broadband availability boosts UC convenience slightly
        "broadband_gbps_flag": True,
    }
    oa_cols = {
        "public_land_acres_30min": True,
        "minutes_to_trailhead": False,
    }
    ij_cols = {
        "msa_jobs_t12": True,
        "msa_jobs_t36": True,
    }
    sc_cols = {
        "slope_gt15_pct_within_10km": True,
        "protected_land_within_10km_pct": True,
        "permits_5plus_per_1k_hh_t12": False,
    }
    pillars = compute_pillars(
        components, uc_cols=uc_cols, oa_cols=oa_cols, ij_cols=ij_cols, sc_cols=sc_cols
    )
    return assemble_place_features(base, pillars, as_of=as_of)


def build_place_features(frame: pd.DataFrame) -> pd.DataFrame:
    """Validate and return canonical place features (pass-through).

    This exists for compatibility with callers that already produce a fully
    assembled `place_features` frame. Prefer `build_place_features_from_components`.
    """

    return validate_table("place_features", pd.DataFrame(frame))


__all__ = [
    "Provenance",
    "assemble_place_features",
    "build_place_features",
    "build_place_features_from_components",
    "compute_aker_market_fit",
    "compute_pillars",
    "make_provenance_sidecar",
]
