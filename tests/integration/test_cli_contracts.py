from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Dict

import pandas as pd
import pytest

from west_housing_model.cli import main as cli_module
from west_housing_model.cli.main import main
from west_housing_model.data.connectors import callable_connector

GOLDEN_DIR = Path(__file__).resolve().parents[1] / "data" / "golden"


@pytest.fixture
def cli_connectors(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Dict[str, object]:
    monkeypatch.setenv("WEST_HOUSING_MODEL_CACHE_ROOT", str(tmp_path / "cache"))

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

    connector = callable_connector("connector.census_acs", fetch_acs, ttl_seconds=24 * 60 * 60)
    registry = {connector.source_id: connector}
    monkeypatch.setattr(cli_module, "DEFAULT_CONNECTORS", registry, raising=False)
    return registry


def test_refresh_contract(cli_connectors: Dict[str, object], capsys, caplog) -> None:
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


def test_features_contract(tmp_path: Path, cli_connectors: Dict[str, object]) -> None:
    base = tmp_path / "place_base.csv"
    components = tmp_path / "place_components.csv"
    site_base = tmp_path / "site_base.csv"
    site_hazards = tmp_path / "site_hazards.csv"

    pd.read_csv(GOLDEN_DIR / "place_base.csv").to_csv(base, index=False)
    pd.read_csv(GOLDEN_DIR / "place_components.csv").to_csv(components, index=False)
    pd.read_csv(GOLDEN_DIR / "site_base.csv").to_csv(site_base, index=False)
    pd.read_csv(GOLDEN_DIR / "site_hazards.csv").to_csv(site_hazards, index=False)

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
    assert (out_dir / "place_features.parquet").exists()
    assert (out_dir / "site_features.parquet").exists()


def test_render_contract(tmp_path: Path, cli_connectors: Dict[str, object], capsys) -> None:
    scenario_path = tmp_path / "scenario.json"
    scenario_path.write_text((GOLDEN_DIR / "scenario.json").read_text())

    rc = main(["render", str(scenario_path), "--json"])
    assert rc == 0
    payload = json.loads(capsys.readouterr().out.strip())
    assert payload["action"] == "render"
    valuation = payload["valuation"]
    assert isinstance(valuation, list)
    assert valuation[0]["source_manifest"]["sources"]
