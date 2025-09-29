from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Mapping, MutableMapping, Optional

import pandas as pd

SPEC_VERSION = "1.0"


@dataclass(frozen=True)
class Scenario:
    scenario_id: str
    property_id: str
    as_of: Optional[pd.Timestamp]
    user_overrides: Mapping[str, Any]
    source_manifest: Mapping[str, Any]
    spec_version: str = SPEC_VERSION


def build_manifest(*, as_of: pd.Timestamp, sources: Mapping[str, str]) -> Dict[str, Any]:
    return {"as_of": as_of.strftime("%Y-%m"), "sources": dict(sources)}


def choose_manifest(
    *, locked: bool, saved_manifest: Mapping[str, Any], current_manifest: Mapping[str, Any]
) -> Mapping[str, Any]:
    return saved_manifest if locked else current_manifest


def deterministic_export_filename(kind: str, scenario_id: str, as_of: str) -> str:
    return (
        f"valuation-{scenario_id}-{as_of}-onepager.pdf"
        if kind == "pdf"
        else f"valuation-{scenario_id}-{as_of}.csv"
    )


def save_scenario(store: MutableMapping[str, Any], scenario: Scenario) -> None:
    store["scenario"] = {
        "scenario_id": scenario.scenario_id,
        "property_id": scenario.property_id,
        "as_of": scenario.as_of.strftime("%Y-%m") if scenario.as_of is not None else None,
        "user_overrides": dict(scenario.user_overrides),
        "source_manifest": dict(scenario.source_manifest),
        "spec_version": scenario.spec_version,
    }


def load_scenario(store: Mapping[str, Any]) -> Optional[Scenario]:
    raw = store.get("scenario")
    if not raw:
        return None
    as_of = pd.Timestamp(raw["as_of"]) if raw.get("as_of") else None
    return Scenario(
        scenario_id=str(raw["scenario_id"]),
        property_id=str(raw["property_id"]),
        as_of=as_of,
        user_overrides=dict(raw.get("user_overrides", {})),
        source_manifest=dict(raw.get("source_manifest", {})),
        spec_version=str(raw.get("spec_version", SPEC_VERSION)),
    )


__all__ = [
    "SPEC_VERSION",
    "Scenario",
    "build_manifest",
    "choose_manifest",
    "deterministic_export_filename",
    "save_scenario",
    "load_scenario",
]
