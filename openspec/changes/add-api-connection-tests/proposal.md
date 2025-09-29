## Why

The repository now ships with a wide catalogue of data connectors (ACS, wildfire, seismic, broadband, HUD FMR, EIA, trails, elevation, etc.) wired into the read-through cache, but our automated coverage stops at schema validation against synthetic payloads. We do not systematically exercise real HTTP integrations, credential handling, rate-limit behaviour, or drift detection for these sources. Several registry entries (BLS timeseries, Census BPS, Zillow Research, FEMA NFHL, OSRM/OpenRouteService, Census Building Permits, etc.) lack connector implementations entirely, leaving critical gaps in the ingest surface. A comprehensive API-connection testing initiative is needed to confirm that each connector can authenticate, query, and persist data using the live endpoints (or sanctioned recorded fixtures), while documenting outstanding connector work and ensuring graceful degradation in offline mode.

## What Changes

- **Inventory & Gap Analysis**: Catalogue every registry source, map it to an implemented connector (or mark it as missing), and capture credentials/rate-limit requirements. Explicitly flag currently unimplemented APIs (e.g., `bls_timeseries`, `census_bps`, `zillow_research`, `fema_nfhl`, `routes_service`, `osm_overpass`, `osrm`) with recommended connector scaffolding tasks.
- **Live/Recorded API Exercisers**: For each implemented connector (`connector.census_acs`, `connector.usfs_wildfire`, `connector.usgs_designmaps`, `connector.noaa_storm_events`, `connector.pad_us`, `connector.fcc_bdc`, `connector.hud_fmr`, `connector.eia_v2`, `connector.usfs_trails`, `connector.usgs_epqs`), add integration tests that hit the real API when credentials/network are available, backed by deterministic recorded fixtures (e.g., `pytest-recording` or `vcrpy`) to keep CI deterministic.
- **Credential & Rate Limit Validation**: Add tests that verify connectors honour configured auth keys, emit descriptive errors when credentials are missing, and respect registry TTLs and rate limit guidance (including back-off retries and header inspection where feasible).
- **Failure, Offline, & Schema Drift Coverage**: Exercise each connector’s failure handling (HTTP 4xx/5xx, malformed payloads, schema drift). Confirm repository falls back to cached artifacts with `STATUS_STALE`, logs failures with captured payloads, and raises actionable diagnostics.
- **Cache & Provenance Assertions**: Validate that successful connector runs populate Parquet artifacts, update the SQLite cache index, and propagate `{source_id, as_of}` metadata end-to-end into feature builders, ensuring provenance tooltips remain accurate.
- **Documentation & Playbooks**: Extend the testing appendix (`tests/README.md`, architecture/testing section) with instructions for refreshing recordings, adding new connectors, and handling credentials required for live API runs.

## Impact

- **Affected Specs**: `openspec/specs/testing/spec.md` (new API connection testing requirements).
- **Affected Code**:
  - `tests/integration/` (new API contract tests, failure simulations, recorded fixtures).
  - `tests/data/fixtures/` (HTTP recordings, golden payloads, credential placeholders).
  - `src/west_housing_model/data/connectors/` (optional patches for missing connectors, retry/back-off logic, credential validation hooks).
  - `src/west_housing_model/data/repository.py` (enhanced metadata surfaced for logging/verifications if gaps found).
  - `docs/` & `tests/README.md` (expanded documentation for API testing workflows).
- **Dependencies & Credentials**: Requires environment variables (`CENSUS_API_KEY`, `HUD_API_KEY`, `EIA_API_KEY`, optional OSRM/ORS tokens). Proposal must document temporary fallbacks for contributors without credentials and ensure CI runs exclusively against recorded fixtures.
