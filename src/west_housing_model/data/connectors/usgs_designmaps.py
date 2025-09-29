from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Mapping

import pandas as pd

from west_housing_model.core.exceptions import ConnectorError
from west_housing_model.data.connectors.common import HttpFetcher


_LOGGER = logging.getLogger(__name__)


DEFAULT_ENDPOINT = "https://earthquake.usgs.gov/ws/designmaps"
DEFAULT_REFERENCE = "asce7-16.json"
DEFAULT_RISK_CATEGORY = "II"
DEFAULT_SITE_CLASS = "D"


@dataclass(slots=True)
class USGSDesignMapsConfig:
    base_url: str = DEFAULT_ENDPOINT
    reference: str = DEFAULT_REFERENCE
    risk_category: str = DEFAULT_RISK_CATEGORY
    site_class: str = DEFAULT_SITE_CLASS


def _to_timestamp(value: str | None) -> pd.Timestamp:
    if not value:
        return pd.Timestamp(datetime.utcnow()).tz_localize("UTC")
    ts = pd.to_datetime(value, utc=True, errors="coerce")
    if ts is pd.NaT:
        return pd.Timestamp(datetime.utcnow()).tz_localize("UTC")
    return ts


def fetch_usgs_designmaps(
    *,
    lat: float,
    lon: float,
    title: str = "site",
    risk_category: str | None = None,
    site_class: str | None = None,
    config: USGSDesignMapsConfig | None = None,
    http: HttpFetcher | None = None,
) -> pd.DataFrame:
    cfg = config or USGSDesignMapsConfig()
    fetcher = http or HttpFetcher(cfg.base_url)
    request_params: Mapping[str, Any] = {
        "latitude": lat,
        "longitude": lon,
        "riskCategory": risk_category or cfg.risk_category,
        "siteClass": site_class or cfg.site_class,
        "title": title,
    }

    payload = fetcher.get_json(cfg.reference, params=request_params)
    try:
        response = payload["response"]
        data = response["data"]
        pga = float(data["pga"])
        observed = _to_timestamp(payload["request"].get("date"))
    except (KeyError, TypeError, ValueError) as exc:
        _LOGGER.exception("Invalid DesignMaps payload", extra={"payload": payload})
        raise ConnectorError(
            "USGS DesignMaps payload missing expected fields",
            context={"payload": payload},
        ) from exc

    frame = pd.DataFrame(
        {
            "lat": [lat],
            "lon": [lon],
            "pga_10in50_g": [pga],
            "observed_at": [observed.tz_convert(None)],
            "source_id": ["connector.usgs_designmaps"],
        }
    )
    return frame


__all__ = ["fetch_usgs_designmaps", "USGSDesignMapsConfig"]
