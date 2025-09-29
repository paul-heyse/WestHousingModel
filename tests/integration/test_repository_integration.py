from __future__ import annotations

import json
import logging
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable

import pandas as pd
import pytest

from west_housing_model.core.exceptions import SchemaError
from west_housing_model.data.connectors import callable_connector
from west_housing_model.data.repository import (
    STATUS_FRESH,
    STATUS_REFRESHED,
    STATUS_STALE,
    Repository,
    RepositoryResult,
)


def _make_payload(source_id: str) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "place_id": ["p-001"],
            "metric": ["msa_jobs_t12"],
            "value": [4.2],
            "observed_at": ["2025-01-01"],
            "source_id": [source_id],
        }
    )


def _connector(
    source_id: str,
    fetcher: Callable[..., pd.DataFrame],
    *,
    ttl_seconds: int = 86_400,
) -> Any:
    return callable_connector(source_id, fetcher, ttl_seconds=ttl_seconds)


def test_repository_read_through_then_cache_hit(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    payload = _make_payload("connector.place_context")

    connector = _connector(
        "connector.place_context", lambda **_: payload.copy(deep=True), ttl_seconds=86_400
    )
    repo = Repository({connector.source_id: connector}, cache_dir=tmp_path)

    caplog.set_level(logging.INFO, logger="west_housing_model")
    first = repo.get(connector.source_id, geo_id="08005001202")
    second = repo.get(connector.source_id, geo_id="08005001202")

    assert first.status == STATUS_REFRESHED
    assert second.status == STATUS_FRESH
    assert first.cache_hit is False
    assert second.cache_hit is True
    assert second.artifact_path.exists()
    pd.testing.assert_frame_equal(
        first.frame.reset_index(drop=True), payload.reset_index(drop=True)
    )

    log_payloads = [
        json.loads(record.message) for record in caplog.records if record.message.startswith("{")
    ]
    assert any(entry.get("status") == STATUS_REFRESHED for entry in log_payloads)
    assert any(entry.get("status") == STATUS_FRESH for entry in log_payloads)
    assert all(entry.get("correlation_id") for entry in log_payloads)


def test_repository_offline_serves_stale(tmp_path: Path) -> None:
    payload = _make_payload("connector.place_context")
    connector = _connector(
        "connector.place_context", lambda **_: payload.copy(deep=True), ttl_seconds=86_400
    )

    online_repo = Repository({connector.source_id: connector}, cache_dir=tmp_path)
    online_repo.get(connector.source_id)

    offline_repo = Repository({connector.source_id: connector}, cache_dir=tmp_path, offline=True)
    result = offline_repo.get(connector.source_id)

    assert result.status == STATUS_STALE
    assert result.cache_hit is True
    pd.testing.assert_frame_equal(
        result.frame.reset_index(drop=True), payload.reset_index(drop=True)
    )


def test_repository_refreshes_after_ttl_expiry(tmp_path: Path) -> None:
    payload = _make_payload("connector.place_context")
    call_count = {"count": 0}

    def fetcher(**_: object) -> pd.DataFrame:
        call_count["count"] += 1
        return payload.copy(deep=True)

    connector = _connector("connector.place_context", fetcher, ttl_seconds=24 * 60 * 60)

    current = datetime(2025, 1, 1, tzinfo=timezone.utc)

    def clock() -> datetime:
        return current

    repo = Repository({connector.source_id: connector}, cache_dir=tmp_path, clock=clock)

    first = repo.get(connector.source_id)
    assert first.status == STATUS_REFRESHED
    assert call_count["count"] == 1

    current = current + timedelta(hours=12)
    second = repo.get(connector.source_id)
    assert second.status == STATUS_FRESH
    assert call_count["count"] == 1, "Should reuse cache within TTL"

    current = current + timedelta(days=2)
    third = repo.get(connector.source_id)
    assert third.status == STATUS_REFRESHED
    assert call_count["count"] == 2


def test_repository_captures_schema_drift_payload(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("WEST_HOUSING_MODEL_FAILURE_CACHE", str(tmp_path / "failures"))

    def bad_fetch(**_: object) -> pd.DataFrame:
        return pd.DataFrame({"unexpected": [1]})

    connector = _connector("connector.place_context", bad_fetch)
    repo = Repository({connector.source_id: connector}, cache_dir=tmp_path)

    with pytest.raises(SchemaError):
        repo.get(connector.source_id)

    failure_dir = Path(tmp_path / "failures") / connector.source_id
    assert any(failure_dir.glob("*.log")), "Schema drift logs should exist"


def test_repository_falls_back_to_stale_on_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("WEST_HOUSING_MODEL_FAILURE_CACHE", str(tmp_path / "failures"))
    payload = _make_payload("connector.place_context")

    class Flaky:
        def __init__(self) -> None:
            self.calls = 0

        def __call__(self, **_: object) -> pd.DataFrame:
            self.calls += 1
            if self.calls == 1:
                return payload.copy(deep=True)
            raise RuntimeError("upstream failure")

    connector = _connector("connector.place_context", Flaky(), ttl_seconds=0)
    repo = Repository({connector.source_id: connector}, cache_dir=tmp_path)

    first = repo.get(connector.source_id)
    assert first.status == STATUS_REFRESHED

    fallback = repo.get(connector.source_id)
    assert fallback.status == STATUS_STALE
    assert fallback.metadata.get("fallback_reason")
    failure_dir = Path(tmp_path / "failures") / connector.source_id
    assert list(failure_dir.glob("*.log")), "Failure log should be recorded"


def test_repository_parallel_refresh_uses_locks(tmp_path: Path) -> None:
    payload = _make_payload("connector.place_context")
    call_count = {"count": 0}

    def fetcher(**_: object) -> pd.DataFrame:
        call_count["count"] += 1
        time.sleep(0.05)
        return payload.copy(deep=True)

    connector = _connector("connector.place_context", fetcher, ttl_seconds=24 * 60 * 60)
    repo = Repository({connector.source_id: connector}, cache_dir=tmp_path)

    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(repo.get, connector.source_id) for _ in range(2)]
        results = [future.result(timeout=5) for future in futures]

    statuses = {result.status for result in results}
    assert statuses == {STATUS_REFRESHED, STATUS_FRESH} or statuses == {STATUS_REFRESHED}

    artifact_paths = {result.artifact_path for result in results}
    assert len(artifact_paths) == 1
    cache_files = list((tmp_path / connector.source_id).glob("*.parquet"))
    assert len(cache_files) == 1
    assert call_count["count"] <= 2


def test_repository_refresh_returns_metadata(tmp_path: Path) -> None:
    payload = _make_payload("connector.place_context")

    connector = _connector(
        "connector.place_context", lambda **_: payload.copy(deep=True), ttl_seconds=86_400
    )
    repo = Repository({connector.source_id: connector}, cache_dir=tmp_path)

    result: RepositoryResult = repo.get(connector.source_id)
    assert result.metadata["rows"] == 1
    assert result.metadata["ttl_days"] >= 1
    assert result.metadata["schema_version"] is None
