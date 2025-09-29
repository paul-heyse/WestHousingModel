from __future__ import annotations

from pathlib import Path

from west_housing_model.cli.main import main


def test_features_golden_snapshot(tmp_path: Path) -> None:
    # Tiny input for golden artifact generation
    base = tmp_path / "place_base.csv"
    comps = tmp_path / "place_components.csv"
    out = tmp_path / "place.parquet"
    base.write_text(
        "place_id,geo_level,geo_code,name,source_id\n"
        "p-001,msa,12345,Test,connector.place_context\n"
    )
    comps.write_text(
        "amenities_15min_walk_count,avg_walk_time_to_top3_amenities,grocery_10min_drive_count,intersection_density,public_land_acres_30min,minutes_to_trailhead,msa_jobs_t12,msa_jobs_t36,slope_gt15_pct_within_10km,protected_land_within_10km_pct,permits_5plus_per_1k_hh_t12\n"
        "10,15.0,5,100,1000,20,1.5,4.0,5.0,20.0,2.0\n"
    )
    rc = main(
        [
            "features",
            "--type",
            "place",
            "--base",
            str(base),
            "--components",
            str(comps),
            "--output",
            str(out),
        ]
    )
    assert rc == 0
    assert out.exists()
