"""Read-through cache repository coordinating connectors and artifacts.

This module implements the cache strategy described in ``architecture.md``.  It
converts connector calls into deterministic cache keys, keeps a SQLite index of
artifacts, and exposes a single interface (`Repository.get`) that higher layers
use to fetch data whether they are online or offline.
"""

from __future__ import annotations

import fcntl
import json
import math
import os
import sqlite3
import tempfile
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, Iterator, Mapping, Optional, Protocol

import pandas as pd

from west_housing_model.core.exceptions import CacheError, ConnectorError, SchemaError
from west_housing_model.data.catalog import failure_capture_path, validate_connector
from west_housing_model.utils.logging import (
    LogContext,
    correlation_context,
)
from west_housing_model.utils.logging import (
    configure as configure_logging,
)
from west_housing_model.utils.logging import (
    error as log_error,
)
from west_housing_model.utils.logging import (
    info as log_info,
)
from west_housing_model.utils.logging import (
    warning as log_warning,
)


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Connector(Protocol):
    """Protocol describing the minimal connector contract.

    Connectors live under ``west_housing_model.data.connectors``.  The
    repository never depends on concrete connector types—this protocol captures
    the handful of attributes/methods required so the repository can work with
    both first-party connectors and test doubles.
    """

    source_id: str
    ttl_seconds: int

    def fetch(self, **query: Any) -> pd.DataFrame:  # pragma: no cover - structural type
        """Fetch a dataset using structured query keywords."""


STATUS_FRESH = "fresh"
STATUS_REFRESHED = "refreshed"
STATUS_STALE = "stale"


@dataclass(frozen=True)
class RepositoryResult:
    """Container for repository responses."""

    source_id: str
    frame: pd.DataFrame
    status: str
    artifact_path: Path
    cache_key: str
    correlation_id: str
    metadata: Mapping[str, Any] = field(default_factory=dict)

    @property
    def is_stale(self) -> bool:
        return self.status == STATUS_STALE

    @property
    def cache_hit(self) -> bool:
        return self.status in {STATUS_FRESH, STATUS_STALE}


@dataclass(frozen=True)
class CacheIndexRecord:
    """Metadata describing a cached artifact."""

    source_id: str
    key_hash: str
    relative_path: Path
    created_at: datetime
    as_of: Optional[str]
    ttl_days: int
    rows: int
    schema_version: Optional[str]

    def is_fresh(self, reference: datetime) -> bool:
        if self.ttl_days <= 0:
            return False
        expires_at = self.created_at + timedelta(days=self.ttl_days)
        return reference <= expires_at


class CacheIndex:
    """SQLite-backed index for cached artifacts.

    The index is intentionally thin: it stores the canonical location on disk
    plus enough metadata to answer freshness questions without touching Parquet
    payloads.  Each method opens a short-lived SQLite connection so that
    multiple processes (e.g., CLI refresh + Streamlit UI) can share the index
    safely.
    """

    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_schema()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        return conn

    def _ensure_schema(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS cache_index (
                    source_id TEXT NOT NULL,
                    key_hash TEXT NOT NULL,
                    path TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    as_of TEXT,
                    ttl_days INTEGER NOT NULL,
                    rows INTEGER,
                    schema_version TEXT,
                    PRIMARY KEY (source_id, key_hash)
                )
                """
            )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_cache_source
                ON cache_index (source_id)
                """
            )

    def lookup(self, source_id: str, key_hash: str) -> Optional[CacheIndexRecord]:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM cache_index WHERE source_id = ? AND key_hash = ?",
                (source_id, key_hash),
            ).fetchone()
        if row is None:
            return None
        return CacheIndexRecord(
            source_id=row["source_id"],
            key_hash=row["key_hash"],
            relative_path=Path(row["path"]),
            created_at=datetime.fromisoformat(row["created_at"]),
            as_of=row["as_of"],
            ttl_days=int(row["ttl_days"]),
            rows=int(row["rows"]) if row["rows"] is not None else 0,
            schema_version=row["schema_version"],
        )

    def upsert(self, record: CacheIndexRecord) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO cache_index (
                    source_id, key_hash, path, created_at, as_of, ttl_days, rows, schema_version
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(source_id, key_hash) DO UPDATE SET
                    path = excluded.path,
                    created_at = excluded.created_at,
                    as_of = excluded.as_of,
                    ttl_days = excluded.ttl_days,
                    rows = excluded.rows,
                    schema_version = excluded.schema_version
                """,
                (
                    record.source_id,
                    record.key_hash,
                    str(record.relative_path),
                    record.created_at.isoformat(),
                    record.as_of,
                    record.ttl_days,
                    record.rows,
                    record.schema_version,
                ),
            )


def _normalize_value(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat()
    if hasattr(value, "isoformat"):
        try:
            return value.isoformat()
        except TypeError:
            return str(value)
    if isinstance(value, (list, tuple)):
        return [_normalize_value(item) for item in value]
    if isinstance(value, dict):
        return {str(k): _normalize_value(v) for k, v in value.items()}
    return value


def _stable_query_signature(query: Mapping[str, Any]) -> str:
    """Create a JSON string that uniquely represents query parameters.

    The normalized signature is hashed with the ``source_id`` to compute cache
    file names.  Keeping this logic in one place ensures callers and tests use
    the same encoding (sorted keys, normalized values) and prevents accidental
    cache misses caused by superficial differences like key ordering.
    """

    return json.dumps({k: _normalize_value(v) for k, v in sorted(query.items())}, sort_keys=True)


def _key_hash(source_id: str, query: Mapping[str, Any]) -> str:
    signature = _stable_query_signature(query)
    digest = sha256()
    digest.update(source_id.encode("utf-8"))
    digest.update(b"::")
    digest.update(signature.encode("utf-8"))
    return digest.hexdigest()


def _deterministic_rows(frame: pd.DataFrame) -> int:
    return int(frame.shape[0])


def _extract_as_of(frame: pd.DataFrame) -> Optional[str]:
    for column in ("as_of", "observed_at"):
        if column in frame.columns and not frame.empty:
            value = frame.iloc[0][column]
            if pd.isna(value):
                continue
            if isinstance(value, datetime):
                return value.isoformat()
            return str(value)
    return None


def _connector_schema_version(connector: Connector) -> Optional[str]:
    return getattr(connector, "schema_version", None)


def _elapsed_ms(start: datetime, end: datetime) -> int:
    return int((end - start).total_seconds() * 1000)


@contextmanager
def _source_lock(lock_path: Path) -> Iterator[None]:
    """Context manager that serialises writes per ``source_id``.

    Without this lock, two workers refreshing the same connector could race and
    overwrite each other's artifacts.  A simple filesystem lock keeps the
    implementation portable and works even when the repository is used from the
    CLI.
    """

    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with open(lock_path, "w") as lock_file:
        fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)


def _record_failure(
    source_id: str,
    message: str,
    *,
    correlation_id: str,
    details: Optional[Mapping[str, Any]] = None,
) -> None:
    failure_dir = failure_capture_path(source_id)
    timestamp = _utcnow().strftime("%Y%m%dT%H%M%S%f")
    payload: Dict[str, Any] = {
        "timestamp": timestamp,
        "source_id": source_id,
        "correlation_id": correlation_id,
        "message": message,
    }
    if details:
        payload.update(details)
    log_path = failure_dir / f"{timestamp}.log"
    log_path.write_text(json.dumps(payload, default=str, indent=2))


@dataclass
class CacheStore:
    """Manages artifact storage and lookup."""

    root: Path
    index: CacheIndex = field(init=False)

    def __post_init__(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        self.index = CacheIndex(self.root / "cache_index.sqlite")

    def artifact_path(self, source_id: str, key_hash: str) -> Path:
        return self.root / source_id / f"{key_hash}.parquet"

    def lock_path(self, source_id: str) -> Path:
        return self.root / source_id / ".lock"

    def load(self, record: CacheIndexRecord) -> pd.DataFrame:
        artifact = self.root / record.relative_path
        if not artifact.exists():
            raise CacheError(
                "Cached artifact missing",
                context={"source_id": record.source_id, "path": str(artifact)},
            )
        return pd.read_parquet(artifact)

    def write(
        self,
        source_id: str,
        key_hash: str,
        frame: pd.DataFrame,
        ttl_days: int,
        schema_version: Optional[str],
        *,
        created_at: Optional[datetime] = None,
    ) -> CacheIndexRecord:
        artifact = self.artifact_path(source_id, key_hash)
        artifact.parent.mkdir(parents=True, exist_ok=True)
        frame.to_parquet(artifact, index=False)
        data_payload_path = artifact.with_suffix(".json")
        try:
            frame.head(20).to_json(data_payload_path, orient="records", date_format="iso")
        except Exception:
            if data_payload_path.exists():
                data_payload_path.unlink(missing_ok=True)
        record = CacheIndexRecord(
            source_id=source_id,
            key_hash=key_hash,
            relative_path=artifact.relative_to(self.root),
            created_at=created_at or _utcnow(),
            as_of=_extract_as_of(frame),
            ttl_days=ttl_days,
            rows=_deterministic_rows(frame),
            schema_version=schema_version,
        )
        self.index.upsert(record)
        return record


@dataclass
class Repository:
    """Repository façade coordinating connectors, cache index, and offline mode."""

    connectors: Optional[Mapping[str, Connector]] = None
    cache_dir: Optional[Path] = None
    offline: bool = False
    clock: Callable[[], datetime] = _utcnow
    _store: CacheStore = field(init=False)
    _connectors: Mapping[str, Connector] = field(init=False)

    def __post_init__(self) -> None:
        configure_logging()
        if self.connectors is None:
            from west_housing_model.data.connectors import DEFAULT_CONNECTORS

            self._connectors = DEFAULT_CONNECTORS
        else:
            self._connectors = dict(self.connectors)

        if self.cache_dir is not None:
            root = self.cache_dir
        else:
            env_root = os.getenv("WEST_HOUSING_MODEL_CACHE_ROOT")
            if env_root:
                root = Path(env_root)
            else:
                # Ephemeral per-process cache to avoid test interference
                root = Path(tempfile.mkdtemp(prefix="whm-cache-"))
        self._store = CacheStore(Path(root))

    def get(self, source_id: str, **query: Any) -> RepositoryResult:
        connector = self._resolve_connector(source_id)
        key_hash = _key_hash(source_id, query)
        query_signature = _stable_query_signature(query)

        with correlation_context() as correlation_id:
            started_at = self.clock()
            context = LogContext(
                event="repository.fetch",
                module="data.repository",
                action="get",
                source_id=source_id,
            )
            log_info(
                context,
                "fetch.start",
                cache_key=key_hash,
                query_signature=query_signature,
                offline=self.offline,
            )

            record = self._store.index.lookup(source_id, key_hash)
            now = self.clock()

            if self.offline:
                if record is None:
                    log_error(
                        context,
                        "fetch.offline-miss",
                        status="error",
                        cache_key=key_hash,
                        query_signature=query_signature,
                    )
                    raise ConnectorError(
                        f"Offline mode: no cached artifact for '{source_id}'",
                        context={"source_id": source_id, "cache_key": key_hash},
                    )
                frame = validate_connector(source_id, self._store.load(record), lazy=True)
                artifact_path = self._store.root / record.relative_path
                duration_ms = _elapsed_ms(started_at, self.clock())
                metadata = {
                    "rows": record.rows,
                    "ttl_days": record.ttl_days,
                    "schema_version": record.schema_version,
                    "as_of": record.as_of,
                }
                log_info(
                    context,
                    "fetch.offline-cache",
                    status=STATUS_STALE,
                    cache_key=key_hash,
                    query_signature=query_signature,
                    artifact=str(artifact_path),
                    duration_ms=duration_ms,
                )
                return RepositoryResult(
                    source_id=source_id,
                    frame=frame,
                    status=STATUS_STALE,
                    artifact_path=artifact_path,
                    cache_key=key_hash,
                    correlation_id=correlation_id,
                    metadata=metadata,
                )

            lock_path = self._store.lock_path(source_id)

            if record and record.is_fresh(now):
                artifact_path = self._store.root / record.relative_path
                if not artifact_path.exists():
                    frame = validate_connector(source_id, connector.fetch(**query))
                    with _source_lock(lock_path):
                        record = self._store.write(
                            source_id=source_id,
                            key_hash=key_hash,
                            frame=frame,
                            ttl_days=max(
                                1,
                                math.ceil(int(getattr(connector, "ttl_seconds", 86_400)) / 86_400),
                            ),
                            schema_version=_connector_schema_version(connector),
                            created_at=self.clock(),
                        )
                    duration_ms = _elapsed_ms(started_at, self.clock())
                    metadata = {
                        "rows": record.rows,
                        "ttl_days": record.ttl_days,
                        "schema_version": record.schema_version,
                        "as_of": record.as_of,
                    }
                    log_info(
                        context,
                        "fetch.connector-success",
                        status=STATUS_REFRESHED,
                        cache_key=key_hash,
                        query_signature=query_signature,
                        artifact=str(artifact_path),
                        duration_ms=duration_ms,
                        ttl_days=record.ttl_days,
                    )
                    return RepositoryResult(
                        source_id=source_id,
                        frame=frame,
                        status=STATUS_REFRESHED,
                        artifact_path=artifact_path,
                        cache_key=key_hash,
                        correlation_id=correlation_id,
                        metadata=metadata,
                    )
                frame = validate_connector(source_id, self._store.load(record), lazy=True)
                duration_ms = _elapsed_ms(started_at, self.clock())
                metadata = {
                    "rows": record.rows,
                    "ttl_days": record.ttl_days,
                    "schema_version": record.schema_version,
                    "as_of": record.as_of,
                }
                log_info(
                    context,
                    "fetch.cache-hit",
                    status=STATUS_FRESH,
                    cache_key=key_hash,
                    query_signature=query_signature,
                    artifact=str(artifact_path),
                    duration_ms=duration_ms,
                )
                return RepositoryResult(
                    source_id=source_id,
                    frame=frame,
                    status=STATUS_FRESH,
                    artifact_path=artifact_path,
                    cache_key=key_hash,
                    correlation_id=correlation_id,
                    metadata=metadata,
                )

            log_info(
                context,
                "fetch.connector.request",
                cache_key=key_hash,
                query_signature=query_signature,
            )
            try:
                frame = connector.fetch(**query)
                # Minimal schema sanity: require at least source_id or observed_at
                if not isinstance(frame, pd.DataFrame) or (
                    "source_id" not in frame.columns and "observed_at" not in frame.columns
                ):
                    _record_failure(
                        source_id,
                        "schema-validation-failed",
                        correlation_id=correlation_id,
                        details={"cache_key": key_hash},
                    )
                    raise SchemaError("Connector schema invalid", context={"source_id": source_id})
            except SchemaError as exc:
                _record_failure(
                    source_id,
                    str(exc),
                    correlation_id=correlation_id,
                    details={
                        "cache_key": key_hash,
                        "query_signature": query_signature,
                        "error": exc.message,
                    },
                )
                log_error(
                    context,
                    "fetch.schema-error",
                    status="error",
                    cache_key=key_hash,
                    query_signature=query_signature,
                    error=str(exc),
                )
                raise
            except ConnectorError as exc:
                if record:
                    artifact_path = self._store.root / record.relative_path
                    duration_ms = _elapsed_ms(started_at, self.clock())
                    metadata = {
                        "rows": record.rows,
                        "ttl_days": record.ttl_days,
                        "schema_version": record.schema_version,
                        "as_of": record.as_of,
                        "fallback_reason": str(exc),
                    }
                    log_warning(
                        context,
                        "fetch.fallback",
                        status=STATUS_STALE,
                        cache_key=key_hash,
                        query_signature=query_signature,
                        artifact=str(artifact_path),
                        duration_ms=duration_ms,
                        error=str(exc),
                    )
                    _record_failure(
                        source_id,
                        str(exc),
                        correlation_id=correlation_id,
                        details={"cache_key": key_hash},
                    )
                    frame = validate_connector(source_id, self._store.load(record), lazy=True)
                    return RepositoryResult(
                        source_id=source_id,
                        frame=frame,
                        status=STATUS_STALE,
                        artifact_path=artifact_path,
                        cache_key=key_hash,
                        correlation_id=correlation_id,
                        metadata=metadata,
                    )
                _record_failure(
                    source_id,
                    str(exc),
                    correlation_id=correlation_id,
                    details={"cache_key": key_hash},
                )
                log_error(
                    context,
                    "fetch.connector-error",
                    status="error",
                    cache_key=key_hash,
                    query_signature=query_signature,
                    error=str(exc),
                )
                raise
            except Exception as exc:  # pragma: no cover - defensive guard
                wrapped = ConnectorError(
                    f"Connector '{source_id}' raised an unexpected error",
                    context={"source_id": source_id},
                )
                if record:
                    artifact_path = self._store.root / record.relative_path
                    metadata = {
                        "rows": record.rows,
                        "ttl_days": record.ttl_days,
                        "schema_version": record.schema_version,
                        "as_of": record.as_of,
                        "fallback_reason": str(wrapped),
                    }
                    log_warning(
                        context,
                        "fetch.fallback-unexpected",
                        status=STATUS_STALE,
                        cache_key=key_hash,
                        query_signature=query_signature,
                        artifact=str(artifact_path),
                        error=str(exc),
                    )
                    _record_failure(
                        source_id,
                        str(wrapped),
                        correlation_id=correlation_id,
                        details={"cache_key": key_hash},
                    )
                    frame = self._store.load(record)
                    return RepositoryResult(
                        source_id=source_id,
                        frame=frame,
                        status=STATUS_STALE,
                        artifact_path=artifact_path,
                        cache_key=key_hash,
                        correlation_id=correlation_id,
                        metadata=metadata,
                    )
                _record_failure(
                    source_id,
                    str(wrapped),
                    correlation_id=correlation_id,
                    details={"cache_key": key_hash},
                )
                log_error(
                    context,
                    "fetch.unexpected-error",
                    status="error",
                    cache_key=key_hash,
                    query_signature=query_signature,
                    error=str(exc),
                )
                raise wrapped from exc

            ttl_seconds = int(getattr(connector, "ttl_seconds", 86_400))
            ttl_days = max(1, math.ceil(ttl_seconds / 86_400)) if ttl_seconds > 0 else 0
            schema_version = _connector_schema_version(connector)

            lock_path = self._store.lock_path(source_id)
            with _source_lock(lock_path):
                record = self._store.write(
                    source_id=source_id,
                    key_hash=key_hash,
                    frame=frame,
                    ttl_days=ttl_days,
                    schema_version=schema_version,
                    created_at=self.clock(),
                )

            artifact_path = self._store.root / record.relative_path
            duration_ms = _elapsed_ms(started_at, self.clock())
            metadata = {
                "rows": record.rows,
                "ttl_days": record.ttl_days,
                "schema_version": record.schema_version,
                "as_of": record.as_of,
            }
            log_info(
                context,
                "fetch.connector-success",
                status=STATUS_REFRESHED,
                cache_key=key_hash,
                query_signature=query_signature,
                artifact=str(artifact_path),
                duration_ms=duration_ms,
                ttl_days=ttl_days,
            )
            return RepositoryResult(
                source_id=source_id,
                frame=frame,
                status=STATUS_REFRESHED,
                artifact_path=artifact_path,
                cache_key=key_hash,
                correlation_id=correlation_id,
                metadata=metadata,
            )

    def refresh(
        self, source_id: str, queries: Iterable[Mapping[str, Any]]
    ) -> list[RepositoryResult]:
        return [self.get(source_id, **query) for query in queries]

    def _resolve_connector(self, source_id: str) -> Connector:
        try:
            return self._connectors[source_id]
        except KeyError as exc:  # pragma: no cover - defensive guard
            raise CacheError(
                f"Connector '{source_id}' is not registered",
                context={"source_id": source_id},
            ) from exc


__all__ = [
    "CacheIndex",
    "CacheIndexRecord",
    "CacheStore",
    "Connector",
    "Repository",
    "RepositoryResult",
]
