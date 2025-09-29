## Why

We now have stabilized repository, features, scoring, and valuation APIs. The next step is to implement a small, performant Streamlit UI that surfaces Explore/Evaluate/Scenarios/Settings, integrates provenance tooltips, supports exports, and persists state in alignment with Scenario manifests for reproducible decisions.

## What Changes

- Build Streamlit pages: Explore, Evaluate, Scenarios, Settings.
- Integrate provenance tooltips using feature/valuation sidecar metadata.
- Implement exports (PDF one‑pager + CSV) embedding the scenario manifest.
- Persist UI state to/from Scenario JSON (save/load) with vintage locking.
- Navigation + performance tuning (caching, offline/stale badges).

## Impact

- Affected specs: ui, exports, scenarios
- Affected code: `src/west_housing_model/ui/*`, `src/west_housing_model/ui/exporters.py`, tests under `tests/ui/*`
- CLI unaffected (optional helpers may be added later)
