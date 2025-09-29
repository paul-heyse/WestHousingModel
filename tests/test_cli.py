from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict

import pandas as pd

from west_housing_model.cli.main import main
from west_housing_model.data.connectors import callable_connector


def test_cli_features_builds_place_and_site(
    tmp_path: Path,
    place_base_df: pd.DataFrame,
    place_components_df: pd.DataFrame,
    site_base_df: pd.DataFrame,
    site_hazards_df: pd.DataFrame,
) -> None:
    places_base = tmp_path / "places_base.csv"
    places_components = tmp_path / "places_components.csv"
    site_base = tmp_path / "sites_base.csv"
    site_hazards = tmp_path / "sites_hazards.csv"

    place_base_df.to_csv(places_base, index=False)
    place_components_df.to_csv(places_components, index=False)
    site_base_df.to_csv(site_base, index=False)
    site_hazards_df.to_csv(site_hazards, index=False)

    out_dir = tmp_path / "artifacts"
    exit_code = main(
        [
            "features",
            "--places",
            str(places_base),
            "--place-components",
            str(places_components),
            "--sites-base",
            str(site_base),
            "--sites-hazards",
            str(site_hazards),
            "--output",
            str(out_dir),
        ]
    )

    assert exit_code == 0
    assert (out_dir / "place_features.parquet").exists()
    assert (out_dir / "site_features.parquet").exists()


def test_cli_features_ops_writes_provenance(tmp_path: Path) -> None:
    ops_csv = tmp_path / "ops.csv"
    ops_csv.write_text(
        "property_id,as_of,eia_state,eia_res_price_cents_per_kwh,broadband_gbps_flag,"
        "zoning_context_note,hud_fmr_2br\n"
        "p-ops,2025-02-01,CO,13.5,True,Allowance,1800\n"
    )

    out_dir = tmp_path / "ops_output"
    exit_code = main(["features", "--ops", str(ops_csv), "--output", str(out_dir)])
    assert exit_code == 0
    ops_path = out_dir / "ops_features.parquet"
    prov_path = out_dir / "ops_features_provenance.json"
    assert ops_path.exists()
    assert prov_path.exists()
    provenance_payload = json.loads(prov_path.read_text())
    assert provenance_payload[0]["property_id"] == "p-ops"
    assert (
        provenance_payload[0]["provenance"]["utility_rate_note"]["source_id"] == "connector.eia_v2"
    )


def test_cli_render_outputs_json(tmp_path: Path, scenario_payload: dict) -> None:
    scenario_path = tmp_path / "scenario.json"
    scenario_path.write_text(json.dumps(scenario_payload))

    out_dir = tmp_path / "valuation"
    exit_code = main(["render", str(scenario_path), "--output", str(out_dir)])
    assert exit_code == 0

    payload_path = out_dir / "valuation.json"
    assert payload_path.exists()
    data = json.loads(payload_path.read_text())
    assert isinstance(data, list)
    assert data[0]["scenario_id"] == scenario_payload["scenario_id"]
    assert "deal_quality" in data[0]
    assert "sensitivity_matrix" in data[0]
    assert isinstance(data[0]["sensitivity_matrix"], list)


def test_cli_refresh_online_and_offline(
    tmp_path: Path, capsys, caplog, temp_cache_dir: Path
) -> None:
    _ = temp_cache_dir
    events = []

    def fetch_stub(**_: object) -> pd.DataFrame:
        events.append("fetch")
        return pd.DataFrame(
            {
                "place_id": ["p-1"],
                "metric": ["msa_jobs_t12"],
                "value": [4.2],
                "observed_at": ["2025-01-01"],
                "source_id": ["connector.place_context"],
            }
        )

    connector = callable_connector("connector.place_context", fetch_stub, ttl_seconds=3600)

    from west_housing_model.cli import main as cli_module

    # Use isolated connector registry so we control behavior.
    cli_module.DEFAULT_CONNECTORS = {connector.source_id: connector}

    caplog.set_level(logging.INFO, logger="west_housing_model")

    # Online refresh warms cache and emits refreshed status
    assert cli_module.main(["refresh", connector.source_id, "--json"]) == 0
    captured_online = json.loads(capsys.readouterr().out.strip())
    assert captured_online["status"] == "refreshed"
    assert captured_online["cache_hit"] is False
    online_logs = [
        json.loads(record.message) for record in caplog.records if record.message.startswith("{")
    ]
    assert any(entry.get("status") == "refreshed" for entry in online_logs)
    assert events == ["fetch"]

    caplog.clear()

    # Offline refresh reads from cache and reports stale status
    assert cli_module.main(["refresh", connector.source_id, "--json", "--offline"]) == 0
    captured_offline = json.loads(capsys.readouterr().out.strip())
    assert captured_offline["status"] == "stale"
    assert captured_offline["cache_hit"] is True
    offline_logs = [
        json.loads(record.message) for record in caplog.records if record.message.startswith("{")
    ]
    assert any(entry.get("status") == "stale" for entry in offline_logs)
