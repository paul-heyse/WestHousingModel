from __future__ import annotations

import pandas as pd

from west_housing_model.data.catalog import validate_connector


def test_noaa_storm_events_schema_accepts() -> None:
    df = pd.DataFrame(
        {
            "county_id": ["08005"],
            "winter_storms_10yr_county": [3],
            "observed_at": [pd.Timestamp("2024-12-31")],
            "source_id": ["connector.noaa_storm_events"],
        }
    )
    validated = validate_connector("connector.noaa_storm_events", df)
    pd.testing.assert_frame_equal(validated.reset_index(drop=True), df.reset_index(drop=True))


def test_pad_us_schema_accepts() -> None:
    df = pd.DataFrame(
        {
            "place_id": ["pl-001"],
            "public_land_acres_30min": [1500.0],
            "observed_at": [pd.Timestamp("2025-01-01")],
            "source_id": ["connector.pad_us"],
        }
    )
    validated = validate_connector("connector.pad_us", df)
    pd.testing.assert_frame_equal(validated.reset_index(drop=True), df.reset_index(drop=True))


def test_fcc_bdc_schema_accepts_boolean() -> None:
    df = pd.DataFrame(
        {
            "geo_id": ["08005001202"],
            "broadband_gbps_flag": [True],
            "observed_at": [pd.Timestamp("2025-02-01")],
            "source_id": ["connector.fcc_bdc"],
        }
    )
    validated = validate_connector("connector.fcc_bdc", df)
    pd.testing.assert_frame_equal(validated.reset_index(drop=True), df.reset_index(drop=True))


def test_hud_fmr_schema_accepts() -> None:
    df = pd.DataFrame(
        {
            "geo_id": ["08005001202"],
            "hud_fmr_2br": [1850.0],
            "observed_at": [pd.Timestamp("2025-01-01")],
            "source_id": ["connector.hud_fmr"],
        }
    )
    validated = validate_connector("connector.hud_fmr", df)
    pd.testing.assert_frame_equal(validated.reset_index(drop=True), df.reset_index(drop=True))


def test_eia_v2_schema_accepts() -> None:
    df = pd.DataFrame(
        {
            "state": ["CO"],
            "res_price_cents_per_kwh": [12.8],
            "observed_at": [pd.Timestamp("2025-03-01")],
            "source_id": ["connector.eia_v2"],
        }
    )
    validated = validate_connector("connector.eia_v2", df)
    pd.testing.assert_frame_equal(validated.reset_index(drop=True), df.reset_index(drop=True))


def test_usfs_trails_schema_accepts() -> None:
    df = pd.DataFrame(
        {
            "place_id": ["pl-001"],
            "minutes_to_trailhead": [20.0],
            "observed_at": [pd.Timestamp("2025-04-01")],
            "source_id": ["connector.usfs_trails"],
        }
    )
    validated = validate_connector("connector.usfs_trails", df)
    pd.testing.assert_frame_equal(validated.reset_index(drop=True), df.reset_index(drop=True))


def test_usgs_epqs_schema_accepts() -> None:
    df = pd.DataFrame(
        {
            "place_id": ["pl-001"],
            "slope_gt15_pct_within_10km": [24.0],
            "observed_at": [pd.Timestamp("2025-05-01")],
            "source_id": ["connector.usgs_epqs"],
        }
    )
    validated = validate_connector("connector.usgs_epqs", df)
    pd.testing.assert_frame_equal(validated.reset_index(drop=True), df.reset_index(drop=True))
