## Why

Site screening requires converting hazard and proximity connectors (FEMA NFHL, USFS wildfire, USGS seismic, NOAA normals/storms, pipelines/rail/EPA proximities) into deterministic site features to power flags and valuation adjustments.

## What Changes

- Add `site_features.py` pure transforms mapping hazard/proximity inputs to typed site features
- Enforce Pandera validation; emit provenance sidecars
- Provide minimal thresholds and mappings for flags (e.g., in_sfha, wildfire percentile, PGA screen)

## Impact

- Affected specs: features/site (new capability)
- Affected code: `src/west_housing_model/features/site_features.py`, `src/west_housing_model/data/catalog.py`, `src/west_housing_model/cli/`
