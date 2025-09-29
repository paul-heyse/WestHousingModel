from __future__ import annotations

import argparse
from pathlib import Path

from west_housing_model.cli import main as cli_main


def test_validate_ok_with_mocked_registry(monkeypatch, capsys) -> None:
    monkeypatch.setattr(cli_main, "load_registry", lambda: {"connector.place_context": {}})
    args = argparse.Namespace(json=True, offline=False, cache_root=None)
    rc = cli_main.cmd_validate(args)
    assert rc == 0
    out = capsys.readouterr().out
    assert '"action": "validate"' in out
    assert '"registry_ok": true' in out
    assert '"sources"' in out


def test_features_site_ok(tmp_path: Path) -> None:
    base = tmp_path / "base.csv"
    hazards = tmp_path / "hazards.csv"
    out = tmp_path / "site.parquet"
    base.write_text("property_id,place_id,latitude,longitude\np1,pl1,39.7,-104.9\n")
    hazards.write_text(
        "property_id,hazard_type,value,flag,as_of,source_id\n"
        "p1,in_sfha,,True,2025-01-01,fema_nfhl\n"
    )
    args = argparse.Namespace(
        type="site",
        base=str(base),
        hazards=str(hazards),
        components=None,
        output=str(out),
        json=True,
        offline=False,
        cache_root=None,
    )
    rc = cli_main.cmd_features(args)
    assert rc == 0
    assert out.exists()


def test_features_place_ok(tmp_path: Path) -> None:
    base = tmp_path / "place_base.csv"
    comps = tmp_path / "place_components.csv"
    out = tmp_path / "place.parquet"
    base.write_text(
        "place_id,geo_level,geo_code,name,source_id\np-001,msa,12345,Test,connector.place_context\n"
    )
    comps.write_text(
        "amenities_15min_walk_count,avg_walk_time_to_top3_amenities,grocery_10min_drive_count,intersection_density,public_land_acres_30min,minutes_to_trailhead,msa_jobs_t12,msa_jobs_t36,slope_gt15_pct_within_10km,protected_land_within_10km_pct,permits_5plus_per_1k_hh_t12\n"
        "10,15.0,5,100,1000,20,1.5,4.0,5.0,20.0,2.0\n"
    )
    args = argparse.Namespace(
        type="place",
        base=str(base),
        hazards=None,
        components=str(comps),
        output=str(out),
        json=True,
        offline=False,
        cache_root=None,
    )
    rc = cli_main.cmd_features(args)
    assert rc == 0
    assert out.exists()
