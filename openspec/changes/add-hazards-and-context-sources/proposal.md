## Why

To support hazards and operating/context features defined in the architecture, we need first-party connectors for public datasets beyond ACS/BLS/ZORI: wildfire risk (USFS), seismic (USGS design maps), winter events (NOAA), outdoor access (PAD-US, USFS trails), broadband (FCC BDC), rent reference (HUD FMR), and utilities (EIA v2), plus elevation/slope (USGS EPQS). These power the Aker Fit pillars and valuation guardrails while preserving offline operation via the repository cache.

## What Changes

- Add connectors and Pandera schemas for:
  - USFS Wildfire Risk to Communities → `wildfire_risk_percentile` (tract/block-group)
  - USGS Seismic Design Maps (ASCE-7) → `pga_10in50_g` (point)
  - NOAA Storm Events (NCEI) → `winter_storms_10yr_county` (county aggregates)
  - PAD-US (Protected Areas) → `public_land_acres_30min` (within 30-min drive; MVP: vector overlay scaffolding with later isochrone integration)
  - FCC BDC (fixed availability) → `broadband_gbps_flag` (tract/place aggregation)
  - HUD FMR API → `fmr_*` reference for rent baseline checks
  - EIA API v2 → `utilities_scaler` inputs (state RES bands)
  - USFS Trails → nearest trailhead distance (`minutes_to_trailhead` via routing later; MVP: nearest distance placeholder)
  - USGS EPQS → elevation samples for slope context (`slope_gt15_pct_within_10km` downstream)
- Wire TTLs from `config/sources.yml` into repository fetches; capture failures in `data/cache/failures/<source_id>/`.
- Update feature builders to consume normalized outputs and compute/append new columns per architecture.
- Update UI Settings data dictionary and provenance tooltips for new features.

## Impact

- Affected specs: connectors, place/site/ops features, data quality
- Affected code: `src/west_housing_model/data/connectors/*`, `src/west_housing_model/data/catalog.py`, `src/west_housing_model/features/*`, `src/west_housing_model/ui/*`
- Tests: unit (connectors), integration (repository + connectors), golden (end-to-end row), performance smoke
