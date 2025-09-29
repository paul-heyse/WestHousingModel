"""Discounted cash flow model stub."""

from __future__ import annotations

from typing import Mapping

from west_housing_model.core.entities import Scenario


def run_dcf(scenario: Scenario) -> Mapping[str, float]:  # pragma: no cover - stub
    """Placeholder DCF computation returning an empty mapping."""

    return {}


__all__ = ["run_dcf"]
