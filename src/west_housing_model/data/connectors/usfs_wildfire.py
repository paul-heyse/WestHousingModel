from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from west_housing_model.core.exceptions import ConnectorError
from west_housing_model.data.connectors.common import HttpFetcher, load_static_records


STATIC_NAME = "usfs_wildfire"
SOURCE_ID = "connector.usfs_wildfire"


@dataclass(slots=True)
class USFSWildfireConfig:
    base_url: str | None = None
    static_dataset: str = STATIC_NAME


def _load_static() -> pd.DataFrame:
    records = load_static_records(STATIC_NAME)
    return pd.DataFrame.from_records(records)


def fetch_usfs_wildfire(
    *,
    geo_id: str,
    config: USFSWildfireConfig | None = None,
    http: HttpFetcher | None = None,
) -> pd.DataFrame:
    cfg = config or USFSWildfireConfig()
    if http and cfg.base_url:
        # Placeholder for future live integration
        payload = http.get_json(cfg.base_url, params={"geoid": geo_id})
        frame = pd.DataFrame(payload)
    else:
        frame = _load_static()
        subset = frame[frame["geo_id"] == geo_id]
        if subset.empty and len(geo_id) > 5:
            prefix = geo_id[:5]
            subset = frame[frame["geo_id"].str.startswith(prefix)]
        frame = subset

    if frame.empty:
        raise ConnectorError(
            "Wildfire risk data unavailable",
            context={"geo_id": geo_id},
        )

    normalized = frame.iloc[[0]].copy()
    normalized["geo_id"] = normalized["geo_id"].iloc[0]
    normalized["source_id"] = SOURCE_ID
    normalized["observed_at"] = pd.to_datetime(normalized["observed_at"]).dt.normalize()
    return normalized[["geo_id", "wildfire_risk_percentile", "observed_at", "source_id"]]


__all__ = ["fetch_usfs_wildfire", "USFSWildfireConfig"]
