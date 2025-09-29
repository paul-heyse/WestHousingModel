## 1. Connector Implementations
- [x] 1.1 Inventory existing connectors and document which rely on stub payloads or hard-coded returns.
- [ ] 1.2 Implement reusable HTTP/fetch helpers (auth, pagination, retry) plus fixture playback for tests.
- [ ] 1.3 Replace census, wildfire, seismic, storm events, PAD-US, FCC, HUD FMR, EIA, trails, and EPQS stubs with full normalization pipelines and Pandera validation.
- [ ] 1.4 Ensure failure capture writes raw payloads with correlation ids and that repository stale/fallback logging continues to operate.

## 2. Testing & Fixtures
- [ ] 2.1 Create fixture snapshots for each connector (success + representative failure) under `tests/data/connectors/`.
- [ ] 2.2 Expand unit/integration tests to exercise real connectors via fixture playback and repository cache flows.
- [ ] 2.3 Update golden pipelines (place/site/ops/valuation) to consume the new normalized outputs.

## 3. Documentation & Spec Updates
- [ ] 3.1 Update connector specs to reference real implementations and new helper utilities.
- [ ] 3.2 Document the fetch helper patterns and fixture workflow in `docs/` / architecture.
- [ ] 3.3 Remove references to stubs from archived change notes and README, highlighting the all-real connector baseline.
