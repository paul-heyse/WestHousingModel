# Connector Stub Inventory

Review date: 2025-09-29

The default connectors registered in `west_housing_model.data.connectors.__init__` were reviewed to confirm which still rely on stub payloads or hard-coded returns.

| Connector | Current factory location | Implementation status | Notes |
| --- | --- | --- | --- |
| `connector.census_acs` | `src/west_housing_model/data/connectors/__init__.py` | Stub payload unless `fetch_override` injected | Real HTTP client exists in `census_acs.py` but factory ignores it |
| `connector.usfs_wildfire` | same as above | Stub payload with static percentile | No dedicated module or external call |
| `connector.usgs_designmaps` | same | Stub payload with static PGA value | Missing integration with USGS DesignMaps API |
| `connector.noaa_storm_events` | same | Stub payload returning constant counts | Real logic lives in `storm_events.py` but the factory does not call it |
| `connector.pad_us` | same | Stub payload returning constant acreage | No PAD-US fetch module yet |
| `connector.fcc_bdc` | same | Stub payload returning broadband flag | Needs FCC BDC dataset access |
| `connector.hud_fmr` | same | Stub payload returning constant rent | Needs HUD API connector |
| `connector.eia_v2` | same | Stub payload returning constant cents/kWh | Module absent; requires EIA v2 integration |
| `connector.usfs_trails` | same | Stub payload returning constant minutes | No USFS trails client |
| `connector.usgs_epqs` | same | Stub payload returning constant slope % | Needs EPQS elevation processing |
