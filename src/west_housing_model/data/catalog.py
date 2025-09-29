from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Mapping, Sequence

import pandas as pd

from west_housing_model.core.exceptions import SchemaError


@dataclass(frozen=True)
class TableSchema:
    name: str
    required_columns: Sequence[str]


_TABLE_SCHEMAS: Mapping[str, TableSchema] = {
    "place_features": TableSchema(
        name="place_features",
        required_columns=(
            "place_id",
            "geo_level",
            "geo_code",
            "name",
            "as_of",
            "source_id",
            "pillar_uc",
            "pillar_oa",
            "pillar_ij",
            "pillar_sc",
            "aker_market_fit",
        ),
    ),
    "ops_features": TableSchema(
        name="ops_features",
        required_columns=(
            "property_id",
            "as_of",
            "source_id",
            "utility_rate_note",
            "broadband_gbps_flag",
            "zoning_context_note",
            "utilities_scaler",
            "hud_fmr_2br",
        ),
    ),
    "site_features": TableSchema(
        name="site_features",
        required_columns=(
            "property_id",
            "place_id",
            "latitude",
            "longitude",
            "as_of",
            "source_id",
            "in_sfha",
            "wildfire_risk_percentile",
            "pga_10in50_g",
            "winter_storms_10yr_county",
            "minutes_to_trailhead",
            "broadband_gbps_flag",
        ),
    ),
    "valuation_outputs": TableSchema(
        name="valuation_outputs",
        required_columns=(
            "scenario_id",
            "property_id",
            "as_of",
            "noistab",
            "cap_rate_low",
            "cap_rate_base",
            "cap_rate_high",
            "value_low",
            "value_base",
            "value_high",
            "yoc_base",
            "irr_5yr_low",
            "irr_5yr_base",
            "irr_5yr_high",
            "dscr_proxy",
            "insurance_uplift",
            "utilities_scaler",
            "aker_fit",
            "deal_quality",
            "sensitivity_matrix",
            "source_manifest",
        ),
    ),
}


_CONNECTOR_SCHEMAS: Mapping[str, TableSchema] = {
    "connector.place_context": TableSchema(
        name="connector.place_context",
        required_columns=("place_id", "metric", "value", "observed_at", "source_id"),
    ),
    "connector.usfs_wildfire": TableSchema(
        name="connector.usfs_wildfire",
        required_columns=("geo_id", "wildfire_risk_percentile", "observed_at", "source_id"),
    ),
    "connector.usgs_designmaps": TableSchema(
        name="connector.usgs_designmaps",
        required_columns=("lat", "lon", "pga_10in50_g", "observed_at", "source_id"),
    ),
    "connector.noaa_storm_events": TableSchema(
        name="connector.noaa_storm_events",
        required_columns=("county_id", "winter_storms_10yr_county", "observed_at", "source_id"),
    ),
    "connector.pad_us": TableSchema(
        name="connector.pad_us",
        required_columns=("place_id", "public_land_acres_30min", "observed_at", "source_id"),
    ),
    "connector.fcc_bdc": TableSchema(
        name="connector.fcc_bdc",
        required_columns=("geo_id", "broadband_gbps_flag", "observed_at", "source_id"),
    ),
    "connector.hud_fmr": TableSchema(
        name="connector.hud_fmr",
        required_columns=("geo_id", "hud_fmr_2br", "observed_at", "source_id"),
    ),
    "connector.eia_v2": TableSchema(
        name="connector.eia_v2",
        required_columns=("state", "res_price_cents_per_kwh", "observed_at", "source_id"),
    ),
    "connector.usfs_trails": TableSchema(
        name="connector.usfs_trails",
        required_columns=("place_id", "minutes_to_trailhead", "observed_at", "source_id"),
    ),
    "connector.usgs_epqs": TableSchema(
        name="connector.usgs_epqs",
        required_columns=("place_id", "slope_gt15_pct_within_10km", "observed_at", "source_id"),
    ),
    "connector.census_acs": TableSchema(
        name="connector.census_acs",
        required_columns=(
            "geo_id",
            "geo_level",
            "median_household_income",
            "observed_at",
            "source_id",
        ),
    ),
}


def _missing_columns(frame: pd.DataFrame, required: Iterable[str]) -> list[str]:
    present = set(frame.columns)
    return [column for column in required if column not in present]


def _raise_schema_error(object_name: str, missing: list[str]) -> None:
    raise SchemaError(
        f"{object_name} missing required columns: {', '.join(missing)}",
        context={"object": object_name, "missing": missing},
    )


def validate_table(
    table: str, frame: pd.DataFrame, *, lazy: bool = False
) -> pd.DataFrame:  # noqa: ARG001
    schema = _TABLE_SCHEMAS.get(table)
    if schema is None:
        return frame
    missing = _missing_columns(frame, schema.required_columns)
    if missing:
        _raise_schema_error(schema.name, missing)
    return frame


def validate_connector(
    source_id: str, frame: pd.DataFrame, *, lazy: bool = False
) -> pd.DataFrame:  # noqa: ARG001
    schema = _CONNECTOR_SCHEMAS.get(source_id)
    if schema is None:
        return frame
    missing = _missing_columns(frame, schema.required_columns)
    if missing:
        _raise_schema_error(schema.name, missing)
    return frame


def failure_capture_path(source_id: str) -> Path:
    """Directory where connector failure payloads/logs are written.

    Honors env var WEST_HOUSING_MODEL_FAILURE_CACHE; otherwise uses CWD/failures.
    """

    root = os.getenv("WEST_HOUSING_MODEL_FAILURE_CACHE")
    base = Path(root) if root else Path.cwd() / "failures"
    path = base / source_id
    path.mkdir(parents=True, exist_ok=True)
    return path


DATA_DICTIONARY: Mapping[str, Mapping[str, Mapping[str, str]]] = {
    "place_features": {
        "aker_market_fit": {
            "description": "Composite 0-100 score from UC/OA/IJ/SC pillars",
            "unit": "index",
            "source": "scoring.aker_fit.compute_aker_fit",
        },
        "pillar_uc": {
            "description": "Urban Convenience pillar percentile (0-1)",
            "unit": "ratio",
            "source": "features.place.compute_pillars",
        },
        "pillar_oa": {
            "description": "Outdoor Access pillar percentile (0-1)",
            "unit": "ratio",
            "source": "features.place.compute_pillars",
        },
        "pillar_ij": {
            "description": "Innovation Jobs pillar percentile (0-1)",
            "unit": "ratio",
            "source": "features.place.compute_pillars",
        },
        "pillar_sc": {
            "description": "Supply Constraints pillar percentile (0-1)",
            "unit": "ratio",
            "source": "features.place.compute_pillars",
        },
        "public_land_acres_30min": {
            "description": "Protected acres reachable within 30-minute drive",
            "unit": "acres",
            "source": "connector.pad_us",
        },
        "broadband_gbps_flag": {
            "description": "Indicator for ≥1Gbps broadband availability",
            "unit": "boolean",
            "source": "connector.fcc_bdc",
        },
    },
    "site_features": {
        "wildfire_risk_percentile": {
            "description": "USFS wildfire risk percentile (0-100)",
            "unit": "percentile",
            "source": "connector.usfs_wildfire",
        },
        "pga_10in50_g": {
            "description": "Peak ground acceleration (10% in 50yr) in g",
            "unit": "g",
            "source": "connector.usgs_designmaps",
        },
        "winter_storms_10yr_county": {
            "description": "10-year winter storm event count (county)",
            "unit": "count",
            "source": "connector.noaa_storm_events",
        },
        "minutes_to_trailhead": {
            "description": "Proxy minutes to nearest trailhead",
            "unit": "minutes",
            "source": "connector.usfs_trails",
        },
        "broadband_gbps_flag": {
            "description": "Site-level broadband ≥1Gbps flag",
            "unit": "boolean",
            "source": "connector.fcc_bdc",
        },
    },
    "ops_features": {
        "utility_rate_note": {
            "description": "Text note summarising utility rates",
            "unit": "text",
            "source": "connector.eia_v2",
        },
        "utilities_scaler": {
            "description": "Scalar applied to baseline OpEx for utilities",
            "unit": "ratio",
            "source": "connector.eia_v2",
        },
        "broadband_gbps_flag": {
            "description": "Broadband ≥1Gbps availability flag",
            "unit": "boolean",
            "source": "connector.fcc_bdc",
        },
        "hud_fmr_2br": {
            "description": "HUD Fair Market Rent (2BR) reference",
            "unit": "USD/month",
            "source": "connector.hud_fmr",
        },
    },
}


__all__ = [
    "DATA_DICTIONARY",
    "TableSchema",
    "failure_capture_path",
    "validate_connector",
    "validate_table",
]
