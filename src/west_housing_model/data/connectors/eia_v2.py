from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from west_housing_model.core.exceptions import ConnectorError
from west_housing_model.data.connectors.common import HttpFetcher, load_static_records


STATIC_NAME = "eia_v2"
SOURCE_ID = "connector.eia_v2"


@dataclass(slots=True)
class EIAConfig:
    base_url: str | None = None
    static_dataset: str = STATIC_NAME


def _load_static() -> pd.DataFrame:
    frame = pd.DataFrame.from_records(load_static_records(STATIC_NAME))
    frame["res_price_cents_per_kwh"] = frame["res_price_cents_per_kwh"].astype(float)
    return frame


def fetch_eia_rates(
    *,
    state: str,
    config: EIAConfig | None = None,
    http: HttpFetcher | None = None,
) -> pd.DataFrame:
    cfg = config or EIAConfig()
    if http and cfg.base_url:
        payload = http.get_json(cfg.base_url, params={"state": state})
        frame = pd.DataFrame(payload)
    else:
        frame = _load_static()
        frame = frame[frame["state"].str.upper() == state.upper()]

    if frame.empty:
        raise ConnectorError(
            "EIA rate data unavailable",
            context={"state": state},
        )

    normalized = frame.iloc[[0]].copy()
    normalized["state"] = normalized["state"].str.upper()
    normalized["source_id"] = SOURCE_ID
    normalized["observed_at"] = pd.to_datetime(normalized["observed_at"]).dt.normalize()
    return normalized[["state", "res_price_cents_per_kwh", "observed_at", "source_id"]]


__all__ = ["fetch_eia_rates", "EIAConfig"]
