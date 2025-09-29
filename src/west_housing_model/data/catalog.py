from __future__ import annotations

import os
from pathlib import Path
from typing import Mapping

import pandas as pd

from west_housing_model.data.schemas import (
    CONNECTOR_SCHEMAS,
    TABLE_SCHEMAS,
    validate_connector_schema,
    validate_table_schema,
)


def validate_table(table: str, frame: pd.DataFrame, *, lazy: bool = False) -> pd.DataFrame:
    """Validate canonical tables using the registered Pandera schemas."""

    return validate_table_schema(table, frame, lazy=lazy)


def validate_connector(source_id: str, frame: pd.DataFrame, *, lazy: bool = False) -> pd.DataFrame:
    """Validate connector payloads using the registered Pandera schemas."""

    return validate_connector_schema(source_id, frame, lazy=lazy)


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
    "CONNECTOR_SCHEMAS",
    "DATA_DICTIONARY",
    "TABLE_SCHEMAS",
    "failure_capture_path",
    "validate_connector",
    "validate_table",
]
