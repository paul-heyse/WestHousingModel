from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable, Dict

import pandas as pd

from west_housing_model.core.exceptions import ConnectorError, SchemaError
from west_housing_model.data.catalog import failure_capture_path, validate_connector
from west_housing_model.data.connectors.census_acs import (
    CensusAcsConfig,
    fetch_census_acs,
)
from west_housing_model.data.connectors.eia_v2 import EIAConfig, fetch_eia_rates
from west_housing_model.data.connectors.fcc_bdc import FCCBDCConfig, fetch_fcc_broadband
from west_housing_model.data.connectors.hud_fmr import HUDFMRConfig, fetch_hud_fmr
from west_housing_model.data.connectors.pad_us import PadUSConfig, fetch_pad_us
from west_housing_model.data.connectors.storm_events import fetch_storm_events
from west_housing_model.data.connectors.usfs_trails import (
    USFSTrailsConfig,
    fetch_usfs_trails,
)
from west_housing_model.data.connectors.usfs_wildfire import (
    USFSWildfireConfig,
    fetch_usfs_wildfire,
)
from west_housing_model.data.connectors.usgs_designmaps import (
    USGSDesignMapsConfig,
    fetch_usgs_designmaps,
)
from west_housing_model.data.connectors.usgs_epqs import (
    USGSEPQSConfig,
    fetch_usgs_epqs,
)
from west_housing_model.data.connectors.usgs_epqs import (
    USGSEPQSConfig,
    fetch_usgs_epqs,
)
STATE_FIPS_TO_ABBR = {
    '08': 'CO',
    '16': 'ID',
    '49': 'UT',
}


@dataclass
class DataConnector:
    """Connector wrapper that enforces schema validation."""

    source_id: str
    fetch_func: Callable[..., pd.DataFrame]
    ttl_seconds: int = 86_400
    schema_version: str | None = None

    def fetch(self, **query: Any) -> pd.DataFrame:
        try:
            frame = self.fetch_func(**query)
        except SchemaError:
            raise
        except Exception as exc:  # pragma: no cover - defensive guard
            raise ConnectorError(
                f"Connector '{self.source_id}' failed",
                context={"source_id": self.source_id, "error": str(exc)},
            ) from exc

        if not isinstance(frame, pd.DataFrame):
            frame = pd.DataFrame(frame)

        try:
            return validate_connector(self.source_id, frame)
        except SchemaError as exc:
            _capture_schema_failure(self.source_id, frame)
            raise SchemaError(
                exc.message,
                context={"source_id": self.source_id, **(exc.context or {})},
            ) from exc


def _capture_schema_failure(source_id: str, frame: pd.DataFrame) -> None:
    failure_dir = failure_capture_path(source_id)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%f")
    failure_dir.mkdir(parents=True, exist_ok=True)
    frame.to_csv(failure_dir / f"{timestamp}.csv", index=False)


def callable_connector(
    source_id: str, func: Callable[..., pd.DataFrame], ttl_seconds: int = 86_400
) -> DataConnector:
    return DataConnector(source_id=source_id, fetch_func=func, ttl_seconds=ttl_seconds)


DEFAULT_CONNECTORS: Dict[str, DataConnector] = {}


def register_connector(conn: DataConnector) -> None:
    DEFAULT_CONNECTORS[conn.source_id] = conn



def make_census_acs_connector(
    *,
    year: int = 2023,
    geo_level: str = "tract",
    ttl_seconds: int = 400 * 86_400,
    config: CensusAcsConfig | None = None,
    fetch_override: Callable[..., pd.DataFrame] | None = None,
) -> DataConnector:
    source_id = "connector.census_acs"
    cfg = config or CensusAcsConfig()

    def _fetch(state: str, county: str, tract: str | None = None, table: str = cfg.table, **_: Any) -> pd.DataFrame:
        raw = (
            fetch_override(state=state, county=county, tract=tract, table=table)
            if fetch_override is not None
            else fetch_census_acs(
                state=state,
                county=county,
                tract=tract,
                table=table,
                config=CensusAcsConfig(dataset=cfg.dataset, table=table, base_url=cfg.base_url),
            )
        )
        frame = pd.DataFrame(raw).copy(deep=True)
        if frame.empty:
            raise SchemaError(
                "ACS connector produced empty frame",
                context={"source_id": source_id},
            )
        if "geo_id" not in frame.columns:
            required = {"state", "county", "tract"}
            if not required.issubset(frame.columns):
                raise SchemaError(
                    "ACS payload missing identifiers",
                    context={"missing": sorted(required - set(frame.columns))},
                )
            frame["geo_id"] = (
                frame["state"].astype(str)
                + frame["county"].astype(str)
                + frame["tract"].astype(str)
            )
        if "median_household_income" not in frame.columns:
            if table not in frame.columns:
                raise SchemaError(
                    "ACS payload missing income column",
                    context={"table": table},
                )
            frame["median_household_income"] = pd.to_numeric(frame[table], errors="coerce")
        frame["median_household_income"] = frame["median_household_income"].astype(float)
        if "geo_level" not in frame.columns:
            frame["geo_level"] = geo_level
        observed = frame["observed_at"] if "observed_at" in frame.columns else pd.Timestamp(f"{year}-12-31")
        frame["observed_at"] = pd.to_datetime(observed)
        frame["source_id"] = source_id
        return frame

    conn = callable_connector(source_id, _fetch, ttl_seconds=ttl_seconds)
    conn.schema_version = "1"
    register_connector(conn)
    return conn


def make_usfs_wildfire_connector(
    *,
    ttl_seconds: int = 365 * 86_400,
    config: USFSWildfireConfig | None = None,
    fetch_override: Callable[..., pd.DataFrame] | None = None,
) -> DataConnector:
    source_id = "connector.usfs_wildfire"
    cfg = config or USFSWildfireConfig()

    def _fetch(geo_id: str, **extras: Any) -> pd.DataFrame:
        if fetch_override is not None:
            return fetch_override(geo_id=geo_id, **extras)
        return fetch_usfs_wildfire(geo_id=geo_id, config=cfg)

    conn = callable_connector(source_id, _fetch, ttl_seconds=ttl_seconds)
    conn.schema_version = "1"
    register_connector(conn)
    return conn


def make_usgs_designmaps_connector(
    *,
    ttl_seconds: int = 365 * 86_400,
    config: USGSDesignMapsConfig | None = None,
    fetch_override: Callable[..., pd.DataFrame] | None = None,
) -> DataConnector:
    source_id = "connector.usgs_designmaps"
    cfg = config or USGSDesignMapsConfig()

    def _fetch(lat: float, lon: float, **extras: Any) -> pd.DataFrame:
        if fetch_override is not None:
            return fetch_override(lat=lat, lon=lon, **extras)
        return fetch_usgs_designmaps(lat=lat, lon=lon, config=cfg)

    conn = callable_connector(source_id, _fetch, ttl_seconds=ttl_seconds)
    conn.schema_version = "1"
    register_connector(conn)
    return conn


def make_noaa_storm_events_connector(
    *,
    ttl_seconds: int = 180 * 86_400,
    fetch_override: Callable[..., pd.DataFrame] | None = None,
) -> DataConnector:
    source_id = "connector.noaa_storm_events"

    def _fetch(county_id: str, state_abbr: str | None = None, **extras: Any) -> pd.DataFrame:
        if fetch_override is not None:
            return fetch_override(county_id=county_id, state_abbr=state_abbr, **extras)
        fips_state = county_id[:2]
        resolved_state = state_abbr or STATE_FIPS_TO_ABBR.get(fips_state)
        if resolved_state is None:
            raise ConnectorError(
                "Storm events requires state abbreviation",
                context={"county_id": county_id},
            )
        county_fips = county_id[-3:]
        frame = fetch_storm_events(county_fips=county_fips, state_abbr=resolved_state)
        frame["source_id"] = source_id
        return frame

    conn = callable_connector(source_id, _fetch, ttl_seconds=ttl_seconds)
    conn.schema_version = "1"
    register_connector(conn)
    return conn


def make_pad_us_connector(
    *,
    ttl_seconds: int = 365 * 86_400,
    config: PadUSConfig | None = None,
    fetch_override: Callable[..., pd.DataFrame] | None = None,
) -> DataConnector:
    source_id = "connector.pad_us"
    cfg = config or PadUSConfig()

    def _fetch(place_id: str, **extras: Any) -> pd.DataFrame:
        if fetch_override is not None:
            return fetch_override(place_id=place_id, **extras)
        return fetch_pad_us(place_id=place_id, config=cfg)

    conn = callable_connector(source_id, _fetch, ttl_seconds=ttl_seconds)
    conn.schema_version = "1"
    register_connector(conn)
    return conn


def make_fcc_bdc_connector(
    *,
    ttl_seconds: int = 240 * 86_400,
    config: FCCBDCConfig | None = None,
    fetch_override: Callable[..., pd.DataFrame] | None = None,
) -> DataConnector:
    source_id = "connector.fcc_bdc"
    cfg = config or FCCBDCConfig()

    def _fetch(geo_id: str, **extras: Any) -> pd.DataFrame:
        if fetch_override is not None:
            return fetch_override(geo_id=geo_id, **extras)
        return fetch_fcc_broadband(geo_id=geo_id, config=cfg)

    conn = callable_connector(source_id, _fetch, ttl_seconds=ttl_seconds)
    conn.schema_version = "1"
    register_connector(conn)
    return conn


def make_hud_fmr_connector(
    *,
    ttl_seconds: int = 400 * 86_400,
    config: HUDFMRConfig | None = None,
    fetch_override: Callable[..., pd.DataFrame] | None = None,
) -> DataConnector:
    source_id = "connector.hud_fmr"
    cfg = config or HUDFMRConfig()

    def _fetch(geo_id: str, **extras: Any) -> pd.DataFrame:
        if fetch_override is not None:
            return fetch_override(geo_id=geo_id, **extras)
        return fetch_hud_fmr(geo_id=geo_id, config=cfg)

    conn = callable_connector(source_id, _fetch, ttl_seconds=ttl_seconds)
    conn.schema_version = "1"
    register_connector(conn)
    return conn


def make_eia_v2_connector(
    *,
    ttl_seconds: int = 120 * 86_400,
    config: EIAConfig | None = None,
    fetch_override: Callable[..., pd.DataFrame] | None = None,
) -> DataConnector:
    source_id = "connector.eia_v2"
    cfg = config or EIAConfig()

    def _fetch(state: str, **extras: Any) -> pd.DataFrame:
        if fetch_override is not None:
            return fetch_override(state=state, **extras)
        return fetch_eia_rates(state=state, config=cfg)

    conn = callable_connector(source_id, _fetch, ttl_seconds=ttl_seconds)
    conn.schema_version = "1"
    register_connector(conn)
    return conn


def make_usfs_trails_connector(
    *,
    ttl_seconds: int = 365 * 86_400,
    config: USFSTrailsConfig | None = None,
    fetch_override: Callable[..., pd.DataFrame] | None = None,
) -> DataConnector:
    source_id = "connector.usfs_trails"
    cfg = config or USFSTrailsConfig()

    def _fetch(place_id: str, **extras: Any) -> pd.DataFrame:
        if fetch_override is not None:
            return fetch_override(place_id=place_id, **extras)
        return fetch_usfs_trails(place_id=place_id, config=cfg)

    conn = callable_connector(source_id, _fetch, ttl_seconds=ttl_seconds)
    conn.schema_version = "1"
    register_connector(conn)
    return conn


def make_usgs_epqs_connector(
    *,
    ttl_seconds: int = 365 * 86_400,
    config: USGSEPQSConfig | None = None,
    fetch_override: Callable[..., pd.DataFrame] | None = None,
) -> DataConnector:
    source_id = "connector.usgs_epqs"
    cfg = config or USGSEPQSConfig()

    def _fetch(place_id: str, **extras: Any) -> pd.DataFrame:
        if fetch_override is not None:
            return fetch_override(place_id=place_id, **extras)
        return fetch_usgs_epqs(place_id=place_id, config=cfg)

    conn = callable_connector(source_id, _fetch, ttl_seconds=ttl_seconds)
    conn.schema_version = "1"
    register_connector(conn)
    return conn


# Register default connectors on import so tests observe them without extra wiring.
make_census_acs_connector()
make_usfs_wildfire_connector()
make_usgs_designmaps_connector()
make_noaa_storm_events_connector()
make_pad_us_connector()
make_fcc_bdc_connector()
make_hud_fmr_connector()
make_eia_v2_connector()
make_usfs_trails_connector()
make_usgs_epqs_connector()


__all__ = [
    "DataConnector",
    "DEFAULT_CONNECTORS",
    "callable_connector",
    "make_census_acs_connector",
    "make_eia_v2_connector",
    "make_fcc_bdc_connector",
    "make_hud_fmr_connector",
    "make_noaa_storm_events_connector",
    "make_pad_us_connector",
    "make_usfs_trails_connector",
    "make_usfs_wildfire_connector",
    "make_usgs_designmaps_connector",
    "make_usgs_epqs_connector",
    "register_connector",
]
