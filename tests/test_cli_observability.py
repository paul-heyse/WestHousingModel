from __future__ import annotations

import json
import logging
from pathlib import Path

import pandas as pd

from west_housing_model.data.connectors import callable_connector


def test_cli_refresh_emits_correlation_and_status(
    tmp_path: Path, caplog, capsys, temp_cache_dir: Path
) -> None:
    _ = temp_cache_dir

    connector = callable_connector(
        "connector.census_acs",
        lambda **_: pd.DataFrame(
            {
                "geo_id": ["08005001202"],
                "geo_level": ["tract"],
                "median_household_income": [75000.0],
                "observed_at": ["2025-01-01"],
                "source_id": ["connector.census_acs"],
            }
        ),
        ttl_seconds=3600,
    )

    from west_housing_model.cli import main as cli_module

    cli_module.DEFAULT_CONNECTORS = {connector.source_id: connector}

    caplog.set_level(logging.INFO, logger="west_housing_model")

    assert cli_module.main(["refresh", connector.source_id, "--json"]) == 0
    online_payload = json.loads(capsys.readouterr().out.strip())
    assert online_payload["status"] == "refreshed"
    assert "correlation_id" in online_payload

    caplog.clear()
    assert cli_module.main(["refresh", connector.source_id, "--json", "--offline"]) == 0
    _ = capsys.readouterr()

    log_payloads = [
        json.loads(record.message) for record in caplog.records if record.message.startswith("{")
    ]
    assert log_payloads, "expected structured logs"
    assert any(entry.get("correlation_id") for entry in log_payloads)
