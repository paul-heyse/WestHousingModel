## Context

Implement Streamlit UI last, on top of stabilized repository, features, scoring, and valuation. UI must remain thin (no business logic), provide provenance tooltips, exports, and scenario‑aligned state persistence.

## Goals / Non-Goals

- Goals: simple nav, responsive interactions, provenance everywhere, reproducible exports
- Non‑Goals: complex theming, multi‑tenant auth, heavy geospatial rendering

## Decisions

- Framework: Streamlit multi‑page (`ui/app.py` + page modules)
- State: `st.session_state` + scenario JSON persistence; lock/unlock vintage flag
- Provenance: feature/valuation sidecars propagated into a shared `provenance_dict`
- Performance: `st.cache_data` for repository/feature calls; latency budgets Explore ≤200ms table / ≤500ms map refresh
- Offline/Status: badge components for Fresh/Stale/Offline states from repository results
- Exports: `ui/exporters.py` for PDF/CSV; embed `source_manifest` and inputs/overrides

## Architecture

- Pages: Explore, Evaluate, Scenarios, Settings
- Shared services: repository loader, feature/valuation orchestrator, provenance binder
- Error handling: fail fast on Schema/Computation errors with user‑readable messages

## Migration Plan

1) Ship pages incrementally behind a stable nav
2) Add tooltips and exports
3) Wire scenario save/load with manifest lock

## Open Questions

- Do we want deep‑linking via query params for `scenario_id`?
- Should PDF include a mini map snapshot (requires extra dependency)?
