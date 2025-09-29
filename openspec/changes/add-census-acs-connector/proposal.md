## Why

We need at least one end‑to‑end connector to exercise repository read‑through caching, offline mode, and failure handling. The Census ACS provides core income and rent‑to‑income context and is well‑suited as the first connector.

## What Changes

- Implement a `census_acs` connector that fetches selected ACS tables at tract/MSA level
- Normalize to a typed DataFrame with documented columns and `{source_id, as_of}`
- Integrate with repository: deterministic keying, TTL, Parquet/GeoParquet artifacts
- Handle offline mode and network failures; log failures to `cache/failures/census_acs/`
- Add tests (unit + integration with fixture payloads) and CLI wire‑up

## Impact

- Affected specs: connectors/census‑acs (new capability)
- Affected code: `src/west_housing_model/data/connectors/census_acs.py`, `src/west_housing_model/data/catalog.py`, `src/west_housing_model/cli/`
