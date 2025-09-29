from __future__ import annotations

import json
import logging

from west_housing_model.utils.logging import (
    LogContext,
    configure,
    correlation_context,
    info,
)


def test_log_event_includes_correlation_id(caplog) -> None:
    configure()
    ctx = LogContext(event="test", module="tests", action="log-event")
    with caplog.at_level(logging.INFO, logger="west_housing_model"):
        with correlation_context("corr-123"):
            info(ctx, "emit", extra="field")
    assert caplog.records
    payload = json.loads(caplog.records[0].message)
    assert payload["correlation_id"] == "corr-123"
    assert payload["event"] == "test"
    assert payload["module"] == "tests"
    assert payload["extra"] == "field"


def test_correlation_context_generates_unique_ids() -> None:
    configure()
    ids: set[str] = set()
    for _ in range(2):
        with correlation_context() as cid:
            assert cid
            ids.add(cid)
    assert len(ids) == 2, "Each correlation context should yield a unique id"
