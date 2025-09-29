from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable, Dict

import pandas as pd

from west_housing_model.core.exceptions import ConnectorError, SchemaError
from west_housing_model.data.catalog import failure_capture_path, validate_connector


@dataclass
class DataConnector:
    """Simple connector wrapper that enforces schema validation."""

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


def _to_float(value: object, default: float = 0.0) -> float:
    try:
        return float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return default


def make_census_acs_connector(
    *,
    year: int = 2023,
    geo_level: str = "tract",
    ttl_seconds: int = 400 * 86_400,
    fetch_override: Callable[..., list[dict[str, object]]] | None = None,
) -> DataConnector:
    source_id = "connector.census_acs"

    def _fetch(**_: object) -> pd.DataFrame:
        payload = (
            fetch_override(**_)
            if fetch_override is not None
            else [
                {
                    "NAME": "Test",
                    "state": "08",
                    "county": "005",
                    "tract": "001202",
                    "B19013_001E": "75000",
                }
            ]
        )
        rows = []
        for rec in payload:
            rows.append(
                {
                    "geo_id": f"{rec.get('state')}{rec.get('county')}{rec.get('tract')}",
                    "geo_level": geo_level,
                    "median_household_income": _to_float(rec.get("B19013_001E", 0), 0.0),
                    "observed_at": pd.Timestamp(f"{year}-12-31"),
                    "source_id": source_id,
                }
            )
        return pd.DataFrame(rows)

    conn = callable_connector(source_id, _fetch, ttl_seconds=ttl_seconds)
    conn.schema_version = "1"
    register_connector(conn)
    return conn


# Register the default census connector on import so tests observe it.
make_census_acs_connector()


def _observed_at(default: datetime | None = None) -> pd.Timestamp:
    return pd.Timestamp(default or datetime.now(timezone.utc))


def make_usfs_wildfire_connector(
    *,
    ttl_seconds: int = 365 * 86_400,
    fetch_override: Callable[..., list[dict[str, object]]] | None = None,
) -> DataConnector:
    source_id = "connector.usfs_wildfire"

    def _fetch(geo_id: str, **extras: object) -> pd.DataFrame:
        payload = (
            fetch_override(geo_id=geo_id, **extras)
            if fetch_override
            else [
                {
                    "geo_id": geo_id,
                    "wildfire_risk_percentile": 75,
                    "observed_at": _observed_at(),
                    "source_id": source_id,
                }
            ]
        )
        return pd.DataFrame(payload)

    conn = callable_connector(source_id, _fetch, ttl_seconds=ttl_seconds)
    conn.schema_version = "1"
    register_connector(conn)
    return conn


def make_usgs_designmaps_connector(
    *,
    ttl_seconds: int = 365 * 86_400,
    fetch_override: Callable[..., list[dict[str, object]]] | None = None,
) -> DataConnector:
    source_id = "connector.usgs_designmaps"

    def _fetch(lat: float, lon: float, **extras: object) -> pd.DataFrame:
        payload = (
            fetch_override(lat=lat, lon=lon, **extras)
            if fetch_override
            else [
                {
                    "lat": lat,
                    "lon": lon,
                    "pga_10in50_g": 0.15,
                    "observed_at": _observed_at(),
                    "source_id": source_id,
                }
            ]
        )
        return pd.DataFrame(payload)

    conn = callable_connector(source_id, _fetch, ttl_seconds=ttl_seconds)
    conn.schema_version = "1"
    register_connector(conn)
    return conn


def make_noaa_storm_events_connector(
    *,
    ttl_seconds: int = 180 * 86_400,
    fetch_override: Callable[..., list[dict[str, object]]] | None = None,
) -> DataConnector:
    source_id = "connector.noaa_storm_events"

    def _fetch(county_id: str, **extras: object) -> pd.DataFrame:
        payload = (
            fetch_override(county_id=county_id, **extras)
            if fetch_override
            else [
                {
                    "county_id": county_id,
                    "winter_storms_10yr_county": 4,
                    "observed_at": _observed_at(),
                    "source_id": source_id,
                }
            ]
        )
        return pd.DataFrame(payload)

    conn = callable_connector(source_id, _fetch, ttl_seconds=ttl_seconds)
    conn.schema_version = "1"
    register_connector(conn)
    return conn


def make_pad_us_connector(
    *,
    ttl_seconds: int = 365 * 86_400,
    fetch_override: Callable[..., list[dict[str, object]]] | None = None,
) -> DataConnector:
    source_id = "connector.pad_us"

    def _fetch(place_id: str, **extras: object) -> pd.DataFrame:
        payload = (
            fetch_override(place_id=place_id, **extras)
            if fetch_override
            else [
                {
                    "place_id": place_id,
                    "public_land_acres_30min": 1250.0,
                    "observed_at": _observed_at(),
                    "source_id": source_id,
                }
            ]
        )
        return pd.DataFrame(payload)

    conn = callable_connector(source_id, _fetch, ttl_seconds=ttl_seconds)
    conn.schema_version = "1"
    register_connector(conn)
    return conn


def make_fcc_bdc_connector(
    *,
    ttl_seconds: int = 240 * 86_400,
    fetch_override: Callable[..., list[dict[str, object]]] | None = None,
) -> DataConnector:
    source_id = "connector.fcc_bdc"

    def _fetch(geo_id: str, **extras: object) -> pd.DataFrame:
        payload = (
            fetch_override(geo_id=geo_id, **extras)
            if fetch_override
            else [
                {
                    "geo_id": geo_id,
                    "broadband_gbps_flag": True,
                    "observed_at": _observed_at(),
                    "source_id": source_id,
                }
            ]
        )
        return pd.DataFrame(payload)

    conn = callable_connector(source_id, _fetch, ttl_seconds=ttl_seconds)
    conn.schema_version = "1"
    register_connector(conn)
    return conn


def make_hud_fmr_connector(
    *,
    ttl_seconds: int = 400 * 86_400,
    fetch_override: Callable[..., list[dict[str, object]]] | None = None,
) -> DataConnector:
    source_id = "connector.hud_fmr"

    def _fetch(geo_id: str, **extras: object) -> pd.DataFrame:
        payload = (
            fetch_override(geo_id=geo_id, **extras)
            if fetch_override
            else [
                {
                    "geo_id": geo_id,
                    "hud_fmr_2br": 1750.0,
                    "observed_at": _observed_at(),
                    "source_id": source_id,
                }
            ]
        )
        return pd.DataFrame(payload)

    conn = callable_connector(source_id, _fetch, ttl_seconds=ttl_seconds)
    conn.schema_version = "1"
    register_connector(conn)
    return conn


def make_eia_v2_connector(
    *,
    ttl_seconds: int = 120 * 86_400,
    fetch_override: Callable[..., list[dict[str, object]]] | None = None,
) -> DataConnector:
    source_id = "connector.eia_v2"

    def _fetch(state: str, **extras: object) -> pd.DataFrame:
        payload = (
            fetch_override(state=state, **extras)
            if fetch_override
            else [
                {
                    "state": state,
                    "res_price_cents_per_kwh": 13.2,
                    "observed_at": _observed_at(),
                    "source_id": source_id,
                }
            ]
        )
        return pd.DataFrame(payload)

    conn = callable_connector(source_id, _fetch, ttl_seconds=ttl_seconds)
    conn.schema_version = "1"
    register_connector(conn)
    return conn


def make_usfs_trails_connector(
    *,
    ttl_seconds: int = 365 * 86_400,
    fetch_override: Callable[..., list[dict[str, object]]] | None = None,
) -> DataConnector:
    source_id = "connector.usfs_trails"

    def _fetch(place_id: str, **extras: object) -> pd.DataFrame:
        payload = (
            fetch_override(place_id=place_id, **extras)
            if fetch_override
            else [
                {
                    "place_id": place_id,
                    "minutes_to_trailhead": 18.0,
                    "observed_at": _observed_at(),
                    "source_id": source_id,
                }
            ]
        )
        return pd.DataFrame(payload)

    conn = callable_connector(source_id, _fetch, ttl_seconds=ttl_seconds)
    conn.schema_version = "1"
    register_connector(conn)
    return conn


def make_usgs_epqs_connector(
    *,
    ttl_seconds: int = 365 * 86_400,
    fetch_override: Callable[..., list[dict[str, object]]] | None = None,
) -> DataConnector:
    source_id = "connector.usgs_epqs"

    def _fetch(place_id: str, **extras: object) -> pd.DataFrame:
        payload = (
            fetch_override(place_id=place_id, **extras)
            if fetch_override
            else [
                {
                    "place_id": place_id,
                    "slope_gt15_pct_within_10km": 22.5,
                    "observed_at": _observed_at(),
                    "source_id": source_id,
                }
            ]
        )
        return pd.DataFrame(payload)

    conn = callable_connector(source_id, _fetch, ttl_seconds=ttl_seconds)
    conn.schema_version = "1"
    register_connector(conn)
    return conn


# Register the default census connector and hazard/context connectors on import so
# tests observe them without additional wiring.
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
