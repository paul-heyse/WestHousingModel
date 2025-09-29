from __future__ import annotations

import importlib


def test_default_connectors_include_census_acs() -> None:
    module = importlib.import_module("west_housing_model.data.connectors")
    # Reload to ensure module-level registration executes even if prior tests cleared state
    module = importlib.reload(module)

    assert "connector.census_acs" in module.DEFAULT_CONNECTORS
    assert "connector.usfs_wildfire" in module.DEFAULT_CONNECTORS
    assert "connector.eia_v2" in module.DEFAULT_CONNECTORS

    wildfire = module.DEFAULT_CONNECTORS["connector.usfs_wildfire"].fetch(geo_id="08005")
    assert "wildfire_risk_percentile" in wildfire.columns
    eia = module.DEFAULT_CONNECTORS["connector.eia_v2"].fetch(state="CO")
    assert "res_price_cents_per_kwh" in eia.columns
