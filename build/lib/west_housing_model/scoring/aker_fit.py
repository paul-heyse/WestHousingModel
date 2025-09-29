"""Aker Fit scoring stub."""

from __future__ import annotations

from typing import Mapping

from west_housing_model.core.entities import Place


def score_place(place: Place) -> Mapping[str, float]:  # pragma: no cover - stub
    """Placeholder for future Aker Fit scoring implementation."""

    return {"aker_fit": 0.0}


__all__ = ["score_place"]
