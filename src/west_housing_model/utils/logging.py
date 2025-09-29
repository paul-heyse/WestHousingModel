"""Structured logging helpers shared across the application.

The utilities here intentionally avoid third-party dependencies so they can be
used by the repository, CLI, and tests without additional setup. Logs default
to JSON but can fall back to text output via environment configuration.
"""

from __future__ import annotations

import json
import logging
import os
import uuid
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Iterator, MutableMapping, Optional

_logger = logging.getLogger("west_housing_model")
_logger.propagate = True

_LOG_FORMAT_JSON = "json"
_LOG_FORMAT_TEXT = "text"
_current_format = _LOG_FORMAT_JSON
_configured = False

_correlation_id: ContextVar[Optional[str]] = ContextVar("correlation_id", default=None)


@dataclass(frozen=True)
class LogContext:
    """Describes the common context propagated through log statements."""

    event: str
    module: str
    action: str
    source_id: Optional[str] = None

    def to_dict(self) -> MutableMapping[str, Any]:
        payload: MutableMapping[str, Any] = {
            "event": self.event,
            "module": self.module,
            "action": self.action,
        }
        if self.source_id is not None:
            payload["source_id"] = self.source_id
        return payload


def _resolve_level(default: int = logging.INFO) -> int:
    env_level = os.getenv("WEST_HOUSING_LOG_LEVEL")
    if not env_level:
        return default
    resolved = getattr(logging, env_level.upper(), None)
    if isinstance(resolved, int):
        return resolved
    return default


def configure(level: int | None = None) -> None:
    """Configure the shared logger using env overrides if present."""

    global _configured, _current_format
    if _configured and level is None:
        return

    resolved_level = _resolve_level(level or logging.INFO)
    log_format = os.getenv("WEST_HOUSING_LOG_FORMAT", _LOG_FORMAT_JSON).lower()
    if log_format not in {_LOG_FORMAT_JSON, _LOG_FORMAT_TEXT}:
        log_format = _LOG_FORMAT_JSON
    _current_format = log_format

    if not _logger.handlers:
        handler = logging.StreamHandler()
        handler.setLevel(resolved_level)
        if log_format == _LOG_FORMAT_TEXT:
            handler.setFormatter(
                logging.Formatter("%(asctime)s %(levelname)s %(message)s", "%Y-%m-%dT%H:%M:%S%z")
            )
        else:
            handler.setFormatter(logging.Formatter("%(message)s"))
        _logger.addHandler(handler)

    _logger.setLevel(resolved_level)
    _configured = True


def _ensure_configured() -> None:
    if not _configured:
        configure()


def _current_correlation_id() -> str:
    cid = _correlation_id.get()
    if cid is None:
        cid = uuid.uuid4().hex
        _correlation_id.set(cid)
    return cid


@contextmanager
def correlation_context(correlation_id: Optional[str] = None) -> Iterator[str]:
    """Context manager that sets the active correlation id for nested logs."""

    cid = correlation_id or uuid.uuid4().hex
    token = _correlation_id.set(cid)
    try:
        yield cid
    finally:
        _correlation_id.reset(token)


def log_event(level: int, context: LogContext, message: str, **fields: Any) -> None:
    """Emit a structured log entry."""

    _ensure_configured()
    record: Dict[str, Any] = dict(context.to_dict())
    record.update({k: v for k, v in fields.items() if v is not None})
    record.update(
        {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": logging.getLevelName(level),
            "message": message,
            "correlation_id": _current_correlation_id(),
        }
    )

    if _current_format == _LOG_FORMAT_TEXT:
        rendered = " ".join(
            f"{key}={record[key]}"
            for key in ("timestamp", "level", "event", "module", "action", "message")
        )
        extras = {
            k: v
            for k, v in record.items()
            if k not in {"timestamp", "level", "event", "module", "action", "message"}
        }
        if extras:
            rendered = f"{rendered} extras={json.dumps(extras, default=str, separators=(",", ":"))}"
    else:
        rendered = json.dumps(record, default=str, separators=(",", ":"))

    _logger.log(level, rendered)


def info(context: LogContext, message: str, **fields: Any) -> None:
    log_event(logging.INFO, context, message, **fields)


def warning(context: LogContext, message: str, **fields: Any) -> None:
    log_event(logging.WARNING, context, message, **fields)


def error(context: LogContext, message: str, **fields: Any) -> None:
    log_event(logging.ERROR, context, message, **fields)


__all__ = [
    "LogContext",
    "configure",
    "correlation_context",
    "error",
    "info",
    "log_event",
    "warning",
]
