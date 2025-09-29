from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml  # type: ignore[import-untyped]

from WestHousingModel.core.exceptions import RegistryError

_REQUIRED_FIELDS: Tuple[str, ...] = (
    "id",
    "enabled",
    "endpoint",
    "geography",
    "cadence",
    "cache_ttl_days",
    "license",
    "rate_limit",
)

_OPTIONAL_FIELDS: Tuple[str, ...] = ("auth_key_name", "notes")

_GEO_ALLOWED = {"msa", "county", "tract", "point"}
_CADENCE_ALLOWED = {"monthly", "quarterly", "annual", "as-updated"}


@dataclass(frozen=True)
class SourceSpec:
    id: str
    enabled: bool
    endpoint: str
    geography: str
    cadence: str
    cache_ttl_days: int
    license: str
    rate_limit: str
    auth_key_name: Optional[str] = None
    notes: Optional[str] = None


def _load_yaml(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {"sources": []}
    try:
        with path.open("r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh) or {}
        if not isinstance(data, dict):
            raise RegistryError(f"Registry file is not a mapping: {path}")
        if "sources" not in data or data["sources"] is None:
            data["sources"] = []
        if not isinstance(data["sources"], list):
            raise RegistryError(f"'sources' must be a list in {path}")
        return data
    except yaml.YAMLError as exc:
        raise RegistryError(f"Failed to parse YAML: {path}: {exc}") from exc


def _merge_sources(
    base: List[Dict[str, Any]], overlay: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    by_id: Dict[str, Dict[str, Any]] = {}
    for s in base:
        if not isinstance(s, dict):
            continue
        sid = s.get("id")
        if not isinstance(sid, str) or not sid:
            continue
        by_id[sid] = dict(s)
    for s in overlay:
        if not isinstance(s, dict):
            continue
        sid = s.get("id")
        if not isinstance(sid, str) or not sid:
            # skip invalid overlay entries without string id
            continue
        current = by_id.get(sid, {})
        current.update({k: v for k, v in s.items() if v is not None})
        by_id[sid] = current
    # preserve deterministic order: base ids then new overlay-only ids sorted
    base_ids: List[str] = []
    for s in base:
        if isinstance(s, dict):
            sid = s.get("id")
            if isinstance(sid, str) and sid:
                base_ids.append(sid)
    new_ids = sorted([k for k in by_id.keys() if k not in base_ids])
    ordered: List[str] = base_ids + new_ids
    return [by_id[i] for i in ordered]


def _validate_source(raw: Dict[str, Any], origin: str) -> SourceSpec:
    sid = raw.get("id")
    if not sid:
        raise RegistryError(f"Missing required field 'id' in {origin}")
    missing = [f for f in _REQUIRED_FIELDS if f not in raw]
    if missing:
        raise RegistryError(f"Source '{sid}': missing required field(s): {', '.join(missing)}")
    # enums
    geo = raw["geography"]
    cad = raw["cadence"]
    if geo not in _GEO_ALLOWED:
        raise RegistryError(
            f"Source '{sid}': invalid geography '{geo}' (allowed: {sorted(_GEO_ALLOWED)})"
        )
    if cad not in _CADENCE_ALLOWED:
        raise RegistryError(
            f"Source '{sid}': invalid cadence '{cad}' (allowed: {sorted(_CADENCE_ALLOWED)})"
        )
    # types (minimal)
    try:
        cache_ttl_days = int(raw["cache_ttl_days"])
    except Exception as exc:  # noqa: BLE001
        raise RegistryError(f"Source '{sid}': cache_ttl_days must be int") from exc
    # unknown fields warning: ignored here; surfaced via return value notes
    allowed = set(_REQUIRED_FIELDS) | set(_OPTIONAL_FIELDS) | {"id"}
    unknown = [k for k in raw.keys() if k not in allowed]
    notes = raw.get("notes")
    if unknown:
        suffix = f" | Unknown fields: {', '.join(sorted(unknown))}"
        notes = (notes + suffix) if isinstance(notes, str) else suffix
    return SourceSpec(
        id=sid,
        enabled=bool(raw["enabled"]),
        endpoint=str(raw["endpoint"]),
        geography=str(geo),
        cadence=str(cad),
        cache_ttl_days=cache_ttl_days,
        license=str(raw["license"]),
        rate_limit=str(raw["rate_limit"]),
        auth_key_name=raw.get("auth_key_name"),
        notes=notes,
    )


def load_registry(
    base_path: Path | str = "config/sources.yml",
    supplement_path: Path | str = "config/sources_supplement.yml",
) -> List[SourceSpec]:
    base_p = Path(base_path)
    sup_p = Path(supplement_path)
    base = _load_yaml(base_p)["sources"]
    sup = _load_yaml(sup_p)["sources"]
    merged = _merge_sources(base, sup)
    validated: List[SourceSpec] = []
    for entry in merged:
        spec = _validate_source(entry, origin=str(base_p if entry in base else sup_p))
        validated.append(spec)
    return validated


def load_data_dictionary(registry: Optional[List[SourceSpec]] = None) -> List[Dict[str, Any]]:
    """Produce a simple data dictionary for UI consumption.

    Returns a list of dicts with keys: id, geography, cadence, cache_ttl_days, license, notes, enabled.
    """
    if registry is None:
        registry = load_registry()
    return [
        {
            "id": s.id,
            "enabled": s.enabled,
            "geography": s.geography,
            "cadence": s.cadence,
            "cache_ttl_days": s.cache_ttl_days,
            "license": s.license,
            "notes": s.notes or "",
        }
        for s in registry
    ]
