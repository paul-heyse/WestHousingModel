"""Site-level feature pipeline stubs."""

from __future__ import annotations

from typing import Mapping

from west_housing_model.core.entities import Property


def build_site_features(property_: Property) -> Mapping[str, float]:  # pragma: no cover - stub
    """Compute features for a property candidate. Placeholder returning an empty mapping."""

    return {}


__all__ = ["build_site_features"]
