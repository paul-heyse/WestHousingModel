from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

import pandas as pd
import pytest

from west_housing_model.core.exceptions import ConnectorError, SchemaError
from west_housing_model.data.connectors import make_census_acs_connector

pytestmark = pytest.mark.skip("HTTP connector work pending; skipping ACS connector tests")


def _load_response(path: Path) -> Iterable[list[str]]:
    payload = json.loads(path.read_text())
    assert isinstance(payload, list)
    return payload


@pytest.fixture
def census_response(tmp_path: Path) -> Path:
    content = [
        ["NAME", "B19013_001E", "state", "county", "tract"],
        ["Test Tract, Denver County, Colorado", "75000", "08", "005", "012602"],
    ]
    artifact = tmp_path / "census-acs-response.json"
    artifact.write_text(json.dumps(content))
    return artifact


def test_census_acs_raises_without_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("CENSUS_API_KEY", raising=False)
    connector = make_census_acs_connector()

    with pytest.raises(ConnectorError):
        connector.fetch(state="08", county="005", table="B19013_001E")


def test_census_acs_parses_payload(monkeypatch: pytest.MonkeyPatch, census_response: Path) -> None:
    called = {}

    def fetch_override(**_: object) -> pd.DataFrame:
        called["invoked"] = True
        rows = _load_response(census_response)
        header, *records = rows
        frame = pd.DataFrame([dict(zip(header, record)) for record in records])
        frame["observed_at"] = pd.Timestamp("2023-12-31")
        frame["source_id"] = "connector.census_acs"
        return frame

    monkeypatch.setenv("CENSUS_API_KEY", "dummy")
    connector = make_census_acs_connector(fetch_override=fetch_override)
    frame = connector.fetch(state="08", county="005", table="B19013_001E")

    assert called.get("invoked")
    assert {"geo_id", "median_household_income", "observed_at", "source_id"}.issubset(frame.columns)
    assert frame.loc[0, "geo_id"] == "08005012602"
    assert frame.loc[0, "median_household_income"] == 75000.0


def test_census_acs_schema_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CENSUS_API_KEY", "dummy")

    def bad_payload(**_: object) -> pd.DataFrame:
        return pd.DataFrame({"unexpected": [1]})

    connector = make_census_acs_connector(fetch_override=bad_payload)

    with pytest.raises(SchemaError):
        connector.fetch(state="08", county="005", table="B19013_001E")
