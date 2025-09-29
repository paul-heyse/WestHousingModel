from __future__ import annotations

from datetime import datetime

import pandas as pd
from west_housing_model.data.connectors import make_census_acs_connector
from west_housing_model.data.repository import (
    STATUS_FRESH,
    STATUS_REFRESHED,
    Repository,
)


def _fake_payload() -> list[dict[str, object]]:
    # Header-like mapping consistent with _http_fetch output
    return [
        {
            "NAME": "Test Tract",
            "state": "08",
            "county": "005",
            "tract": "001202",
            "B19013_001E": "75000",
        }
    ]


def test_census_acs_fetch_normalizes_and_validates() -> None:
    connector = make_census_acs_connector(year=2023, fetch_override=lambda **_: _fake_payload())
    repo = Repository(connectors={connector.source_id: connector})
    result = repo.get(connector.source_id, state="08", county="005")

    assert result.source_id == connector.source_id
    assert not result.is_stale
    df = pd.DataFrame(result.frame)
    assert result.status == STATUS_REFRESHED
    assert {"geo_id", "geo_level", "observed_at", "median_household_income", "source_id"}.issubset(
        df.columns
    )
    assert df.loc[0, "median_household_income"] == 75000.0
    assert df.loc[0, "geo_level"] == "tract"
    # observed_at coerces to end-of-year timestamp
    assert isinstance(df.loc[0, "observed_at"], (datetime,))


def test_census_acs_repository_cache_hit() -> None:
    connector = make_census_acs_connector(
        geo_level="tract", year=2023, fetch_override=lambda **_: _fake_payload(), ttl_seconds=3600
    )
    repo = Repository(connectors={connector.source_id: connector})

    first = repo.get(connector.source_id, state="08", county="005")
    second = repo.get(connector.source_id, state="08", county="005")

    assert first.status == STATUS_REFRESHED
    # within TTL, second call should be served from cache and not marked stale
    assert second.status == STATUS_FRESH
    pd.testing.assert_frame_equal(pd.DataFrame(first.frame), pd.DataFrame(second.frame))


def test_census_acs_registry_defaults_used() -> None:
    connector = make_census_acs_connector(fetch_override=lambda **_: _fake_payload())

    # Registry specifies tract geography and 400-day TTL
    assert connector.ttl_seconds == 400 * 86_400

    repo = Repository(connectors={connector.source_id: connector})
    result = repo.get(connector.source_id, state="08", county="005")
    df = pd.DataFrame(result.frame)
    assert df.loc[0, "geo_level"] == "tract"
