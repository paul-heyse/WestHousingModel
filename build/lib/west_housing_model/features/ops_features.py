"""Operating context feature stubs."""

from __future__ import annotations

from typing import Mapping

from west_housing_model.core.entities import Property


def build_ops_features(property_: Property) -> Mapping[str, float]:  # pragma: no cover - stub
    """Placeholder for operating context feature computation."""

    return {}


__all__ = ["build_ops_features"]
