"""Deal Quality scoring engine.

Compute Deal Quality (0..100) as Returns minus Penalties. Returns are a
weighted aggregation of YoC, IRR, and DSCR mapped to 0..100 via piecewise
tables. Penalties include hazards, supply, affordability, and data confidence.
All computations are pure and deterministic.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class ReturnsWeights:
    yoy_yoc: float = 0.45
    irr_5yr: float = 0.35
    dscr: float = 0.20


DEFAULT_RETURNS_WEIGHTS = ReturnsWeights()


def _map_piecewise(
    value: float, points: list[tuple[float, int]], *, higher_is_better: bool = True
) -> int:
    """Map a numeric value to a score using ordered breakpoints.

    points: list of (threshold, score). For higher_is_better, thresholds are
    ascending with increasing scores; otherwise descending.
    """

    if np.isnan(value):
        return 0
    v = float(value)
    sel = points if higher_is_better else sorted(points, key=lambda x: x[0], reverse=True)
    score = sel[0][1]
    for t, s in sel:
        if (higher_is_better and v >= t) or ((not higher_is_better) and v <= t):
            score = s
    return int(score)


def _score_returns(
    yoc: float | None,
    irr: float | None,
    dscr: float | None,
    weights: ReturnsWeights = DEFAULT_RETURNS_WEIGHTS,
) -> float:
    # Tables from architecture defaults
    # YoC: 5.5%→40; 6.0%→55; 6.5%→70; 7.0%→85; ≥7.5%→95
    yoc_pts = [(5.5, 40), (6.0, 55), (6.5, 70), (7.0, 85), (7.5, 95)]
    # IRR: 10%→40; 12%→60; 14%→80; ≥16%→92
    irr_pts = [(10.0, 40), (12.0, 60), (14.0, 80), (16.0, 92)]
    # DSCR: 1.20x→40; 1.25x→55; 1.30x→70; 1.40x→90
    dscr_pts = [(1.20, 40), (1.25, 55), (1.30, 70), (1.40, 90)]

    yoc_s = _map_piecewise(yoc if yoc is not None else np.nan, yoc_pts, higher_is_better=True)
    irr_s = _map_piecewise(irr if irr is not None else np.nan, irr_pts, higher_is_better=True)
    dscr_s = _map_piecewise(dscr if dscr is not None else np.nan, dscr_pts, higher_is_better=True)
    total_w = float(weights.yoy_yoc + weights.irr_5yr + weights.dscr) or 1.0
    return (yoc_s * weights.yoy_yoc + irr_s * weights.irr_5yr + dscr_s * weights.dscr) / total_w


def _hazard_penalty(
    in_sfha: bool | None,
    wildfire_pct: float | None,
    pga_g: float | None,
    winter_events: float | None,
) -> int:
    pen = 0
    if in_sfha:
        pen += 10
    if wildfire_pct is not None:
        if wildfire_pct >= 90:
            pen += 10
        elif wildfire_pct >= 75:
            pen += 5
    if pga_g is not None and pga_g >= 0.15:
        pen += 5
    if winter_events is not None:
        # high winter events → -3 to -6; use simple two-tier
        if winter_events >= 90:
            pen += 6
        elif winter_events >= 75:
            pen += 3
    return pen


def _supply_penalty(permits_per_1k_hh: float | None) -> int:
    if permits_per_1k_hh is None:
        return 0
    if permits_per_1k_hh >= 90:
        return 10
    if permits_per_1k_hh >= 75:
        return 5
    return 0


def _affordability_penalty(
    rent_to_income: float | None, threshold: float = 0.35, overridden: bool = False
) -> int:
    if overridden or rent_to_income is None:
        return 0
    if rent_to_income > threshold:
        # scale penalty modestly up to +15
        excess = min(0.15, rent_to_income - threshold)
        return 5 + int(round(10 * (excess / 0.15)))
    return 0


def _data_confidence_penalty(missing_or_stale: int | None) -> int:
    if not missing_or_stale:
        return 0
    # small penalty per missing key feature, capped at 10
    return int(min(10, max(0, missing_or_stale) * 2))


def compute_deal_quality(
    *,
    yoc: float | None,
    irr_5yr: float | None,
    dscr: float | None,
    in_sfha: bool | None = None,
    wildfire_risk_percentile: float | None = None,
    pga_10in50_g: float | None = None,
    winter_storms_10yr_county_percentile: float | None = None,
    permits_5plus_per_1k_hh_percentile: float | None = None,
    rent_to_income: float | None = None,
    affordability_overridden: bool = False,
    missing_or_stale_features_count: int | None = None,
    returns_weights: ReturnsWeights = DEFAULT_RETURNS_WEIGHTS,
) -> int:
    """Compute Deal Quality 0..100.

    All inputs are primitive scalars already normalized upstream where relevant
    (e.g., percentiles). The function clamps and guards against Nones.
    """

    returns_score = _score_returns(yoc, irr_5yr, dscr, returns_weights)
    penalties = 0
    penalties += _hazard_penalty(
        in_sfha, wildfire_risk_percentile, pga_10in50_g, winter_storms_10yr_county_percentile
    )
    penalties += _supply_penalty(permits_5plus_per_1k_hh_percentile)
    penalties += _affordability_penalty(rent_to_income, overridden=affordability_overridden)
    penalties += _data_confidence_penalty(missing_or_stale_features_count)

    score = int(round(returns_score - penalties))
    return int(max(0, min(100, score)))


__all__ = ["compute_deal_quality", "ReturnsWeights", "DEFAULT_RETURNS_WEIGHTS"]
