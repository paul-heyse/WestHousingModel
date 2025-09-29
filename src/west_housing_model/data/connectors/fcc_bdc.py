from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from west_housing_model.core.exceptions import ConnectorError
from west_housing_model.data.connectors.common import HttpFetcher, load_static_records


STATIC_NAME = "fcc_bdc"
SOURCE_ID = "connector.fcc_bdc"


@dataclass(slots=True)
class FCCBDCConfig:
    base_url: str | None = None
    static_dataset: str = STATIC_NAME


def _load_static() -> pd.DataFrame:
    frame = pd.DataFrame.from_records(load_static_records(STATIC_NAME))
    frame["broadband_gbps_flag"] = frame["broadband_gbps_flag"].astype(bool)
    return frame


def fetch_fcc_broadband(
    *,
    geo_id: str,
    config: FCCBDCConfig | None = None,
    http: HttpFetcher | None = None,
) -> pd.DataFrame:
    cfg = config or FCCBDCConfig()
    if http and cfg.base_url:
        payload = http.get_json(cfg.base_url, params={"geo_id": geo_id})
        frame = pd.DataFrame(payload)
    else:
        frame = _load_static()
        frame = frame[frame["geo_id"] == geo_id]

    if frame.empty:
        raise ConnectorError(
            "FCC broadband data unavailable",
            context={"geo_id": geo_id},
        )

    normalized = frame.iloc[[0]].copy()
    normalized["source_id"] = SOURCE_ID
    normalized["observed_at"] = pd.to_datetime(normalized["observed_at"]).dt.normalize()
    return normalized[["geo_id", "broadband_gbps_flag", "observed_at", "source_id"]]


__all__ = ["fetch_fcc_broadband", "FCCBDCConfig"]
