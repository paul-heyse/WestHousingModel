## Why

Operational context features (utilities, broadband, zoning notes) support valuation and UI context. We need a minimal, deterministic builder to materialize ops features for sites.

## What Changes

- Add `ops_features.py` pure functions to map EIA v2, FCC BDC, and optional zoning inputs into typed ops features
- Enforce Pandera validation; emit provenance sidecars

## Impact

- Affected specs: features/ops (new capability)
- Affected code: `src/west_housing_model/features/ops_features.py`, `src/west_housing_model/data/catalog.py`, `src/west_housing_model/cli/`
