from __future__ import annotations

import pandas as pd

from west_housing_model.data.catalog import validate_table


def build_ops_features(
    property_id: str,
    as_of: pd.Timestamp,
    eia_state: str | None,
    eia_res_price_cents_per_kwh: float | None,
    broadband_gbps_flag: bool | None,
    zoning_context_note: str | None,
    hud_fmr_2br: float | None = None,
) -> pd.DataFrame:
    if eia_state and eia_res_price_cents_per_kwh is not None:
        note = f"Utilities ({eia_state} RES): {eia_res_price_cents_per_kwh:.1f} c/kWh"
    else:
        note = "Utilities: RES price unavailable"

    if eia_res_price_cents_per_kwh is not None:
        utilities_scaler = round(max(0.5, min(1.5, eia_res_price_cents_per_kwh / 12.0)), 3)
    else:
        utilities_scaler = pd.NA

    frame = pd.DataFrame(
        {
            "property_id": [property_id],
            "as_of": [as_of],
            "source_id": ["ops.features"],
            "utility_rate_note": [note],
            "broadband_gbps_flag": [
                bool(broadband_gbps_flag) if broadband_gbps_flag is not None else pd.NA
            ],
            "zoning_context_note": [zoning_context_note],
            "utilities_scaler": [utilities_scaler],
            "hud_fmr_2br": [hud_fmr_2br if hud_fmr_2br is not None else pd.NA],
        }
    )
    if "broadband_gbps_flag" in frame.columns:
        frame["broadband_gbps_flag"] = (
            frame["broadband_gbps_flag"]
            .apply(lambda value: bool(value) if not pd.isna(value) else value)
            .astype(object)
        )
    return validate_table("ops_features", frame)


__all__ = ["build_ops_features"]
