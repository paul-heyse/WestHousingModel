from __future__ import annotations

from typing import Any, Dict, Optional

import pandas as pd

from west_housing_model.data.catalog import validate_table


def build_site_features_from_components(
    base: pd.DataFrame, hazards: pd.DataFrame, *, as_of: Optional[pd.Timestamp] = None
) -> pd.DataFrame:
    """Very small stub that pivots minimal hazards into columns and validates.

    This supports CLI tests; full implementation can be restored later.
    """

    out = base.copy(deep=True)
    if as_of is not None:
        out["as_of"] = as_of
    # Map a couple hazard rows into columns if present
    for _, row in hazards.iterrows():
        hid = row.get("hazard_type")
        if hid == "in_sfha":
            out["in_sfha"] = bool(str(row.get("flag", "")).lower() == "true")
        elif hid == "wildfire_risk_percentile":
            try:
                out["wildfire_risk_percentile"] = int(row.get("value"))
            except Exception:
                out["wildfire_risk_percentile"] = pd.NA
        elif hid == "pga_10in50_g":
            try:
                out["pga_10in50_g"] = float(row.get("value"))
            except Exception:
                out["pga_10in50_g"] = pd.NA
        elif hid == "winter_storms_10yr_county":
            try:
                out["winter_storms_10yr_county"] = int(row.get("value"))
            except Exception:
                out["winter_storms_10yr_county"] = pd.NA
        elif hid == "minutes_to_trailhead":
            try:
                out["minutes_to_trailhead"] = float(row.get("value"))
            except Exception:
                out["minutes_to_trailhead"] = pd.NA
        elif hid == "hdd_annual":
            out["hdd_annual"] = float(row.get("value"))
        elif hid == "cdd_annual":
            out["cdd_annual"] = float(row.get("value"))
        elif hid == "rail_within_300m_flag":
            out["rail_within_300m_flag"] = bool(row.get("flag"))
        elif hid == "broadband_gbps_flag":
            flag_value = row.get("flag", row.get("value"))
            if flag_value is None or (isinstance(flag_value, float) and pd.isna(flag_value)):
                out["broadband_gbps_flag"] = pd.NA
            else:
                out["broadband_gbps_flag"] = bool(flag_value)
    # Minimal metadata
    if "source_id" not in out.columns:
        out["source_id"] = "site.features"
    if "as_of" not in out.columns:
        # fallback to first hazard as_of if present
        if "as_of" in hazards.columns and not hazards.empty:
            out["as_of"] = hazards.iloc[0]["as_of"]
        else:
            out["as_of"] = pd.NaT
    for column in ("in_sfha", "rail_within_300m_flag", "broadband_gbps_flag"):
        if column in out.columns:
            out[column] = (
                out[column]
                .apply(lambda value: bool(value) if not pd.isna(value) else value)
                .astype(object)
            )
    # Ensure required numeric columns exist even if input missing
    defaults: Dict[str, Any] = {
        "in_sfha": pd.NA,
        "wildfire_risk_percentile": pd.NA,
        "pga_10in50_g": pd.NA,
        "winter_storms_10yr_county": pd.NA,
        "minutes_to_trailhead": pd.NA,
        "broadband_gbps_flag": pd.NA,
    }
    for column, default in defaults.items():
        if column not in out.columns:
            out[column] = default
    return validate_table("site_features", out)


def extract_provenance(hazards: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
    """Create a simple provenance dict keyed by hazard_type -> {source_id, as_of}.

    This is used by UI tooltips tests.
    """
    prov: Dict[str, Dict[str, Any]] = {}
    for _, row in hazards.iterrows():
        h = str(row.get("hazard_type"))
        prov[h] = {
            "source_id": row.get("source_id"),
            "as_of": row.get("as_of"),
        }
    return prov


__all__ = ["build_site_features_from_components", "extract_provenance"]
