"""Capex and contingency model stub."""

from __future__ import annotations

from typing import Sequence

from west_housing_model.core.entities import CapexItem


def summarize_capex_plan(plan: Sequence[CapexItem]) -> float:  # pragma: no cover - stub
    """Placeholder summarizing the total capex plan amount."""

    return sum(item.amount for item in plan)


__all__ = ["summarize_capex_plan"]
