"""Runtime settings helpers for scoring weights.

Weights can be overridden via environment variables; defaults follow the
architecture spec (equal weights for pillars, 45/35/20 for returns).
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING, Dict

if TYPE_CHECKING:
    from west_housing_model.scoring.deal_quality import ReturnsWeights


def _get_env_float(name: str, default: float) -> float:
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        return float(raw)
    except (TypeError, ValueError):
        return default


def get_pillar_weights() -> Dict[str, float]:
    """Return normalized pillar weights from environment or defaults."""

    weights = {
        "pillar_uc": _get_env_float("WHM_PILLAR_WEIGHT_UC", 0.25),
        "pillar_oa": _get_env_float("WHM_PILLAR_WEIGHT_OA", 0.25),
        "pillar_ij": _get_env_float("WHM_PILLAR_WEIGHT_IJ", 0.25),
        "pillar_sc": _get_env_float("WHM_PILLAR_WEIGHT_SC", 0.25),
    }
    total = sum(weights.values())
    if total <= 0:
        return {key: 0.25 for key in weights}
    return {key: value / total for key, value in weights.items()}


def get_returns_weights() -> "ReturnsWeights":
    """Return ReturnsWeights with environment overrides normalized."""

    from west_housing_model.scoring.deal_quality import ReturnsWeights

    w_yoc = _get_env_float("WHM_RETURNS_WEIGHT_YOC", 0.45)
    w_irr = _get_env_float("WHM_RETURNS_WEIGHT_IRR", 0.35)
    w_dscr = _get_env_float("WHM_RETURNS_WEIGHT_DSCR", 0.20)
    total = w_yoc + w_irr + w_dscr
    if total <= 0:
        return ReturnsWeights()
    return ReturnsWeights(
        yoy_yoc=w_yoc / total,
        irr_5yr=w_irr / total,
        dscr=w_dscr / total,
    )


__all__ = ["get_pillar_weights", "get_returns_weights"]
