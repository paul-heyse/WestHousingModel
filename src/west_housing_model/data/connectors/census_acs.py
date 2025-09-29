"""HTTP client for the Census ACS API."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any, Iterable

import pandas as pd
import requests

from west_housing_model.core.exceptions import ConnectorError, SchemaError
from west_housing_model.data.catalog import validate_connector


@dataclass
class CensusAcsConfig:
    base_url: str = "https://api.census.gov/data"
    dataset: str = "2022/acs/acs5"
    table: str = "B19013_001E"


def fetch_census_acs(
    *,
    state: str,
    county: str,
    tract: str | None = None,
    table: str = "B19013_001E",
    config: CensusAcsConfig | None = None,
    session: requests.Session | None = None,
) -> pd.DataFrame:
    config = config or CensusAcsConfig(table=table)
    url = f"{config.base_url}/{config.dataset}"
    params: dict[str, Any] = {
        "get": ",".join(["NAME", table, "state", "county", "tract"]),
        "for": f"tract:{tract}" if tract else "tract:*",
        "in": f"state:{state} county:{county}",
    }
    api_key = _get_api_key(optional=False)
    params["key"] = api_key

    http = session or requests.Session()
    response = http.get(url, params=params, timeout=60)
    if response.status_code not in {200, 204}:
        raise ConnectorError(
            "ACS request failed",
            context={"status": response.status_code, "url": response.url, "text": response.text},
        )
    payload = response.json() if response.text else []
    frame = _to_frame(payload, table)
    return validate_connector("connector.census_acs", frame)


def _to_frame(payload: Iterable[Iterable[Any]], table: str) -> pd.DataFrame:
    rows = list(payload)
    if not rows:
        return pd.DataFrame(
            {
                "geo_id": [],
                "geo_level": [],
                "median_household_income": [],
                "observed_at": [],
                "source_id": [],
            }
        )
    header, *rest = rows
    expected = {"NAME", table, "state", "county", "tract"}
    if not expected.issubset(set(header)):
        raise SchemaError(
            "ACS response missing expected columns",
            context={"expected": sorted(expected), "header": header},
        )
    frame = pd.DataFrame([dict(zip(header, values)) for values in rest])
    if frame.empty:
        raise ConnectorError("ACS returned no rows", context={"table": table})
    frame["geo_id"] = frame["state"].astype(str) + frame["county"].astype(str) + frame["tract"].astype(str)
    frame["geo_level"] = "tract"
    frame["median_household_income"] = frame[table].astype(float)
    frame["observed_at"] = pd.to_datetime(date.today().replace(month=12, day=31))
    frame["source_id"] = "connector.census_acs"
    return frame[["geo_id", "geo_level", "median_household_income", "observed_at", "source_id"]]


def _get_api_key(*, optional: bool = False) -> str | None:
    from os import getenv

    key = getenv("CENSUS_API_KEY")
    if not key and not optional:
        raise ConnectorError("CENSUS_API_KEY is required for ACS connector")
    return key


__all__ = ["fetch_census_acs", "CensusAcsConfig"]
