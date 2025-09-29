from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable, Dict

import pandas as pd
import pytest

from west_housing_model.core.exceptions import SchemaError
from west_housing_model.data.connectors import (
    make_census_acs_connector,
    make_eia_v2_connector,
    make_fcc_bdc_connector,
    make_hud_fmr_connector,
    make_noaa_storm_events_connector,
    make_pad_us_connector,
    make_usfs_trails_connector,
    make_usfs_wildfire_connector,
    make_usgs_designmaps_connector,
    make_usgs_epqs_connector,
)

FIXTURE_ROOT = Path(__file__).parent / "data" / "connectors"


def _load_frame(connector: str, case: str) -> pd.DataFrame:
    path = FIXTURE_ROOT / connector / f"{case}.json"
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    return pd.DataFrame(payload)


ConnectorFactory = Callable[..., Any]


CONNECTOR_CASES: list[tuple[str, ConnectorFactory, Dict[str, Any]]] = [
    ("census_acs", make_census_acs_connector, {"state": "08", "county": "005", "tract": "012602"}),
    ("usfs_wildfire", make_usfs_wildfire_connector, {"geo_id": "08005012602"}),
    ("usgs_designmaps", make_usgs_designmaps_connector, {"lat": 39.7392, "lon": -104.9903}),
    ("noaa_storm_events", make_noaa_storm_events_connector, {"county_id": "08005", "state_abbr": "CO"}),
    ("pad_us", make_pad_us_connector, {"place_id": "denver"}),
    ("fcc_bdc", make_fcc_bdc_connector, {"geo_id": "08005012602"}),
    ("hud_fmr", make_hud_fmr_connector, {"geo_id": "08005012602"}),
    ("eia_v2", make_eia_v2_connector, {"state": "CO"}),
    ("usfs_trails", make_usfs_trails_connector, {"place_id": "denver"}),
    ("usgs_epqs", make_usgs_epqs_connector, {"place_id": "denver"}),
]


@pytest.mark.parametrize("connector_key,factory,args", CONNECTOR_CASES)
def test_connector_success(connector_key: str, factory: ConnectorFactory, args: Dict[str, Any]) -> None:
    success_frame = _load_frame(connector_key, "success")
    connector = factory(fetch_override=lambda **_: success_frame)
    result = connector.fetch(**args)
    assert not result.empty, connector_key


@pytest.mark.parametrize("connector_key,factory,args", CONNECTOR_CASES)
def test_connector_schema_failure(connector_key: str, factory: ConnectorFactory, args: Dict[str, Any]) -> None:
    failure_frame = _load_frame(connector_key, "failure")
    connector = factory(fetch_override=lambda **_: failure_frame)
    with pytest.raises(SchemaError):
        connector.fetch(**args)
