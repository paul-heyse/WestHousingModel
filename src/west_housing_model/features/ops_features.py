from __future__ import annotations

from typing import Any, Dict, Tuple

import pandas as pd

from west_housing_model.data.catalog import validate_table


def _coerce_boolean(value: Any) -> object:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return pd.NA
    return bool(value)


def extract_ops_provenance(
    *,
    as_of: pd.Timestamp,
    eia_state: str | None,
    eia_res_price_cents_per_kwh: float | None,
    broadband_gbps_flag: bool | None,
    zoning_context_note: str | None,
    hud_fmr_2br: float | None,
) -> Dict[str, Dict[str, Any]]:
    provenance: Dict[str, Dict[str, Any]] = {}
    if eia_state is not None and eia_res_price_cents_per_kwh is not None:
        provenance["utility_rate_note"] = {
            "source_id": "connector.eia_v2",
            "as_of": as_of,
            "transformation": "scaled utilities note",
        }
        provenance["utilities_scaler"] = {
            "source_id": "connector.eia_v2",
            "as_of": as_of,
            "transformation": "res_price_cents_per_kwh/12 clamp",
        }
    else:
        provenance["utility_rate_note"] = {
            "source_id": "ops.features",
            "as_of": None,
            "transformation": "default",
        }
        provenance["utilities_scaler"] = {
            "source_id": "ops.features",
            "as_of": None,
            "transformation": "default",
        }

    provenance["broadband_gbps_flag"] = {
        "source_id": "connector.fcc_bdc" if broadband_gbps_flag is not None else "ops.features",
        "as_of": as_of if broadband_gbps_flag is not None else None,
        "transformation": "boolean" if broadband_gbps_flag is not None else "default",
    }

    provenance["zoning_context_note"] = {
        "source_id": "ops.features",
        "as_of": as_of if zoning_context_note is not None else None,
        "transformation": "pass-through" if zoning_context_note else "default",
    }

    provenance["hud_fmr_2br"] = {
        "source_id": "connector.hud_fmr" if hud_fmr_2br is not None else "ops.features",
        "as_of": as_of if hud_fmr_2br is not None else None,
        "transformation": "HUD FMR (2BR)" if hud_fmr_2br is not None else "default",
    }
    return provenance


def build_ops_features(
    property_id: str,
    as_of: pd.Timestamp,
    eia_state: str | None,
    eia_res_price_cents_per_kwh: float | None,
    broadband_gbps_flag: bool | None,
    zoning_context_note: str | None,
    hud_fmr_2br: float | None = None,
) -> Tuple[pd.DataFrame, Dict[str, Dict[str, Any]]]:
    if eia_state is not None and eia_res_price_cents_per_kwh is not None:
        note = f"Utilities ({eia_state} RES): {eia_res_price_cents_per_kwh:.1f} c/kWh"
        utilities_scaler = round(max(0.5, min(1.5, eia_res_price_cents_per_kwh / 12.0)), 3)
    else:
        note = "Utilities: RES price unavailable"
        utilities_scaler = pd.NA

    frame = pd.DataFrame(
        {
            "property_id": [property_id],
            "as_of": [as_of],
            "source_id": ["ops.features"],
            "utility_rate_note": [note],
            "broadband_gbps_flag": [_coerce_boolean(broadband_gbps_flag)],
            "zoning_context_note": [zoning_context_note],
            "utilities_scaler": [utilities_scaler],
            "hud_fmr_2br": [hud_fmr_2br if hud_fmr_2br is not None else pd.NA],
        }
    )

    validated = validate_table("ops_features", frame)
    provenance = extract_ops_provenance(
        as_of=as_of,
        eia_state=eia_state,
        eia_res_price_cents_per_kwh=eia_res_price_cents_per_kwh,
        broadband_gbps_flag=broadband_gbps_flag,
        zoning_context_note=zoning_context_note,
        hud_fmr_2br=hud_fmr_2br,
    )
    return validated, provenance


__all__ = ["build_ops_features", "extract_ops_provenance"]
