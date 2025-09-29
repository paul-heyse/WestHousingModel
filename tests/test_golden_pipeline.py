from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest

from west_housing_model.features.ops_features import build_ops_features
from west_housing_model.features.place_features import build_place_features_from_components
from west_housing_model.features.site_features import build_site_features_from_components
from west_housing_model.valuation import ValuationInputs, run_valuation

GOLDEN_DIR = Path(__file__).resolve().parent / "data" / "golden"


def _load_csv(name: str, **kwargs) -> pd.DataFrame:
    path = GOLDEN_DIR / name
    return pd.read_csv(
        path, true_values=["True", "true"], false_values=["False", "false"], **kwargs
    )


def _load_json(name: str):
    return json.loads((GOLDEN_DIR / name).read_text())


def _compare_records(actual: list[dict], expected: list[dict]) -> None:
    assert len(actual) == len(expected)
    for act, exp in zip(actual, expected, strict=False):
        for key, value in exp.items():
            assert key in act
            actual_value = act[key]
            if isinstance(value, float):
                assert pytest.approx(value, rel=1e-6, abs=1e-6) == float(actual_value)
            elif isinstance(value, dict):
                assert actual_value == value
            elif key == "as_of":
                assert str(actual_value).startswith(value)
            elif isinstance(value, str) and not isinstance(actual_value, str):
                assert str(actual_value) == value
            else:
                assert actual_value == value


def test_pipeline_golden_snapshot() -> None:
    place_base = _load_csv("place_base.csv")
    place_components = _load_csv("place_components.csv")
    site_base = _load_csv("site_base.csv")
    site_hazards = _load_csv("site_hazards.csv")
    site_hazards["as_of"] = pd.to_datetime(site_hazards["as_of"])
    ops_rows = _load_csv("ops.csv", parse_dates=["as_of"])
    scenario_payload = _load_json("scenario.json")

    place_features = build_place_features_from_components(
        place_base, place_components, as_of=pd.Timestamp("2025-01-01")
    )
    site_features = build_site_features_from_components(
        site_base, site_hazards, as_of=pd.Timestamp("2025-02-01")
    )
    ops_row = ops_rows.iloc[0].to_dict()
    ops_features, ops_provenance = build_ops_features(
        property_id=str(ops_row["property_id"]),
        as_of=pd.to_datetime(ops_row["as_of"]),
        eia_state=ops_row.get("eia_state"),
        eia_res_price_cents_per_kwh=float(ops_row.get("eia_res_price_cents_per_kwh", 0)),
        broadband_gbps_flag=bool(ops_row.get("broadband_gbps_flag")),
        zoning_context_note=ops_row.get("zoning_context_note"),
        hud_fmr_2br=ops_row.get("hud_fmr_2br"),
    )

    expected_place = _load_json("expected_place_features.json")
    expected_site = _load_json("expected_site_features.json")
    expected_ops = _load_json("expected_ops_features.json")
    expected_ops_provenance = _load_json("expected_ops_provenance.json")

    _compare_records(place_features.to_dict(orient="records"), expected_place)
    _compare_records(site_features.to_dict(orient="records"), expected_site)
    _compare_records(ops_features.to_dict(orient="records"), expected_ops)

    actual_ops_provenance = json.loads(json.dumps(ops_provenance, default=str))
    assert actual_ops_provenance == expected_ops_provenance

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

    expected_valuation = _load_json("expected_valuation.json")
    _compare_records(valuation.to_dict(orient="records"), expected_valuation)
