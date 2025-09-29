from __future__ import annotations

import json
import logging
import threading
import time
from dataclasses import dataclass, field

from functools import lru_cache
from pathlib import Path
from typing import Any, Callable, Mapping

import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry


_LOGGER = logging.getLogger(__name__)


class FixtureNotFoundError(FileNotFoundError):
    """Raised when a fixture lookup fails."""


@dataclass(slots=True)
class FixturePlayback:
    """Simple filesystem-backed fixture loader for connector replay tests."""

    root: Path
    decoder: Callable[[str], Any] = json.loads

    def resolve(self, key: str) -> Path:
        path = self.root / key
        if path.suffix:
            candidate = path
        else:
            candidate = path.with_suffix(".json")
        if not candidate.exists():
            raise FixtureNotFoundError(f"Fixture not found: {candidate}")
        return candidate

    def json(self, key: str) -> Any:
        path = self.resolve(key)
        _LOGGER.debug("Loading connector fixture", extra={"fixture": str(path)})
        return self.decoder(path.read_text())


@dataclass(slots=True)
class HttpFetcher:
    """Reusable HTTP helper with retries, rate limiting, and fixture playback."""

    base_url: str
    session: requests.Session | None = None
    retries: int = 3
    backoff_factor: float = 0.5
    timeout: float = 60.0
    rate_limit_per_sec: float | None = None
    fixture: FixturePlayback | None = None
    _lock: threading.Lock = field(default_factory=threading.Lock, init=False)
    _last_request_ts: float = field(default=0.0, init=False)

    def __post_init__(self) -> None:
        session = self._ensure_session()
        adapter = HTTPAdapter(
            max_retries=Retry(
                total=self.retries,
                backoff_factor=self.backoff_factor,
                status_forcelist=(429, 500, 502, 503, 504),
                allowed_methods=("GET", "POST"),
            )
        )
        session.mount("http://", adapter)
        session.mount("https://", adapter)

    def _ensure_session(self) -> requests.Session:
        if self.session is None:
            self.session = requests.Session()
        return self.session

    def _respect_rate_limit(self) -> None:
        if self.rate_limit_per_sec and self.rate_limit_per_sec > 0:
            min_interval = 1.0 / self.rate_limit_per_sec
            with self._lock:
                now = time.monotonic()
                elapsed = now - self._last_request_ts
                if elapsed < min_interval:
                    time.sleep(min_interval - elapsed)
                    now = time.monotonic()
                self._last_request_ts = now

    def get_json(
        self,
        path: str,
        *,
        params: Mapping[str, Any] | None = None,
        headers: Mapping[str, str] | None = None,
        fixture_key: str | None = None,
    ) -> Any:
        if self.fixture is not None:
            key = fixture_key or self._fixture_key_from_request(path, params)
            return self.fixture.json(key)

        self._respect_rate_limit()
        url = self._build_url(path)
        session = self._ensure_session()
        response = session.get(url, params=params, headers=headers, timeout=self.timeout)
        _LOGGER.debug(
            "HTTP GET",
            extra={
                "url": response.url,
                "status": response.status_code,
                "path": path,
                "params": dict(params or {}),
            },
        )
        response.raise_for_status()
        return response.json()

    def _build_url(self, path: str) -> str:
        if path.startswith("http://") or path.startswith("https://"):
            return path
        return f"{self.base_url.rstrip('/')}/{path.lstrip('/')}"

    def _fixture_key_from_request(
        self, path: str, params: Mapping[str, Any] | None
    ) -> str:
        if params:
            serialised = "&".join(
                f"{key}={value}" for key, value in sorted(params.items(), key=lambda item: item[0])
            )
            return f"{path.replace('/', '_')}__{serialised}"
        return path.replace("/", "_")


@lru_cache(maxsize=None)
def load_static_records(name: str) -> list[dict[str, Any]]:
    """Load packaged JSON fixture for offline connector workflows."""

    static_dir = Path(__file__).with_name("static")
    path = static_dir / f"{name}.json"
    if not path.exists():
        raise FixtureNotFoundError(f"Static dataset not found: {path}")
    return json.loads(path.read_text())


__all__ = ["FixturePlayback", "HttpFetcher", "FixtureNotFoundError", "load_static_records"]
