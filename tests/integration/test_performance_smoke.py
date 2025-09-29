from __future__ import annotations

import time

import pandas as pd

from west_housing_model.cli.main import main as cli_main
from west_housing_model.features.place_features import build_place_features_from_components
from typing import Any, Callable
from pathlib import Path
import pytest


def _measure_runtime(func: Callable[[], Any]) -> float:
    start = time.perf_counter()
    func()
    elapsed = time.perf_counter() - start
    return elapsed


def test_place_feature_build_performance_monkeypatched(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    sample_base = pd.DataFrame(
        {
            "place_id": [f"p-{i}" for i in range(50)],
            "geo_level": ["msa"] * 50,
            "geo_code": [str(10000 + i) for i in range(50)],
            "name": [f"Place {i}" for i in range(50)],
            "source_id": ["connector.place_context"] * 50,
        }
    )
    components = pd.DataFrame(
        {
            "amenities_15min_walk_count": [10 + i for i in range(50)],
            "avg_walk_time_to_top3_amenities": [15 - (i * 0.1) for i in range(50)],
            "grocery_10min_drive_count": [5 + i for i in range(50)],
            "intersection_density": [100 + i for i in range(50)],
            "public_land_acres_30min": [1000 - i for i in range(50)],
            "minutes_to_trailhead": [20 + i for i in range(50)],
            "msa_jobs_t12": [1.5 + 0.05 * i for i in range(50)],
            "msa_jobs_t36": [4.0 + 0.1 * i for i in range(50)],
            "slope_gt15_pct_within_10km": [5 + i for i in range(50)],
            "protected_land_within_10km_pct": [20 + i for i in range(50)],
            "permits_5plus_per_1k_hh_t12": [2 + 0.02 * i for i in range(50)],
            "broadband_gbps_flag": [True] * 50,
        }
    )

    elapsed = _measure_runtime(lambda: build_place_features_from_components(sample_base, components))
    assert elapsed < 0.5, f"place feature build took {elapsed:.3f}s"


def test_cli_refresh_roundtrip_time(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    def fetch_stub(**_: object) -> pd.DataFrame:
        return pd.DataFrame(
            {
                "geo_id": ["08005001202"],
                "geo_level": ["tract"],
                "median_household_income": [76000.0],
                "observed_at": ["2025-01-01"],
                "source_id": ["connector.census_acs"],
            }
        )

    from west_housing_model.data.connectors import callable_connector

    connector = callable_connector("connector.census_acs", fetch_stub)
    from west_housing_model.cli import main as cli_module

    monkeypatch.setattr(cli_module, "DEFAULT_CONNECTORS", {connector.source_id: connector})
    monkeypatch.setenv("WEST_HOUSING_MODEL_CACHE_ROOT", str(tmp_path / "cache"))

    start = time.perf_counter()
    rc = cli_main(["refresh", connector.source_id, "--json"])
    elapsed = time.perf_counter() - start
    assert rc == 0
    assert elapsed < 0.5, f"CLI refresh took {elapsed:.3f}s"
    capsys.readouterr()
