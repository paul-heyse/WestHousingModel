from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from west_housing_model.valuation import ValuationInputs, run_valuation

GOLDEN_DIR = Path(__file__).resolve().parents[1] / "data" / "golden"


def test_valuation_matches_golden_snapshot() -> None:
    scenario_payload = json.loads((GOLDEN_DIR / "scenario.json").read_text())
    valuation_inputs = ValuationInputs(
        scenario_id=scenario_payload["scenario_id"],
        property_id=scenario_payload["property_id"],
        as_of=pd.to_datetime(scenario_payload.get("as_of")),
        place_features=scenario_payload["place_features"],
        site_features=scenario_payload["site_features"],
        ops_features=scenario_payload["ops_features"],
        user_overrides=scenario_payload["user_overrides"],
    )

    valuation = run_valuation(valuation_inputs).reset_index(drop=True)
    expected = pd.read_json(GOLDEN_DIR / "expected_valuation.json").reset_index(drop=True)
    valuation["as_of"] = valuation["as_of"].astype(str)
    expected["as_of"] = expected["as_of"].astype(str)
    pd.testing.assert_frame_equal(valuation, expected, check_dtype=False)
