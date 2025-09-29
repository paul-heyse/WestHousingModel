import pandas as pd

from west_housing_model.valuation import ValuationInputs, run_valuation


def test_run_valuation_basic_flow_validates():
    inputs = ValuationInputs(
        scenario_id="scn-1",
        property_id="prop-1",
        as_of=pd.Timestamp("2025-09-01"),
        place_features={
            "aker_market_fit": 80,
            "msa_jobs_t12": 0.02,
            "permits_5plus_per_1k_hh_t12": 0.5,
            "zori_level": 1500.0,
        },
        site_features={
            "in_sfha": False,
            "wildfire_risk_percentile": 70,
            "pga_10in50_g": 0.12,
            "hdd_annual": 6000.0,
            "cdd_annual": 900.0,
        },
        ops_features={
            "utility_rate_note": "context",
            "broadband_gbps_flag": True,
        },
        user_overrides={
            "units": 50,
            "base_opex_per_unit_year": 2800.0,
            "cap_base": 0.065,
            "cap_low": 0.06,
            "cap_high": 0.07,
            "total_cost": 10000000.0,
        },
    )

    out = run_valuation(inputs)

    # Required columns exist and basic value sanity
    for col in [
        "scenario_id",
        "property_id",
        "as_of",
        "noistab",
        "cap_rate_low",
        "cap_rate_base",
        "cap_rate_high",
        "value_low",
        "value_base",
        "value_high",
        "yoc_base",
        "irr_5yr_base",
        "sensitivity_matrix",
        "dscr_proxy",
        "insurance_uplift",
        "utilities_scaler",
        "source_manifest",
    ]:
        assert col in out.columns

    assert out.loc[0, "scenario_id"] == "scn-1"
    assert out.loc[0, "property_id"] == "prop-1"
    assert out.loc[0, "noistab"] > 0
    matrix = out.loc[0, "sensitivity_matrix"]
    assert isinstance(matrix, list)
    assert len(matrix) == 27
