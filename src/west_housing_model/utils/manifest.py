from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Mapping, Optional, cast

import pandas as pd


def _dt(value: Any) -> Optional[str]:
    try:
        ts = cast(pd.Timestamp, pd.Timestamp(value))
    except Exception:
        return None
    if pd.isna(ts):
        return None
    if ts.tzinfo is not None:
        ts = ts.tz_convert(None)
    return cast(str, ts.strftime("%Y-%m"))


def build_source_manifest(
    *,
    as_of: Optional[Any] = None,
    place_features: Mapping[str, Any] | None = None,
    site_features: Mapping[str, Any] | None = None,
    ops_features: Mapping[str, Any] | None = None,
    hazards: Optional[pd.DataFrame] = None,
) -> Dict[str, Any]:
    """Compose a minimal source manifest mapping source_id->as_of string.

    Inputs are light dict-like structures; if a hazards dataframe is provided,
    its first row's `as_of` and `source_id` per `hazard_type` are captured.
    """

    sources: Dict[str, str] = {}

    def add(source_id: Optional[str], observed: Optional[Any]) -> None:
        if not source_id:
            return
        iso = _dt(observed) or (as_of and _dt(as_of)) or None
        if iso is None:
            iso = datetime.now(timezone.utc).strftime("%Y-%m")
        sources[str(source_id)] = iso

    if place_features:
        add(str(place_features.get("source_id")), place_features.get("as_of"))
    if site_features:
        add(str(site_features.get("source_id")), site_features.get("as_of"))
    if ops_features:
        add(str(ops_features.get("source_id")), ops_features.get("as_of"))

    if hazards is not None and not hazards.empty:
        for _, row in hazards.iterrows():
            add(str(row.get("source_id")), row.get("as_of"))

    return {
        "as_of": _dt(as_of) or datetime.now(timezone.utc).strftime("%Y-%m"),
        "sources": sources,
    }


__all__ = ["build_source_manifest"]
