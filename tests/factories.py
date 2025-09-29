from __future__ import annotations

from datetime import datetime
from typing import Any, Dict

import pandas as pd


def make_place_base() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "place_id": ["p-1"],
            "geo_level": ["msa"],
            "geo_code": ["12345"],
            "name": ["Test Place"],
            "source_id": ["connector.place_context"],
            "public_land_acres_30min": [950.0],
            "broadband_gbps_flag": [True],
        }
    )


def make_place_components() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "amenities_15min_walk_count": [12],
            "avg_walk_time_to_top3_amenities": [10.0],
            "grocery_10min_drive_count": [5],
            "intersection_density": [110],
            "public_land_acres_30min": [950.0],
            "minutes_to_trailhead": [18.0],
            "msa_jobs_t12": [2.4],
            "msa_jobs_t36": [5.0],
            "slope_gt15_pct_within_10km": [3.5],
            "protected_land_within_10km_pct": [15.0],
            "permits_5plus_per_1k_hh_t12": [1.2],
            "broadband_gbps_flag": [1.0],
        }
    )


def make_site_base() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "property_id": ["s-1"],
            "place_id": ["p-1"],
            "latitude": [39.7],
            "longitude": [-104.9],
        }
    )


def make_site_hazards() -> pd.DataFrame:
    rows = [
        {
            "property_id": "s-1",
            "hazard_type": "in_sfha",
            "value": None,
            "flag": False,
            "as_of": datetime(2025, 2, 1),
            "source_id": "connector.fema",
        },
        {
            "property_id": "s-1",
            "hazard_type": "wildfire_risk_percentile",
            "value": 82,
            "flag": None,
            "as_of": datetime(2025, 2, 1),
            "source_id": "connector.usfs_wildfire",
        },
        {
            "property_id": "s-1",
            "hazard_type": "pga_10in50_g",
            "value": 0.18,
            "flag": None,
            "as_of": datetime(2025, 2, 1),
            "source_id": "connector.usgs_designmaps",
        },
        {
            "property_id": "s-1",
            "hazard_type": "winter_storms_10yr_county",
            "value": 12,
            "flag": None,
            "as_of": datetime(2025, 2, 1),
            "source_id": "connector.noaa_storms",
        },
        {
            "property_id": "s-1",
            "hazard_type": "hdd_annual",
            "value": 6000,
            "flag": None,
            "as_of": datetime(2025, 2, 1),
            "source_id": "connector.noaa_normals",
        },
        {
            "property_id": "s-1",
            "hazard_type": "cdd_annual",
            "value": 900,
            "flag": None,
            "as_of": datetime(2025, 2, 1),
            "source_id": "connector.noaa_normals",
        },
        {
            "property_id": "s-1",
            "hazard_type": "rail_within_300m_flag",
            "value": None,
            "flag": True,
            "as_of": datetime(2025, 2, 1),
            "source_id": "connector.transport",
        },
        {
            "property_id": "s-1",
            "hazard_type": "broadband_gbps_flag",
            "value": None,
            "flag": True,
            "as_of": datetime(2025, 2, 1),
            "source_id": "connector.fcc",
        },
        {
            "property_id": "s-1",
            "hazard_type": "minutes_to_trailhead",
            "value": 20,
            "flag": None,
            "as_of": datetime(2025, 2, 1),
            "source_id": "connector.osm",
        },
    ]
    return pd.DataFrame(rows)


def make_ops_rows() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "property_id": ["s-1"],
            "as_of": [datetime(2025, 2, 1)],
            "eia_state": ["CO"],
            "eia_res_price_cents_per_kwh": [13.5],
            "broadband_gbps_flag": [True],
            "zoning_context_note": ["MF allowed"],
        }
    )


def make_scenario_payload() -> Dict[str, Any]:
    return {
        "scenario_id": "scn-001",
        "property_id": "s-1",
        "as_of": "2025-03-01",
        "place_features": {
            "aker_market_fit": 74,
            "msa_jobs_t12": 2.4,
            "permits_5plus_per_1k_hh_t12": 40,
            "source_id": "connector.place_context",
            "as_of": "2025-01-01",
        },
        "site_features": {
            "in_sfha": False,
            "wildfire_risk_percentile": 82,
            "pga_10in50_g": 0.18,
            "winter_storms_10yr_county": 12,
            "hdd_annual": 6000,
            "cdd_annual": 900,
            "source_id": "site.features",
            "as_of": "2025-02-01",
        },
        "ops_features": {
            "utility_rate_note": "Utilities (CO RES): 13.5 c/kWh",
            "broadband_gbps_flag": True,
            "source_id": "ops.features",
            "as_of": "2025-02-01",
        },
        "user_overrides": {
            "units": 24,
            "rent_baseline": 1800,
            "base_opex_per_unit_year": 3200,
            "total_cost": 3_500_000,
            "cap_low": 0.06,
            "cap_base": 0.065,
            "cap_high": 0.07,
            "g_base": 0.025,
            "rent_to_income": 0.28,
            "affordability_overridden": False,
        },
    }
