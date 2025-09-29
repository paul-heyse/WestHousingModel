from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, Iterable

import pandas as pd
import pytest

from west_housing_model.cli import main as cli_module
from west_housing_model.cli.main import main
from west_housing_model.data.connectors import DEFAULT_CONNECTORS, callable_connector

GOLDEN_DIR = Path(__file__).resolve().parents[1] / "data" / "golden"


def _load_csv(name: str, **kwargs: Any) -> pd.DataFrame:
    return pd.read_csv(GOLDEN_DIR / name, **kwargs)


def _write_csv(tmp_path: Path, name: str, rows: Iterable[Dict[str, Any]]) -> Path:
    df = pd.DataFrame(rows)
    path = tmp_path / name
    df.to_csv(path, index=False)
    return path


@pytest.fixture
def cli_connectors(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Dict[str, object]:
    monkeypatch.setenv("WEST_HOUSING_MODEL_CACHE_ROOT", str(tmp_path / "cache"))
    registry = dict(DEFAULT_CONNECTORS)

    def fetch_acs(**_: object) -> pd.DataFrame:
        return pd.DataFrame(
            {
                "geo_id": ["08005001202"],
                "geo_level": ["tract"],
                "median_household_income": [76000.0],
                "observed_at": ["2025-01-01"],
                "source_id": ["connector.census_acs"],
            }
        )

    registry["connector.census_acs"] = callable_connector(
        "connector.census_acs", fetch_acs, ttl_seconds=24 * 60 * 60
    )
    monkeypatch.setattr(cli_module, "DEFAULT_CONNECTORS", registry, raising=False)
    return registry


def test_cli_refresh_json_contract(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    caplog: pytest.LogCaptureFixture,
    cli_connectors: Dict[str, object],
) -> None:
    source_id = next(iter(cli_connectors))
    caplog.set_level(logging.INFO, logger="west_housing_model")

    rc_online = main(["refresh", source_id, "--json"])
    assert rc_online == 0
    online_payload = json.loads(capsys.readouterr().out.strip())
    assert online_payload["status"] == "refreshed"
    assert online_payload["cache_hit"] is False
    assert online_payload["cache_key"]
    assert online_payload["artifact_path"].endswith(".parquet")
    assert online_payload["correlation_id"]

    log_payloads = [
        json.loads(record.message) for record in caplog.records if record.message.startswith("{")
    ]
    assert any(entry.get("status") == "refreshed" for entry in log_payloads)
    caplog.clear()

    rc_offline = main(["refresh", source_id, "--json", "--offline"])
    assert rc_offline == 0
    offline_payload = json.loads(capsys.readouterr().out.strip())
    assert offline_payload["status"] == "stale"
    assert offline_payload["cache_hit"] is True
    assert offline_payload["stale"] is True

    log_payloads = [
        json.loads(record.message) for record in caplog.records if record.message.startswith("{")
    ]
    assert any(entry.get("status") == "stale" for entry in log_payloads)


def test_cli_features_place_and_site(
    tmp_path: Path, cli_connectors: Dict[str, object]
) -> None:
    base = tmp_path / "place_base.csv"
    components = tmp_path / "place_components.csv"
    site_base = tmp_path / "site_base.csv"
    site_hazards = tmp_path / "site_hazards.csv"

    _load_csv("place_base.csv").to_csv(base, index=False)
    _load_csv("place_components.csv").to_csv(components, index=False)
    _load_csv("site_base.csv").to_csv(site_base, index=False)
    _load_csv("site_hazards.csv").to_csv(site_hazards, index=False)

    out_dir = tmp_path / "features"
    rc = main(
        [
            "features",
            "--places",
            str(base),
            "--place-components",
            str(components),
            "--sites-base",
            str(site_base),
            "--sites-hazards",
            str(site_hazards),
            "--output",
            str(out_dir),
        ]
    )
    assert rc == 0

    place_parquet = out_dir / "place_features.parquet"
    site_parquet = out_dir / "site_features.parquet"
    assert place_parquet.exists()
    assert site_parquet.exists()

    place_df = pd.read_parquet(place_parquet)
    site_df = pd.read_parquet(site_parquet)
    assert {
        "place_id",
        "geo_level",
        "geo_code",
        "aker_market_fit",
        "pillar_uc",
        "pillar_sc",
    }.issubset(place_df.columns)
    assert {
        "property_id",
        "place_id",
        "wildfire_risk_percentile",
        "pga_10in50_g",
        "in_sfha",
    }.issubset(site_df.columns)


def test_cli_render_outputs_manifest(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    scenario_path = tmp_path / "scenario.json"
    scenario_path.write_text((GOLDEN_DIR / "scenario.json").read_text())

    rc = main(["render", str(scenario_path), "--json"])
    assert rc == 0
    stdout = capsys.readouterr().out.strip()
    payload = json.loads(stdout)
    assert payload["action"] == "render"
    valuation = payload["valuation"]
    assert isinstance(valuation, list)
    assert valuation[0]["source_manifest"]["sources"]
