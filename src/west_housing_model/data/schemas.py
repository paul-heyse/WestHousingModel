"""Centralised Pandera schemas for connector and table datasets."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Literal, Mapping, MutableMapping, Optional

import pandas as pd
import pandera as pa
from pandera import Column, DataFrameSchema
from pandera.dtypes import Bool, DateTime, Float64, Int64, String
from pandera.errors import SchemaError as PanderaSchemaError

from west_housing_model.core.exceptions import SchemaError
from west_housing_model.utils.logging import LogContext, info

SchemaKind = Literal["table", "connector"]


def _string(*, nullable: bool = False, required: bool = True) -> Column:
    return Column(String, nullable=nullable, required=required, coerce=True)


def _float(*, nullable: bool = True, required: bool = True) -> Column:
    return Column(Float64, nullable=nullable, required=required, coerce=True)


def _int(*, nullable: bool = True, required: bool = True) -> Column:
    return Column(Int64, nullable=nullable, required=required, coerce=True)


def _bool(*, nullable: bool = True, required: bool = True) -> Column:
    return Column(Bool, nullable=nullable, required=required, coerce=True)


def _datetime(*, nullable: bool = True, required: bool = True) -> Column:
    return Column(DateTime, nullable=nullable, required=required, coerce=True)


def _object(*, nullable: bool = True, required: bool = True) -> Column:
    return Column(object, nullable=nullable, required=required, coerce=False)


TABLE_SCHEMAS: Mapping[str, DataFrameSchema] = {
    "place_features": DataFrameSchema(
        {
            "place_id": _string(),
            "geo_level": _string(),
            "geo_code": _string(),
            "name": _string(),
            "as_of": _datetime(),
            "source_id": _string(),
            "pillar_uc": _float(),
            "pillar_oa": _float(),
            "pillar_ij": _float(),
            "pillar_sc": _float(),
            "aker_market_fit": _int(),
            "public_land_acres_30min": _float(required=False),
            "broadband_gbps_flag": _bool(required=False),
        },
        coerce=True,
        strict=False,
        name="place_features",
    ),
    "ops_features": DataFrameSchema(
        {
            "property_id": _string(),
            "as_of": _datetime(),
            "source_id": _string(),
            "utility_rate_note": _string(),
            "broadband_gbps_flag": _bool(),
            "zoning_context_note": _string(nullable=True),
            "utilities_scaler": _float(),
            "hud_fmr_2br": _float(),
        },
        coerce=True,
        strict=False,
        name="ops_features",
    ),
    "site_features": DataFrameSchema(
        {
            "property_id": _string(),
            "place_id": _string(),
            "latitude": _float(required=False),
            "longitude": _float(required=False),
            "as_of": _datetime(),
            "source_id": _string(),
            "in_sfha": _bool(),
            "wildfire_risk_percentile": _float(),
            "pga_10in50_g": _float(),
            "winter_storms_10yr_county": _float(),
            "minutes_to_trailhead": _float(),
            "broadband_gbps_flag": _bool(),
            "hdd_annual": _float(required=False),
            "cdd_annual": _float(required=False),
            "rail_within_300m_flag": _bool(required=False),
        },
        coerce=True,
        strict=False,
        name="site_features",
    ),
    "valuation_outputs": DataFrameSchema(
        {
            "scenario_id": _string(),
            "property_id": _string(),
            "as_of": _datetime(),
            "noistab": _float(nullable=False),
            "cap_rate_low": _float(nullable=False),
            "cap_rate_base": _float(nullable=False),
            "cap_rate_high": _float(nullable=False),
            "value_low": _float(nullable=False),
            "value_base": _float(nullable=False),
            "value_high": _float(nullable=False),
            "yoc_base": _float(nullable=False),
            "irr_5yr_low": _float(nullable=False),
            "irr_5yr_base": _float(nullable=False),
            "irr_5yr_high": _float(nullable=False),
            "dscr_proxy": _float(nullable=False),
            "insurance_uplift": _float(nullable=False),
            "utilities_scaler": _float(nullable=False),
            "aker_fit": _int(nullable=False),
            "deal_quality": _int(nullable=False),
            "sensitivity_matrix": _object(nullable=False),
            "source_manifest": _object(nullable=False),
        },
        coerce=True,
        strict=False,
        name="valuation_outputs",
    ),
}


CONNECTOR_SCHEMAS: Mapping[str, DataFrameSchema] = {
    "connector.place_context": DataFrameSchema(
        {
            "place_id": _string(),
            "metric": _string(),
            "value": _float(),
            "observed_at": _datetime(),
            "source_id": _string(),
        },
        coerce=True,
        strict=False,
        name="connector.place_context",
    ),
    "connector.usfs_wildfire": DataFrameSchema(
        {
            "geo_id": _string(),
            "wildfire_risk_percentile": _float(),
            "observed_at": _datetime(),
            "source_id": _string(),
        },
        coerce=True,
        strict=False,
        name="connector.usfs_wildfire",
    ),
    "connector.usgs_designmaps": DataFrameSchema(
        {
            "lat": _float(nullable=False),
            "lon": _float(nullable=False),
            "pga_10in50_g": _float(),
            "observed_at": _datetime(),
            "source_id": _string(),
        },
        coerce=True,
        strict=False,
        name="connector.usgs_designmaps",
    ),
    "connector.noaa_storm_events": DataFrameSchema(
        {
            "county_id": _string(),
            "winter_storms_10yr_county": _float(),
            "observed_at": _datetime(),
            "source_id": _string(),
        },
        coerce=True,
        strict=False,
        name="connector.noaa_storm_events",
    ),
    "connector.pad_us": DataFrameSchema(
        {
            "place_id": _string(),
            "public_land_acres_30min": _float(),
            "observed_at": _datetime(),
            "source_id": _string(),
        },
        coerce=True,
        strict=False,
        name="connector.pad_us",
    ),
    "connector.fcc_bdc": DataFrameSchema(
        {
            "geo_id": _string(),
            "broadband_gbps_flag": _bool(),
            "observed_at": _datetime(),
            "source_id": _string(),
        },
        coerce=True,
        strict=False,
        name="connector.fcc_bdc",
    ),
    "connector.hud_fmr": DataFrameSchema(
        {
            "geo_id": _string(),
            "hud_fmr_2br": _float(),
            "observed_at": _datetime(),
            "source_id": _string(),
        },
        coerce=True,
        strict=False,
        name="connector.hud_fmr",
    ),
    "connector.eia_v2": DataFrameSchema(
        {
            "state": _string(),
            "res_price_cents_per_kwh": _float(),
            "observed_at": _datetime(),
            "source_id": _string(),
        },
        coerce=True,
        strict=False,
        name="connector.eia_v2",
    ),
    "connector.usfs_trails": DataFrameSchema(
        {
            "place_id": _string(),
            "minutes_to_trailhead": _float(),
            "observed_at": _datetime(),
            "source_id": _string(),
        },
        coerce=True,
        strict=False,
        name="connector.usfs_trails",
    ),
    "connector.usgs_epqs": DataFrameSchema(
        {
            "place_id": _string(),
            "slope_gt15_pct_within_10km": _float(),
            "observed_at": _datetime(),
            "source_id": _string(),
        },
        coerce=True,
        strict=False,
        name="connector.usgs_epqs",
    ),
    "connector.census_acs": DataFrameSchema(
        {
            "geo_id": _string(),
            "geo_level": _string(),
            "median_household_income": _float(),
            "observed_at": _datetime(),
            "source_id": _string(),
        },
        coerce=True,
        strict=False,
        name="connector.census_acs",
    ),
}


def _schema_context(kind: SchemaKind, name: str) -> LogContext:
    action = f"{kind}-validate"
    source = name if kind == "connector" else None
    return LogContext(event="schema.validation", module="data.schemas", action=action, source_id=source)


def _collect_adjustments(
    original_dtypes: Mapping[str, str],
    validated: pd.DataFrame,
    *,
    ignored_columns: Iterable[str] | None = None,
) -> MutableMapping[str, object]:
    ignored = set(ignored_columns or [])
    dtype_changes = []
    for column, before in original_dtypes.items():
        if column in ignored:
            continue
        if column not in validated.columns:
            continue
        after = str(validated[column].dtype)
        if after != before:
            dtype_changes.append({"column": column, "from": before, "to": after})
    added = [col for col in validated.columns if col not in original_dtypes]
    removed = [col for col in original_dtypes if col not in validated.columns]
    payload: MutableMapping[str, object] = {}
    if dtype_changes:
        payload["dtype_changes"] = dtype_changes
    if added:
        payload["added_columns"] = added
    if removed:
        payload["dropped_columns"] = removed
    return payload


def _validate(
    name: str,
    frame: pd.DataFrame,
    *,
    mapping: Mapping[str, DataFrameSchema],
    kind: SchemaKind,
    lazy: bool,
) -> pd.DataFrame:
    schema = mapping.get(name)
    if schema is None:
        return pd.DataFrame(frame)

    frame_obj = pd.DataFrame(frame)
    original_dtypes = {column: str(dtype) for column, dtype in frame_obj.dtypes.items()}
    try:
        validated = schema.validate(frame_obj, lazy=lazy)
    except PanderaSchemaError as exc:
        context: MutableMapping[str, object] = {"schema": name, "kind": kind}
        failure_cases = getattr(exc, "failure_cases", None)
        if failure_cases is not None:
            try:
                context["failure_cases"] = failure_cases.head(10).to_dict("records")
            except Exception:  # pragma: no cover - defensive guard
                context["failure_cases"] = str(failure_cases)
        raise SchemaError(f"{name} schema validation failed", context=context) from exc

    adjustments = _collect_adjustments(original_dtypes, validated)
    if adjustments:
        info(_schema_context(kind, name), "schema-adjustments", **adjustments)
    return validated


def validate_table_schema(table: str, frame: pd.DataFrame, *, lazy: bool = False) -> pd.DataFrame:
    """Validate a canonical table DataFrame against the registered schema."""

    return _validate(table, frame, mapping=TABLE_SCHEMAS, kind="table", lazy=lazy)


def validate_connector_schema(
    source_id: str, frame: pd.DataFrame, *, lazy: bool = False
) -> pd.DataFrame:
    """Validate a connector payload against the registered schema."""

    return _validate(source_id, frame, mapping=CONNECTOR_SCHEMAS, kind="connector", lazy=lazy)


__all__ = [
    "CONNECTOR_SCHEMAS",
    "SchemaKind",
    "TABLE_SCHEMAS",
    "validate_connector_schema",
    "validate_table_schema",
]
