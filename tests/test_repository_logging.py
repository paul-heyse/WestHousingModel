from __future__ import annotations

import json
import logging
from pathlib import Path

import pandas as pd

import pytest

from west_housing_model.data.connectors import callable_connector
from west_housing_model.data.repository import (
    STATUS_REFRESHED,
    STATUS_STALE,
    Repository,
)


def test_repository_writes_failure_log_and_returns_stale(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("WEST_HOUSING_MODEL_FAILURE_CACHE", str(tmp_path / "failures"))

    payload = pd.DataFrame(
        {
            "place_id": ["p-001"],
            "metric": ["msa_jobs_t12"],
            "value": [4.2],
            "observed_at": ["2024-01-01"],
            "source_id": ["connector.place_context"],
        }
    )

    class Flaky:
        def __init__(self) -> None:
            self.calls = 0

        def __call__(self, **_: object) -> pd.DataFrame:
            self.calls += 1
            if self.calls == 1:
                return payload.copy(deep=True)
            raise RuntimeError("boom")

    connector = callable_connector("connector.place_context", Flaky(), ttl_seconds=0)
    repo = Repository({"connector.place_context": connector}, cache_dir=tmp_path)

    first = repo.get("connector.place_context")
    assert first.status == STATUS_REFRESHED

    # Second should fallback to stale and write a failure log
    second = repo.get("connector.place_context")
    assert second.status == STATUS_STALE

    failure_dir = tmp_path / "failures" / "connector.place_context"
    logs = list(failure_dir.glob("*.log"))
    assert logs, "expected a failure log to be written"
    data = json.loads(logs[-1].read_text())
    assert data.get("source_id") == "connector.place_context"
    assert "correlation_id" in data


def test_repository_logs_status_transitions(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    payload = _valid_connector_frame()

    connector = callable_connector(
        "connector.place_context",
        lambda **_: payload.copy(deep=True),
        ttl_seconds=86_400,
    )
    repo = Repository({"connector.place_context": connector}, cache_dir=tmp_path)

    caplog.set_level(logging.INFO, logger="west_housing_model")
    first = repo.get("connector.place_context")
    logs_first = [json.loads(record.message) for record in caplog.records if record.message.startswith("{")]
    assert any(entry.get("status") == STATUS_REFRESHED for entry in logs_first)
    assert first.status == STATUS_REFRESHED
    caplog.clear()

    second = repo.get("connector.place_context")
    logs_second = [json.loads(record.message) for record in caplog.records if record.message.startswith("{")]
    assert any(entry.get("status") == STATUS_FRESH for entry in logs_second)
    assert second.status == STATUS_FRESH
    assert first.correlation_id != ""
    assert second.cache_key == first.cache_key
