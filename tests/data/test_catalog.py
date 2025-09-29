"""Unit tests for the schema catalog."""

from __future__ import annotations

import pandas as pd
import pytest
from west_housing_model.core.exceptions import SchemaError
from west_housing_model.data.catalog import validate_table


def _valid_place_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "place_id": ["p-001"],
            "geo_level": ["msa"],
            "geo_code": ["12345"],
            "name": ["Example MSA"],
            "as_of": [pd.Timestamp("2024-01-01")],
            "source_id": ["connector.place_context"],
            "pillar_uc": [0.75],
            "pillar_oa": [0.55],
            "pillar_ij": [0.60],
            "pillar_sc": [0.65],
            "aker_market_fit": [82],
        }
    )


def test_validate_table_passes_for_place_features() -> None:
    frame = _valid_place_frame()
    validated = validate_table("place_features", frame)
    pd.testing.assert_frame_equal(validated.reset_index(drop=True), frame.reset_index(drop=True))


def test_validate_table_raises_schema_error_on_missing_column() -> None:
    frame = _valid_place_frame().drop(columns=["geo_code"])
    with pytest.raises(SchemaError) as excinfo:
        validate_table("place_features", frame)

    assert "place_features" in str(excinfo.value)
