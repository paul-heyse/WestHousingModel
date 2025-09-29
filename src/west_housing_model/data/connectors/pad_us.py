from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from west_housing_model.core.exceptions import ConnectorError
from west_housing_model.data.connectors.common import HttpFetcher, load_static_records


STATIC_NAME = "pad_us"
SOURCE_ID = "connector.pad_us"


@dataclass(slots=True)
class PadUSConfig:
    base_url: str | None = None
    static_dataset: str = STATIC_NAME


def _load_static() -> pd.DataFrame:
    return pd.DataFrame.from_records(load_static_records(STATIC_NAME))


def fetch_pad_us(
    *,
    place_id: str,
    config: PadUSConfig | None = None,
    http: HttpFetcher | None = None,
) -> pd.DataFrame:
    cfg = config or PadUSConfig()
    if http and cfg.base_url:
        payload = http.get_json(cfg.base_url, params={"place_id": place_id})
        frame = pd.DataFrame(payload)
    else:
        frame = _load_static()
        frame = frame[frame["place_id"] == place_id]

    if frame.empty:
        raise ConnectorError(
            "PAD-US acres unavailable",
            context={"place_id": place_id},
        )

    normalized = frame.iloc[[0]].copy()
    normalized["source_id"] = SOURCE_ID
    normalized["observed_at"] = pd.to_datetime(normalized["observed_at"]).dt.normalize()
    return normalized[["place_id", "public_land_acres_30min", "observed_at", "source_id"]]


__all__ = ["fetch_pad_us", "PadUSConfig"]
