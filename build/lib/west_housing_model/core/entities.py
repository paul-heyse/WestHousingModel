"""Domain entities for the West Housing Model."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Mapping, MutableMapping, Optional, Sequence

from west_housing_model.core.enums import GeoLevel, ScenarioType


@dataclass(frozen=True)
class SourceAttribution:
    """Represents provenance for a single dataset pull."""

    source_id: str
    as_of: Optional[date]


@dataclass(frozen=True)
class SourceManifest:
    """Captures the data vintage manifest attached to scenarios and exports."""

    as_of: Optional[date] = None
    sources: Mapping[str, str] = field(default_factory=dict)

    def get_version(self, source_id: str) -> Optional[str]:
        """Return the recorded version for a source, if available."""

        return self.sources.get(source_id)


@dataclass(frozen=True)
class Place:
    """Geographic aggregation used for market selection and percentile baselines."""

    place_id: str
    geo_level: GeoLevel
    geo_code: str
    name: str
    features: Mapping[str, float] = field(default_factory=dict)
    feature_percentiles: Mapping[str, float] = field(default_factory=dict)
    data_vintage: Optional[SourceAttribution] = None
    metadata: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class HazardProfile:
    """Measured hazard context derived from authoritative datasets."""

    in_sfha: Optional[bool] = None
    fema_zone: Optional[str] = None
    distance_to_sfha_m: Optional[float] = None
    wildfire_risk_percentile: Optional[int] = None
    pga_10in50_g: Optional[float] = None
    hdd_annual: Optional[float] = None
    cdd_annual: Optional[float] = None
    winter_storms_10yr_county: Optional[int] = None


@dataclass(frozen=True)
class ProximityContext:
    """Binary proximity indicators that influence livability and risk."""

    pipelines_within_500m: Optional[bool] = None
    rail_within_300m: Optional[bool] = None
    regulated_facility_within_1km: Optional[bool] = None


@dataclass(frozen=True)
class OpsContext:
    """Operating context annotations carried alongside properties."""

    utility_rate_note: Optional[str] = None
    broadband_gbps_flag: Optional[bool] = None
    zoning_context_note: Optional[str] = None


@dataclass(frozen=True)
class Property:
    """Candidate site evaluated by the Opportunity Identifier & Evaluator."""

    property_id: str
    address: str
    latitude: float
    longitude: float
    place_id: str
    hazard_profile: HazardProfile = field(default_factory=HazardProfile)
    proximity_context: ProximityContext = field(default_factory=ProximityContext)
    ops_context: OpsContext = field(default_factory=OpsContext)
    feature_values: Mapping[str, float] = field(default_factory=dict)
    provenance: Sequence[SourceAttribution] = field(default_factory=tuple)


@dataclass(frozen=True)
class CapexItem:
    """Represents a line item in a capital expenditure plan."""

    category: str
    amount: float
    execution_year: int
    notes: Optional[str] = None


@dataclass(frozen=True)
class RentAssumptions:
    """Baseline and target rent assumptions for a scenario."""

    current_rent: Mapping[str, float]
    target_rent: Mapping[str, float]
    growth_overrides: Mapping[int, float] = field(default_factory=dict)


@dataclass(frozen=True)
class OpexAssumptions:
    """Operating expense assumptions derived from user input and hazards."""

    base_opex_per_unit: float
    insurance_uplift_pct: Optional[float] = None
    utilities_scaler: Optional[float] = None
    notes: Optional[str] = None


@dataclass(frozen=True)
class LeverageAssumptions:
    """Capital stack assumptions used in valuation calculations."""

    loan_to_value: float
    interest_rate: float
    amort_years: Optional[int] = None
    interest_only_years: int = 0
    dscr_target: Optional[float] = None


@dataclass(frozen=True)
class Scenario:
    """A reproducible set of overrides, outputs, and data vintages."""

    scenario_id: str
    property_id: str
    name: str
    scenario_type: ScenarioType
    unit_mix: Mapping[str, int]
    rent_assumptions: RentAssumptions
    opex_assumptions: OpexAssumptions
    capex_plan: Sequence[CapexItem] = field(default_factory=tuple)
    leverage: Optional[LeverageAssumptions] = None
    weights: Mapping[str, float] = field(default_factory=dict)
    source_manifest: SourceManifest = field(default_factory=SourceManifest)
    notes: Optional[str] = None

    def mutable_unit_mix(self) -> MutableMapping[str, int]:
        """Return a mutable copy of the unit mix for caller convenience."""

        return dict(self.unit_mix)


__all__ = [
    "CapexItem",
    "HazardProfile",
    "LeverageAssumptions",
    "OpsContext",
    "Place",
    "Property",
    "ProximityContext",
    "RentAssumptions",
    "Scenario",
    "ScenarioType",
    "SourceAttribution",
    "SourceManifest",
]
