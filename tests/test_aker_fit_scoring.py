from __future__ import annotations

import pandas as pd

from west_housing_model.scoring.aker_fit import compute_aker_fit


def test_default_weights_and_rounding() -> None:
    pillars = pd.DataFrame(
        {
            "pillar_uc": [0.33, 0.92],
            "pillar_oa": [0.50, 0.50],
            "pillar_ij": [0.10, 0.80],
            "pillar_sc": [0.90, 0.10],
        }
    )
    scores = compute_aker_fit(pillars)
    assert list(scores.astype(int)) == [46, 58]


def test_custom_weights_and_clamp() -> None:
    pillars = pd.DataFrame(
        {
            "pillar_uc": [1.5],  # out of bounds -> clamped
            "pillar_oa": [0.5],
            "pillar_ij": [0.5],
            "pillar_sc": [-1.0],  # out of bounds -> clamped
        }
    )
    w = {"pillar_uc": 0.5, "pillar_oa": 0.2, "pillar_ij": 0.2, "pillar_sc": 0.1}
    scores = compute_aker_fit(pillars, weights=w)
    assert int(scores.iloc[0]) == 70


def test_missing_pillars_treated_as_zero() -> None:
    pillars = pd.DataFrame(
        {
            "pillar_uc": [0.4],
            # oa missing
            "pillar_ij": [0.4],
            # sc missing
        }
    )
    scores = compute_aker_fit(pillars)
    # two present at 0.4 with equal weights -> 0.2 of total -> 20
    assert int(scores.iloc[0]) == 20
