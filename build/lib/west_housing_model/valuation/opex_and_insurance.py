"""Operating expense and insurance model stub."""

from __future__ import annotations

from typing import Mapping

from west_housing_model.core.entities import Property, Scenario


def estimate_operating_costs(
    property_: Property, scenario: Scenario
) -> Mapping[str, float]:  # pragma: no cover - stub
    """Placeholder operating expense estimator."""

    return {}


__all__ = ["estimate_operating_costs"]
