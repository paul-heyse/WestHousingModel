from __future__ import annotations

import pandas as pd
import pytest

from west_housing_model.core.exceptions import SchemaError
from west_housing_model.data.catalog import validate_connector


def test_usgs_designmaps_schema_accepts_minimal_payload() -> None:
    df = pd.DataFrame(
        {
            "lat": [43.618],
            "lon": [-116.214],
            "pga_10in50_g": [0.15],
            "observed_at": [pd.Timestamp("2025-01-01")],
            "source_id": ["connector.usgs_designmaps"],
        }
    )
    validated = validate_connector("connector.usgs_designmaps", df)
    pd.testing.assert_frame_equal(validated.reset_index(drop=True), df.reset_index(drop=True))


def test_usgs_designmaps_schema_rejects_missing_columns() -> None:
    df = pd.DataFrame({"lat": [43.618]})
    with pytest.raises(SchemaError):
        validate_connector("connector.usgs_designmaps", df)
