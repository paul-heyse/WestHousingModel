from __future__ import annotations

import json
import os
import time

import pandas as pd
import pytest

from west_housing_model.features.ops_features import build_ops_features
from west_housing_model.features.place_features import build_place_features_from_components
from west_housing_model.features.site_features import build_site_features_from_components
from west_housing_model.valuation import ValuationInputs, run_valuation

THRESHOLD_SECONDS = float(os.getenv("PERF_SMOKE_THRESHOLD", "5.0"))


@pytest.mark.performance
def test_end_to_end_pipeline_performance(
    place_base_df: pd.DataFrame,
    place_components_df: pd.DataFrame,
    site_base_df: pd.DataFrame,
    site_hazards_df: pd.DataFrame,
    ops_rows_df: pd.DataFrame,
    scenario_payload: dict,
    record_property,
) -> None:
    start = time.perf_counter()

    place_features = build_place_features_from_components(
        place_base_df, place_components_df, as_of=pd.Timestamp("2025-01-01")
    )
    site_features = build_site_features_from_components(
        site_base_df, site_hazards_df, as_of=pd.Timestamp("2025-02-01")
    )

    ops_row = ops_rows_df.iloc[0]
    ops_features, _ = build_ops_features(
        property_id=str(ops_row["property_id"]),
        as_of=pd.to_datetime(ops_row["as_of"]),
        eia_state=ops_row.get("eia_state"),
        eia_res_price_cents_per_kwh=ops_row.get("eia_res_price_cents_per_kwh"),
        broadband_gbps_flag=ops_row.get("broadband_gbps_flag"),
        zoning_context_note=ops_row.get("zoning_context_note"),
        hud_fmr_2br=ops_row.get("hud_fmr_2br"),
    )

    valuation_inputs = ValuationInputs(
        scenario_id=scenario_payload["scenario_id"],
        property_id=scenario_payload["property_id"],
        as_of=pd.to_datetime(scenario_payload.get("as_of")),
        place_features=scenario_payload["place_features"],
        site_features=scenario_payload["site_features"],
        ops_features=scenario_payload["ops_features"],
        user_overrides=scenario_payload["user_overrides"],
    )
    valuation = run_valuation(valuation_inputs)

    duration = time.perf_counter() - start
    record_property("perf_smoke_seconds", duration)

    assert not place_features.empty
    assert not site_features.empty
    assert not ops_features.empty
    assert not valuation.empty
    report_path = os.getenv("PERF_SMOKE_REPORT")
    if report_path:
        with open(report_path, "w", encoding="utf-8") as handle:
            json.dump(
                {"duration_seconds": duration, "threshold_seconds": THRESHOLD_SECONDS}, handle
            )

    assert (
        duration < THRESHOLD_SECONDS
    ), f"Performance smoke test exceeded threshold: {duration:.3f}s >= {THRESHOLD_SECONDS:.2f}s"
