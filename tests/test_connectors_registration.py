from __future__ import annotations

import importlib


def test_default_connectors_include_census_acs() -> None:
    module = importlib.import_module("west_housing_model.data.connectors")
    # Reload to ensure module-level registration executes even if prior tests cleared state
    module = importlib.reload(module)

    assert "connector.census_acs" in module.DEFAULT_CONNECTORS
