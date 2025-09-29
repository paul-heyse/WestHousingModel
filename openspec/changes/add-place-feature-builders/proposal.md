## Why

With connectors in place (ACS, BLS, Census BPS, FCC BDC, PAD-US, etc.), we need minimal, deterministic place-level feature builders that aggregate public datasets into Aker’s four pillars (Urban Convenience, Outdoor Access, Innovation Jobs, Supply Constraints). This enables ranking markets and powering Aker Fit.

## What Changes

- Add `place_features.py` pure functions that transform connector outputs into typed pillar components
- Enforce Pandera validation against cataloged schemas; emit provenance sidecars per column
- Compute pillar indices via regional percentiles (configurable) and expose contribution-ready outputs
- Wire minimal CLI path to build a small state/MSA batch

## Impact

- Affected specs: features/place (new capability)
- Affected code: `src/west_housing_model/features/place_features.py`, `src/west_housing_model/data/catalog.py`, `src/west_housing_model/cli/`
