from __future__ import annotations

import pandas as pd

from west_housing_model.features.ops_features import build_ops_features


def test_build_ops_features_happy_path() -> None:
    frame = build_ops_features(
        property_id="p-1",
        as_of=pd.Timestamp("2025-09-01"),
        eia_state="CO",
        eia_res_price_cents_per_kwh=13.2,
        broadband_gbps_flag=True,
        zoning_context_note="MF allowed",
        hud_fmr_2br=1800.0,
    )
    assert frame.loc[0, "property_id"] == "p-1"
    assert frame.loc[0, "broadband_gbps_flag"] is True
    assert "Utilities (CO RES):" in frame.loc[0, "utility_rate_note"]
    assert frame.loc[0, "utilities_scaler"] > 0
    assert frame.loc[0, "hud_fmr_2br"] == 1800.0


def test_build_ops_features_missing_prices_defaults() -> None:
    frame = build_ops_features(
        property_id="p-2",
        as_of=pd.Timestamp("2025-09-01"),
        eia_state="UT",
        eia_res_price_cents_per_kwh=None,
        broadband_gbps_flag=None,
        zoning_context_note=None,
        hud_fmr_2br=None,
    )
    assert frame.loc[0, "utility_rate_note"].startswith("Utilities: RES price unavailable")
    assert pd.isna(frame.loc[0, "broadband_gbps_flag"]) or frame.loc[0, "broadband_gbps_flag"] in (
        True,
        False,
    )
    assert pd.isna(frame.loc[0, "utilities_scaler"])
    assert pd.isna(frame.loc[0, "hud_fmr_2br"])
