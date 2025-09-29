"""Valuation orchestrator and public API."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Mapping, Optional, Sequence

import pandas as pd

from west_housing_model.data.catalog import validate_table
from west_housing_model.scoring.deal_quality import compute_deal_quality
from west_housing_model.utils.manifest import build_source_manifest


@dataclass(frozen=True)
class ValuationInputs:
    scenario_id: str
    property_id: str
    as_of: Optional[pd.Timestamp]
    place_features: Mapping[str, Any]
    site_features: Mapping[str, Any]
    ops_features: Mapping[str, Any]
    user_overrides: Mapping[str, Any]


def _compute_rent_baseline(inputs: ValuationInputs) -> Dict[str, Any]:
    # Simplified baseline: use override if present else fallback
    override = inputs.user_overrides.get("rent_baseline")
    baseline = (
        float(override)
        if override is not None
        else float(inputs.place_features.get("zori_level", 0.0))
    )
    # UC uplift small cap example
    uc_uplift = 0.015 if int(inputs.place_features.get("aker_market_fit", 0)) >= 75 else 0.0
    return {"rent_baseline": baseline * (1.0 + uc_uplift)}


def _compute_growth(inputs: ValuationInputs) -> Dict[str, Any]:
    jobs = float(inputs.place_features.get("msa_jobs_t12", 0.0))
    supply = float(inputs.place_features.get("permits_5plus_per_1k_hh_t12", 0.0))
    g_base = float(inputs.user_overrides.get("g_base", 0.02))
    growth = max(-0.02, min(0.06, g_base + 0.2 * jobs - 0.1 * supply))
    return {"growth": growth}


def _compute_opex_and_insurance(inputs: ValuationInputs) -> Dict[str, Any]:
    base_opex = float(inputs.user_overrides.get("base_opex_per_unit_year", 3000.0))
    hdd = inputs.site_features.get("hdd_annual")
    cdd = inputs.site_features.get("cdd_annual")
    scaler = 1.0
    if hdd is not None and cdd is not None:
        scaler = 0.5 * (float(hdd) / 5000.0) + 0.5 * (float(cdd) / 1000.0)
    insurance = 0.0
    if bool(inputs.site_features.get("in_sfha", False)):
        insurance += 250.0
    wf = inputs.site_features.get("wildfire_risk_percentile")
    if wf is not None and int(wf) >= 75:
        insurance += 150.0
    pga = inputs.site_features.get("pga_10in50_g")
    if pga is not None and float(pga) >= 0.15:
        insurance += 100.0
    return {
        "utilities_scaler": scaler,
        "insurance_uplift": insurance,
        "opex_per_unit_year": base_opex * scaler + insurance,
    }


def _irr(cashflows: Sequence[float], *, guess: float = 0.1) -> float:
    rate = guess
    for _ in range(100):
        if rate <= -0.999:
            rate = -0.5
        npv = 0.0
        derivative = 0.0
        for period, cash in enumerate(cashflows):
            denom = (1.0 + rate) ** period
            if denom == 0:
                denom = 1e-12
            npv += cash / denom
            if period > 0:
                derivative -= period * cash / ((1.0 + rate) ** (period + 1))
        if abs(derivative) < 1e-9:
            break
        new_rate = rate - npv / derivative
        if abs(new_rate - rate) < 1e-6:
            if -0.999 < new_rate < 10:
                return float(new_rate)
            break
        rate = new_rate
    return float(max(rate, 0.0))


def _compute_capex(inputs: ValuationInputs) -> Dict[str, Any]:
    plan = inputs.user_overrides.get("capex_plan", {})

    def _coerce(value: Any) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0

    if isinstance(plan, Mapping):
        base_total = sum(_coerce(v) for v in plan.values())
    else:
        base_total = _coerce(plan)

    contingency_pct = 0.0
    if bool(inputs.site_features.get("in_sfha", False)):
        contingency_pct += 0.05
    pga_value = _coerce(inputs.site_features.get("pga_10in50_g"))
    if pga_value >= 0.15:
        contingency_pct += 0.02

    total_with_contingency = base_total * (1.0 + contingency_pct)

    schedule_override = inputs.user_overrides.get("capex_schedule")
    capex_schedule: Dict[int, float] = {}
    if isinstance(schedule_override, Mapping):
        raw_schedule: Dict[int, float] = {}
        for key, value in schedule_override.items():
            try:
                year = int(key)
            except (TypeError, ValueError):
                continue
            raw_schedule[year] = _coerce(value)
        total_override = sum(raw_schedule.values())
        if 0.0 < total_override <= 1.0 + 1e-6:
            capex_schedule = {
                year: total_with_contingency * weight for year, weight in raw_schedule.items()
            }
        else:
            capex_schedule = raw_schedule

    if not capex_schedule:
        default_weights = {0: 0.6, 1: 0.3, 2: 0.1}
        capex_schedule = {
            year: total_with_contingency * weight
            for year, weight in default_weights.items()
            if weight > 0.0
        }

    return {
        "capex_total": total_with_contingency,
        "capex_schedule": capex_schedule,
    }


def _compute_dcf(
    inputs: ValuationInputs,
    rent_baseline: float,
    growth: float,
    opex_per_unit_year: float,
    insurance_uplift: float,
    capex_schedule: Mapping[int, float],
) -> Dict[str, Any]:
    units = int(inputs.user_overrides.get("units", 100))
    long_run_growth = float(inputs.user_overrides.get("long_run_growth", 0.02))
    opex_growth = float(inputs.user_overrides.get("opex_growth", 0.02))
    terminal_growth = float(inputs.user_overrides.get("terminal_growth", 0.02))

    years = 10
    rent_series: list[float] = []
    rent = rent_baseline
    for year in range(1, years + 1):
        if year > 1:
            if year <= 5:
                incremental = growth
            else:
                blend = min(max((year - 5) / 5.0, 0.0), 1.0)
                incremental = (1.0 - blend) * growth + blend * long_run_growth
            rent *= 1.0 + incremental
        rent_series.append(rent)

    revenue_series = [rent_year * 12.0 * units for rent_year in rent_series]
    base_opex_without_insurance = max(opex_per_unit_year - insurance_uplift, 0.0)
    base_opex_series = [
        base_opex_without_insurance * ((1.0 + opex_growth) ** (year - 1)) * units
        for year in range(1, years + 1)
    ]
    insurance_series = [insurance_uplift * units for _ in range(years)]

    cap_low = float(inputs.user_overrides.get("cap_low", 0.06))
    cap_base = float(inputs.user_overrides.get("cap_base", 0.065))
    cap_high = float(inputs.user_overrides.get("cap_high", 0.07))

    discount_rate_base = float(inputs.user_overrides.get("discount_rate", cap_base + 0.02))
    discount_rate_low = discount_rate_base + 0.01
    discount_rate_high = max(discount_rate_base - 0.01, 0.0001)

    def _valuation_for(
        discount_rate: float,
        exit_cap: float,
        *,
        rent_multiplier: float = 1.0,
        insurance_multiplier: float = 1.0,
        cap_rate_shift: float = 0.0,
    ) -> Dict[str, Any]:
        cap = max(exit_cap + cap_rate_shift, 0.0001)
        dr = max(discount_rate, 0.0001)
        pv = -float(capex_schedule.get(0, 0.0))
        noi_series: list[float] = []
        cash_flows: list[float] = []
        for year in range(1, years + 1):
            idx = year - 1
            revenue = revenue_series[idx] * rent_multiplier
            insurance_cost = insurance_series[idx] * insurance_multiplier
            noi = revenue - base_opex_series[idx] - insurance_cost
            noi_series.append(noi)
            cash = noi - float(capex_schedule.get(year, 0.0))
            pv += cash / ((1.0 + dr) ** year)
            cash_flows.append(cash)
        terminal_noi = noi_series[-1] * (1.0 + terminal_growth)
        terminal_value = terminal_noi / cap
        pv += terminal_value / ((1.0 + dr) ** years)
        cash_flows[-1] += terminal_value
        return {
            "value": float(pv),
            "noi_series": noi_series,
            "cash_flows": cash_flows,
        }

    base_result = _valuation_for(discount_rate_base, cap_base)
    low_result = _valuation_for(discount_rate_low, cap_high)
    high_result = _valuation_for(discount_rate_high, cap_low)

    noistab = float(base_result["noi_series"][0])
    value_base = base_result["value"]
    value_low = low_result["value"]
    value_high = high_result["value"]

    total_cost = float(inputs.user_overrides.get("total_cost", value_base))
    initial_outlay = total_cost + float(capex_schedule.get(0, 0.0))

    def _irr_for(exit_cap: float) -> float:
        cashflows = [-initial_outlay]
        horizon = min(5, years)
        for year in range(1, horizon + 1):
            idx = year - 1
            revenue = revenue_series[idx]
            insurance_cost = insurance_series[idx]
            noi = revenue - base_opex_series[idx] - insurance_cost
            cash = noi - float(capex_schedule.get(year, 0.0))
            if year == horizon:
                terminal = (noi * (1.0 + terminal_growth)) / max(exit_cap, 0.0001)
                cash += terminal
            cashflows.append(cash)
        return _irr(cashflows)

    irr_base = _irr_for(cap_base)
    irr_low = _irr_for(cap_high)
    irr_high = _irr_for(cap_low)

    target_dscr = float(inputs.user_overrides.get("target_dscr", 1.30))
    if target_dscr <= 0:
        target_dscr = 1.30
    assumed_debt_service = float(
        inputs.user_overrides.get("debt_service", noistab / max(target_dscr, 0.01))
    )
    dscr_proxy = noistab / assumed_debt_service if assumed_debt_service else 0.0

    rent_multipliers = [0.95, 1.0, 1.05]
    cap_shifts = [-0.005, 0.0, 0.005]
    insurance_multipliers = [0.8, 1.0, 1.2]
    sensitivity_matrix: list[Dict[str, float]] = []
    for rent_mult in rent_multipliers:
        for cap_shift in cap_shifts:
            for insurance_mult in insurance_multipliers:
                scenario = _valuation_for(
                    discount_rate_base,
                    cap_base,
                    rent_multiplier=rent_mult,
                    insurance_multiplier=insurance_mult,
                    cap_rate_shift=cap_shift,
                )
                sensitivity_matrix.append(
                    {
                        "rent_multiplier": round(rent_mult, 3),
                        "cap_rate_shift": round(cap_shift, 4),
                        "insurance_multiplier": round(insurance_mult, 3),
                        "value": scenario["value"],
                    }
                )

    yoc_base = noistab / max(total_cost, 1.0)

    return {
        "noistab": noistab,
        "cap_rate_low": cap_low,
        "cap_rate_base": cap_base,
        "cap_rate_high": cap_high,
        "value_low": value_low,
        "value_base": value_base,
        "value_high": value_high,
        "yoc_base": float(yoc_base),
        "irr_5yr_low": irr_low,
        "irr_5yr_base": irr_base,
        "irr_5yr_high": irr_high,
        "dscr_proxy": float(dscr_proxy),
        "sensitivity_matrix": sensitivity_matrix,
    }


def run_valuation(inputs: ValuationInputs) -> pd.DataFrame:
    """Compose valuation modules and return validated `valuation_outputs`."""

    rent = _compute_rent_baseline(inputs)
    growth = _compute_growth(inputs)
    costs = _compute_opex_and_insurance(inputs)
    capex = _compute_capex(inputs)
    dcf = _compute_dcf(
        inputs,
        rent["rent_baseline"],
        growth["growth"],
        costs["opex_per_unit_year"],
        costs["insurance_uplift"],
        capex["capex_schedule"],
    )

    # Compute Deal Quality using available context
    wildfire = inputs.site_features.get("wildfire_risk_percentile")
    pga = inputs.site_features.get("pga_10in50_g")
    winter_storms = inputs.site_features.get("winter_storms_10yr_county")
    rent_to_income = inputs.user_overrides.get("rent_to_income")

    dq = compute_deal_quality(
        yoc=float(dcf["yoc_base"]),
        irr_5yr=float(dcf["irr_5yr_base"]),
        dscr=float(dcf["dscr_proxy"]),
        in_sfha=bool(inputs.site_features.get("in_sfha", False)),
        wildfire_risk_percentile=float(wildfire) if wildfire is not None else None,
        pga_10in50_g=float(pga) if pga is not None else None,
        winter_storms_10yr_county_percentile=(
            float(winter_storms) if winter_storms is not None else None
        ),
        # If percentile form of permits not available, omit supply penalty
        permits_5plus_per_1k_hh_percentile=None,
        rent_to_income=float(rent_to_income) if rent_to_income is not None else None,
        affordability_overridden=bool(inputs.user_overrides.get("affordability_overridden", False)),
        missing_or_stale_features_count=None,
    )

    manifest = build_source_manifest(
        as_of=inputs.as_of,
        place_features=inputs.place_features,
        site_features=inputs.site_features,
        ops_features=inputs.ops_features,
    )

    # Allow user overrides to extend/replace manifest
    user_manifest = inputs.user_overrides.get("source_manifest") or {}
    if isinstance(user_manifest, dict):
        # Shallow merge: user keys win
        manifest = {**manifest, **user_manifest}

    out = {
        "scenario_id": [inputs.scenario_id],
        "property_id": [inputs.property_id],
        # Normalize tz-aware to naive to satisfy schema
        "as_of": [
            (
                pd.to_datetime(inputs.as_of).tz_localize(None)
                if inputs.as_of is not None and getattr(inputs.as_of, "tzinfo", None) is not None
                else inputs.as_of
            )
        ],
        "noistab": [dcf["noistab"]],
        "cap_rate_low": [dcf["cap_rate_low"]],
        "cap_rate_base": [dcf["cap_rate_base"]],
        "cap_rate_high": [dcf["cap_rate_high"]],
        "value_low": [dcf["value_low"]],
        "value_base": [dcf["value_base"]],
        "value_high": [dcf["value_high"]],
        "yoc_base": [dcf["yoc_base"]],
        "irr_5yr_low": [dcf["irr_5yr_low"]],
        "irr_5yr_base": [dcf["irr_5yr_base"]],
        "irr_5yr_high": [dcf["irr_5yr_high"]],
        "dscr_proxy": [dcf["dscr_proxy"]],
        "insurance_uplift": [costs["insurance_uplift"]],
        "utilities_scaler": [costs["utilities_scaler"]],
        "aker_fit": [int(inputs.place_features.get("aker_market_fit", 0))],
        "deal_quality": [int(dq)],
        "sensitivity_matrix": [dcf["sensitivity_matrix"]],
        "source_manifest": [manifest],
    }
    frame = pd.DataFrame(out)
    return validate_table("valuation_outputs", frame)


__all__ = ["ValuationInputs", "run_valuation"]
