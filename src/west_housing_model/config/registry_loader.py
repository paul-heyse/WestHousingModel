from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Sequence

import yaml  # type: ignore[import-untyped]

from west_housing_model.core.exceptions import RegistryError


@dataclass(frozen=True)
class SourceConfig:
    id: str
    enabled: bool
    endpoint: str
    geography: str
    cadence: str
    cache_ttl_days: int
    license: str
    rate_limit: str
    notes: str | None = None

    @classmethod
    def from_payload(cls, payload: Mapping[str, Any]) -> "SourceConfig":
        missing = [key for key in cls._required_fields() if key not in payload]
        if missing:
            raise RegistryError(
                f"Source '{payload.get('id', '<unknown>')}' missing required fields: {', '.join(missing)}",
                context={"missing": missing, "payload": dict(payload)},
            )
        return cls(
            id=str(payload["id"]),
            enabled=bool(payload.get("enabled", True)),
            endpoint=str(payload["endpoint"]),
            geography=str(payload["geography"]),
            cadence=str(payload["cadence"]),
            cache_ttl_days=int(payload["cache_ttl_days"]),
            license=str(payload["license"]),
            rate_limit=str(payload.get("rate_limit", "unknown")),
            notes=str(payload.get("notes")) if payload.get("notes") is not None else None,
        )

    def merged(self, payload: Mapping[str, Any]) -> "SourceConfig":
        data: Dict[str, Any] = {
            "enabled": payload.get("enabled", self.enabled),
            "endpoint": payload.get("endpoint", self.endpoint),
            "geography": payload.get("geography", self.geography),
            "cadence": payload.get("cadence", self.cadence),
            "cache_ttl_days": payload.get("cache_ttl_days", self.cache_ttl_days),
            "license": payload.get("license", self.license),
            "rate_limit": payload.get("rate_limit", self.rate_limit),
            "notes": payload.get("notes", self.notes),
        }
        return replace(self, **data)

    @classmethod
    def _required_fields(cls) -> Sequence[str]:
        return (
            "id",
            "endpoint",
            "geography",
            "cadence",
            "cache_ttl_days",
            "license",
            "rate_limit",
        )


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _load_sources(path: Path | None) -> List[Mapping[str, Any]]:
    if path is None or not path.exists():
        return []
    raw = yaml.safe_load(path.read_text()) or {}
    sources = raw.get("sources", [])
    if not isinstance(sources, list):
        raise RegistryError(
            "Registry file must define a list under 'sources'", context={"path": str(path)}
        )
    return [entry for entry in sources if isinstance(entry, Mapping)]


def load_registry(
    base_path: Path | None = None, supplement_path: Path | None = None
) -> List[SourceConfig]:
    if base_path is None:
        root = _repo_root()
        base_path = root / "config" / "sources.yml"
    entries: MutableMapping[str, SourceConfig] = {}
    for payload in _load_sources(base_path):
        config = SourceConfig.from_payload(payload)
        entries[config.id] = config
    if supplement_path is None:
        supplement_path = _repo_root() / "config" / "sources_supplement.yml"
    for payload in _load_sources(supplement_path):
        source_id = payload.get("id")
        if not source_id:
            raise RegistryError(
                "Supplemental entry missing 'id'", context={"payload": dict(payload)}
            )
        if source_id in entries:
            entries[source_id] = entries[source_id].merged(payload)
        else:
            entries[source_id] = SourceConfig.from_payload(payload)
    return list(entries.values())


def load_data_dictionary(
    registry: Iterable[SourceConfig] | None = None,
) -> List[Dict[str, Any]]:
    configs = list(registry) if registry is not None else load_registry()
    return [
        {
            "id": cfg.id,
            "enabled": cfg.enabled,
            "endpoint": cfg.endpoint,
            "geography": cfg.geography,
            "cadence": cfg.cadence,
            "cache_ttl_days": cfg.cache_ttl_days,
            "license": cfg.license,
            "rate_limit": cfg.rate_limit,
            "notes": cfg.notes,
        }
        for cfg in configs
    ]


__all__ = ["load_registry", "load_data_dictionary", "SourceConfig"]
