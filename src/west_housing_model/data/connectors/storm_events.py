from __future__ import annotations

import logging
from datetime import date
from typing import Any, Dict

import pandas as pd
import requests

from west_housing_model.core.exceptions import ConnectorError, SchemaError
from west_housing_model.data.catalog import validate_connector


_LOGGER = logging.getLogger(__name__)


def fetch_storm_events(
    *,
    county_fips: str,
    state_abbr: str,
    start_year: int | None = None,
    end_year: int | None = None,
    session: requests.Session | None = None,
) -> pd.DataFrame:
    start_year = start_year or date.today().year - 9
    end_year = end_year or date.today().year
    params: Dict[str, Any] = {
        "datasetcode": "STORM_DETAILS",
        "statefips": state_abbr,
        "countyfips": county_fips,
        "startyear": start_year,
        "endyear": end_year,
        "results": "json",
    }
    http = session or requests.Session()
    response = http.get(
        "https://www.ncdc.noaa.gov/swdiws/json/stormevents", params=params, timeout=120
    )
    _check_response(response)
    payload = response.json()
    events = _extract_events(payload)
    frame = pd.DataFrame(events)
    if frame.empty:
        frame = pd.DataFrame(
            {
                "county_id": [f"{state_abbr}{county_fips}"],
                "winter_storms_10yr_county": [0],
                "observed_at": [pd.Timestamp(f"{end_year}-12-31")],
                "source_id": ["connector.noaa_storm_events"],
            }
        )
    return validate_connector("connector.noaa_storm_events", frame)


def _check_response(response: requests.Response) -> None:
    if response.status_code == 200:
        return
    try:
        payload = response.json()
    except ValueError:
        payload = {"text": response.text}
    raise ConnectorError(
        "Storm events request failed",
        context={"status": response.status_code, "payload": payload, "url": response.url},
    )


def _extract_events(payload: dict[str, Any]) -> list[dict[str, Any]]:
    data = payload.get("swdiJsonResponse", {}).get("result", {}).get("event", [])
    events = []
    for entry in data:
        if entry.get("eventType") == "Winter Storm":
            county_id = f"{entry.get('stateFips','')}{entry.get('czFips','')}"
            events.append(
                {
                    "county_id": county_id,
                    "winter_storms_10yr_county": entry.get("eventId"),
                    "observed_at": pd.to_datetime(entry.get("endDate", "")),
                    "source_id": "connector.noaa_storm_events",
                }
            )
    return events


__all__ = ["fetch_storm_events"]
