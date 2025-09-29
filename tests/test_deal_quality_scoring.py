from __future__ import annotations

from west_housing_model.scoring.deal_quality import compute_deal_quality


def test_returns_mapping_and_weights() -> None:
    # Strong returns: expect high baseline before penalties
    score = compute_deal_quality(yoc=7.2, irr_5yr=16.5, dscr=1.35)
    assert 80 <= score <= 100


def test_hazard_and_supply_penalties() -> None:
    base = compute_deal_quality(yoc=6.5, irr_5yr=14.0, dscr=1.30)
    penalized = compute_deal_quality(
        yoc=6.5,
        irr_5yr=14.0,
        dscr=1.30,
        in_sfha=True,
        wildfire_risk_percentile=92,
        pga_10in50_g=0.2,
        winter_storms_10yr_county_percentile=90,
        permits_5plus_per_1k_hh_percentile=90,
    )
    assert penalized < base


def test_affordability_and_data_confidence_penalties() -> None:
    base = compute_deal_quality(yoc=6.0, irr_5yr=12.0, dscr=1.25, rent_to_income=0.30)
    penal = compute_deal_quality(yoc=6.0, irr_5yr=12.0, dscr=1.25, rent_to_income=0.40, missing_or_stale_features_count=3)
    assert penal < base


def test_clamping_bounds() -> None:
    low = compute_deal_quality(yoc=5.5, irr_5yr=10.0, dscr=1.20, in_sfha=True, wildfire_risk_percentile=99, pga_10in50_g=0.3, permits_5plus_per_1k_hh_percentile=99, missing_or_stale_features_count=10)
    high = compute_deal_quality(yoc=10.0, irr_5yr=30.0, dscr=3.0)
    assert low >= 0 and high <= 100


