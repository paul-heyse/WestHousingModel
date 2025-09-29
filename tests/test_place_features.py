from __future__ import annotations

import pandas as pd

from west_housing_model.features.place_features import (
    assemble_place_features,
    build_place_features_from_components,
    compute_aker_market_fit,
    compute_pillars,
)


def _base_row() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "place_id": ["p-001"],
            "geo_level": ["msa"],
            "geo_code": ["12345"],
            "name": ["Example"],
            "source_id": ["connector.place_context"],
        }
    )


def test_compute_pillars_and_aker_fit() -> None:
    components = pd.DataFrame(
        {
            "amenities_15min_walk_count": [10, 30, 20],
            "avg_walk_time_to_top3_amenities": [15.0, 12.0, 20.0],
            "grocery_10min_drive_count": [5, 7, 6],
            "intersection_density": [100, 120, 110],
            "public_land_acres_30min": [1000, 2000, 1500],
            "minutes_to_trailhead": [20, 15, 25],
            "msa_jobs_t12": [1.5, 2.5, 2.0],
            "msa_jobs_t36": [4.0, 6.0, 5.0],
            "slope_gt15_pct_within_10km": [5.0, 15.0, 10.0],
            "protected_land_within_10km_pct": [20.0, 30.0, 25.0],
            "permits_5plus_per_1k_hh_t12": [2.0, 4.0, 3.0],
        }
    )
    pillars = compute_pillars(
        components,
        uc_cols={
            "amenities_15min_walk_count": True,
            "avg_walk_time_to_top3_amenities": False,
            "grocery_10min_drive_count": True,
            "intersection_density": True,
        },
        oa_cols={"public_land_acres_30min": True, "minutes_to_trailhead": False},
        ij_cols={"msa_jobs_t12": True, "msa_jobs_t36": True},
        sc_cols={
            "slope_gt15_pct_within_10km": True,
            "protected_land_within_10km_pct": True,
            "permits_5plus_per_1k_hh_t12": False,
        },
    )
    assert set(pillars.columns) == {"pillar_uc", "pillar_oa", "pillar_ij", "pillar_sc"}
    aker = compute_aker_market_fit(pillars)
    assert aker.between(0, 100).all()


def test_build_place_features_from_components_validates() -> None:
    base = _base_row()
    components = pd.DataFrame(
        {
            "amenities_15min_walk_count": [10],
            "avg_walk_time_to_top3_amenities": [15.0],
            "grocery_10min_drive_count": [5],
            "intersection_density": [100],
            "public_land_acres_30min": [1000],
            "minutes_to_trailhead": [20],
            "msa_jobs_t12": [1.5],
            "msa_jobs_t36": [4.0],
            "slope_gt15_pct_within_10km": [5.0],
            "protected_land_within_10km_pct": [20.0],
            "permits_5plus_per_1k_hh_t12": [2.0],
        }
    )
    out = build_place_features_from_components(base, components)
    assert set(out.columns) >= {
        "place_id",
        "geo_level",
        "geo_code",
        "name",
        "pillar_uc",
        "pillar_oa",
        "pillar_ij",
        "pillar_sc",
        "aker_market_fit",
        "source_id",
    }


def test_assemble_place_features_validates_complete_shape() -> None:
    base = _base_row()
    pillars = pd.DataFrame(
        {
            "pillar_uc": [0.5],
            "pillar_oa": [0.5],
            "pillar_ij": [0.5],
            "pillar_sc": [0.5],
        }
    )
    out = assemble_place_features(base, pillars)
    assert out.loc[0, "aker_market_fit"] == 50
