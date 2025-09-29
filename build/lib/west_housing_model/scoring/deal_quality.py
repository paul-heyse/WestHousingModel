"""Deal Quality scoring stub."""

from __future__ import annotations

from typing import Mapping

from west_housing_model.core.entities import Property, Scenario


def score_deal(property_: Property, scenario: Scenario) -> Mapping[str, float]:  # pragma: no cover - stub
    """Placeholder for Deal Quality scoring implementation."""

    return {"deal_quality": 0.0}


__all__ = ["score_deal"]
