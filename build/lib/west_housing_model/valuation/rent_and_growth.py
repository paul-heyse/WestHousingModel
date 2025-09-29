"""Rent baseline and growth model stub."""

from __future__ import annotations

from typing import Mapping

from west_housing_model.core.entities import Scenario


def project_rent_growth(scenario: Scenario) -> Mapping[str, float]:  # pragma: no cover - stub
    """Placeholder rent growth projection."""

    return {}


__all__ = ["project_rent_growth"]
