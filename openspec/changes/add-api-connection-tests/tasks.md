## 1. Planning & Inventory

- [ ] 1.1 Enumerate all registry sources (base + supplement) and map to implemented connectors or mark as missing.
- [ ] 1.2 Document credential, rate-limit, and TTL expectations per source; capture gaps (e.g., required API keys, accepted parameter sets).
- [ ] 1.3 Design live-vs-recorded testing approach, including fixture tooling (`vcrpy`/`pytest-recording`) and CI gating strategy.

## 2. Implementation

- [ ] 2.1 Implement or stub missing connectors for registry sources (bls_timeseries, census_bps, zillow_research, fema_nfhl, routes_service/osm_overpass, osrm) or create follow-up changes if out of scope.
- [ ] 2.2 Add connector integration tests that execute real API calls when `LIVE_API_TESTS=1` and fall back to recordings otherwise.
- [ ] 2.3 Add negative-path tests covering credential absence, rate-limit responses, network failures, and schema drift handling.
- [ ] 2.4 Extend repository tests to assert cache index updates, stale fallback behaviour, and captured failure payloads for each connector.
- [ ] 2.5 Update documentation (`tests/README.md`, `architecture.md` testing appendix) describing the API testing workflow and credential management.

## 3. Validation

- [ ] 3.1 Run `pytest -q` with and without `LIVE_API_TESTS=1` to confirm deterministic behaviour from recordings.
- [ ] 3.2 Run `openspec validate add-api-connection-tests --strict` and update specs until clean.
- [ ] 3.3 Ensure CI configuration exercises the recorded tests and skips live calls by default (document override procedure).
