"""Place-level feature pipeline stubs."""

from __future__ import annotations

from typing import Mapping

from west_housing_model.core.entities import Place


def build_place_features(place: Place) -> Mapping[str, float]:  # pragma: no cover - stub
    """Compute pillar features for a place. Placeholder returning an empty mapping."""

    return {}


__all__ = ["build_place_features"]
