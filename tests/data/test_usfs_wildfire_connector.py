from __future__ import annotations

import pandas as pd

from west_housing_model.data.catalog import validate_connector


def test_usfs_wildfire_schema_accepts_minimal_payload() -> None:
    df = pd.DataFrame(
        {
            "geo_id": ["08005001202"],
            "wildfire_risk_percentile": [85],
            "observed_at": [pd.Timestamp("2025-01-01")],
            "source_id": ["connector.usfs_wildfire"],
        }
    )
    validated = validate_connector("connector.usfs_wildfire", df)
    pd.testing.assert_frame_equal(validated.reset_index(drop=True), df.reset_index(drop=True))
