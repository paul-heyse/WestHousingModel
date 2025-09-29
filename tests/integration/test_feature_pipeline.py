from __future__ import annotations

from pathlib import Path
import json

import pandas as pd

from west_housing_model.features.ops_features import build_ops_features
from west_housing_model.features.place_features import build_place_features_from_components
from west_housing_model.features.site_features import build_site_features_from_components

GOLDEN_DIR = Path(__file__).resolve().parents[1] / "data" / "golden"


def _load_csv(name: str, **kwargs) -> pd.DataFrame:
    return pd.read_csv(GOLDEN_DIR / name, **kwargs)


def test_feature_pipeline_matches_golden_snapshots() -> None:
    place_base = _load_csv("place_base.csv")
    place_components = _load_csv("place_components.csv")
    site_base = _load_csv("site_base.csv")
    site_hazards = _load_csv("site_hazards.csv", parse_dates=["as_of"])
    ops_rows = _load_csv("ops.csv", parse_dates=["as_of"])

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

    expected_place = pd.read_json(GOLDEN_DIR / "expected_place_features.json")
    expected_site = pd.read_json(GOLDEN_DIR / "expected_site_features.json")
    expected_ops = pd.read_json(GOLDEN_DIR / "expected_ops_features.json")
    expected_ops_provenance = json.loads((GOLDEN_DIR / "expected_ops_provenance.json").read_text())

    def _normalized(df: pd.DataFrame) -> pd.DataFrame:
        out = df.copy()
        if "as_of" in out.columns:
            out["as_of"] = out["as_of"].astype(str)
        if "geo_code" in out.columns:
            out["geo_code"] = out["geo_code"].astype(str)
        return out.reindex(sorted(out.columns), axis=1).reset_index(drop=True)

    pd.testing.assert_frame_equal(
        _normalized(place_features), _normalized(expected_place), check_dtype=False
    )
    pd.testing.assert_frame_equal(
        _normalized(site_features), _normalized(expected_site), check_dtype=False
    )
    pd.testing.assert_frame_equal(
        _normalized(ops_features), _normalized(expected_ops), check_dtype=False
    )

    actual_ops_provenance = json.loads(json.dumps(ops_provenance, default=str))
    assert actual_ops_provenance == expected_ops_provenance
