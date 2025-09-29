"""Tests covering schema capture and repository caching behavior."""

from __future__ import annotations

import json
import logging
from pathlib import Path

import pandas as pd
import pytest
from west_housing_model.core.exceptions import ConnectorError, SchemaError
from west_housing_model.data.connectors import callable_connector
from west_housing_model.data.repository import (
    STATUS_FRESH,
    STATUS_REFRESHED,
    STATUS_STALE,
    Repository,
)


def _valid_connector_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "place_id": ["p-001"],
            "metric": ["msa_jobs_t12"],
            "value": [4.2],
            "observed_at": ["2024-01-01"],
            "source_id": ["connector.place_context"],
        }
    )


def test_connector_captures_payload_on_schema_failure(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("WEST_HOUSING_MODEL_FAILURE_CACHE", str(tmp_path))

    def bad_fetcher(**_: object) -> pd.DataFrame:
        return pd.DataFrame({"unexpected": [1]})

    connector = callable_connector("connector.place_context", bad_fetcher)

    with pytest.raises(SchemaError):
        connector.fetch()

    failure_dir = Path(tmp_path) / "connector.place_context"
    assert list(failure_dir.glob("*.csv")), "schema failures should capture payload CSVs"


def test_repository_returns_cached_frame_when_fresh(tmp_path) -> None:
    payload = _valid_connector_frame()

    class Fetcher:
        def __init__(self) -> None:
            self.calls = 0

        def __call__(self, **_: object) -> pd.DataFrame:
            self.calls += 1
            return payload.copy(deep=True)

    fetcher = Fetcher()
    connector = callable_connector("connector.place_context", fetcher, ttl_seconds=86_400)
    repo = Repository({"connector.place_context": connector}, cache_dir=tmp_path)

    first = repo.get("connector.place_context")
    second = repo.get("connector.place_context")

    assert fetcher.calls == 1
    assert first.status == STATUS_REFRESHED
    assert second.status == STATUS_FRESH
    assert first.cache_hit is False
    assert second.cache_hit is True
    assert second.artifact_path.exists()
    pd.testing.assert_frame_equal(
        first.frame.reset_index(drop=True), payload.reset_index(drop=True)
    )


def test_repository_refetches_when_ttl_zero(tmp_path) -> None:
    payload = _valid_connector_frame()

    class Fetcher:
        def __init__(self) -> None:
            self.calls = 0

        def __call__(self, **_: object) -> pd.DataFrame:
            self.calls += 1
            return payload.copy(deep=True)

    fetcher = Fetcher()
    connector = callable_connector("connector.place_context", fetcher, ttl_seconds=0)
    repo = Repository({"connector.place_context": connector}, cache_dir=tmp_path)

    result_one = repo.get("connector.place_context")
    result_two = repo.get("connector.place_context")

    assert fetcher.calls == 2, "TTL zero should force refetch on subsequent calls"
    assert result_one.status == STATUS_REFRESHED
    assert result_two.status == STATUS_REFRESHED


def test_repository_returns_stale_on_connector_error(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("WEST_HOUSING_MODEL_FAILURE_CACHE", str(tmp_path / "failures"))

    payload = _valid_connector_frame()

    class FlakyFetcher:
        def __init__(self) -> None:
            self.calls = 0

        def __call__(self, **_: object) -> pd.DataFrame:
            if self.calls == 0:
                self.calls += 1
                return payload.copy(deep=True)
            self.calls += 1
            raise RuntimeError("network error")

    flaky = FlakyFetcher()
    connector = callable_connector("connector.place_context", flaky, ttl_seconds=0)
    repo = Repository({"connector.place_context": connector}, cache_dir=tmp_path)

    fresh = repo.get("connector.place_context")
    assert fresh.status == STATUS_REFRESHED

    fallback = repo.get("connector.place_context")
    assert fallback.status == STATUS_STALE
    assert flaky.calls == 2

    failure_dir = Path(tmp_path / "failures") / "connector.place_context"
    assert list(failure_dir.glob("*.log")), "failures should be logged when falling back"


def test_repository_raises_when_no_cache_available(tmp_path) -> None:
    def failing_fetcher(**_: object) -> pd.DataFrame:
        raise RuntimeError("boom")

    connector = callable_connector("connector.place_context", failing_fetcher)
    repo = Repository({"connector.place_context": connector}, cache_dir=tmp_path)

    with pytest.raises(ConnectorError):
        repo.get("connector.place_context")


def test_repository_offline_mode(tmp_path) -> None:
    payload = _valid_connector_frame()

    connector = callable_connector(
        "connector.place_context",
        lambda **_: payload.copy(deep=True),
        ttl_seconds=86_400,
    )
    online_repo = Repository({"connector.place_context": connector}, cache_dir=tmp_path)
    online_repo.get("connector.place_context")

    connectors = {"connector.place_context": connector}
    offline_repo = Repository(connectors, cache_dir=tmp_path, offline=True)
    result = offline_repo.get("connector.place_context")
    assert result.status == STATUS_STALE
    pd.testing.assert_frame_equal(
        result.frame.reset_index(drop=True), payload.reset_index(drop=True)
    )

    empty_repo_dir = tmp_path / "empty_offline"
    empty_repo = Repository(connectors, cache_dir=empty_repo_dir, offline=True)
    with pytest.raises(ConnectorError):
        empty_repo.get("connector.place_context")


def test_repository_emits_structured_logs(tmp_path, caplog) -> None:
    payload = _valid_connector_frame()

    connector = callable_connector(
        "connector.place_context",
        lambda **_: payload.copy(deep=True),
        ttl_seconds=86_400,
    )
    repo = Repository({"connector.place_context": connector}, cache_dir=tmp_path)

    with caplog.at_level(logging.INFO, logger="west_housing_model"):
        result = repo.get("connector.place_context")

    assert result.correlation_id
    records = [json.loads(record.message) for record in caplog.records]
    final = records[-1]
    assert final["event"] == "repository.fetch"
    assert final["status"] == STATUS_REFRESHED
    assert final["cache_key"]
    assert final["correlation_id"] == result.correlation_id
