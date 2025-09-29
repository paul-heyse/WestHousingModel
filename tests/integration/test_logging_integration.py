from __future__ import annotations

import json
import logging
from pathlib import Path

import pandas as pd

from west_housing_model.data.connectors import callable_connector
from west_housing_model.data.repository import Repository


def test_repository_logs_include_correlation_and_cache_key(tmp_path: Path, caplog) -> None:
    payload = pd.DataFrame(
        {
            "place_id": ["p-1"],
            "metric": ["msa_jobs_t12"],
            "value": [4.2],
            "observed_at": ["2025-01-01"],
            "source_id": ["connector.place_context"],
        }
    )

    connector = callable_connector(
        "connector.place_context", lambda **_: payload.copy(deep=True), ttl_seconds=86_400
    )
    repo = Repository({connector.source_id: connector}, cache_dir=tmp_path)

    caplog.set_level(logging.INFO, logger="west_housing_model")
    result = repo.get(connector.source_id)

    assert result.correlation_id
    log_payloads = [
        json.loads(record.message) for record in caplog.records if record.message.startswith("{")
    ]
    assert any(entry.get("correlation_id") == result.correlation_id for entry in log_payloads)
    assert any(entry.get("cache_key") == result.cache_key for entry in log_payloads)
