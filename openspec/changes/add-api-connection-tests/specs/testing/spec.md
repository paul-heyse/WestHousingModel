## ADDED Requirements

### Requirement: Registry Connector Inventory Coverage

The testing suite SHALL maintain an authoritative inventory mapping every enabled registry source (`config/sources*.yml`) to its corresponding connector implementation or an explicit "missing" marker.

#### Scenario: Inventory Export Lists Missing Connectors

- **WHEN** the inventory test runs against the registry
- **THEN** it produces a machine-readable report documenting connectors for `connector.census_acs`, `connector.usfs_wildfire`, `connector.usgs_designmaps`, `connector.noaa_storm_events`, `connector.pad_us`, `connector.fcc_bdc`, `connector.hud_fmr`, `connector.eia_v2`, `connector.usfs_trails`, `connector.usgs_epqs`
- **AND** it explicitly flags unimplemented sources such as `bls_timeseries`, `census_bps`, `zillow_research`, `fema_nfhl`, `routes_service`, `osm_overpass`, and `osrm` so follow-up work can be scheduled

### Requirement: Live API Contract Tests with Recordings

Integration tests SHALL exercise live API calls for each implemented connector (subject to credentials) and capture deterministic recordings for CI replay.

#### Scenario: Live Run Generates Recording

- **GIVEN** `LIVE_API_TESTS=1` and required credentials are present
- **WHEN** the connector integration test executes (e.g., `connector.hud_fmr`)
- **THEN** the test issues a real HTTP request, persists a sanitized recording artifact, and asserts schema-compliant DataFrame output

#### Scenario: CI Uses Recorded Fixture

- **WHEN** the same test runs without live flags (default CI)
- **THEN** the recording is replayed without network access and the assertions still pass deterministically within the defined TTL window

### Requirement: Credential and Rate-Limit Enforcement Tests

Tests SHALL verify that connectors validate credential presence, respect registry rate-limit guidance, and surface actionable errors.

#### Scenario: Missing Credential Raises Helpful Error

- **WHEN** `HUD_API_KEY` is absent and a HUD FMR test runs
- **THEN** the connector raises a `ConnectorError` with guidance on setting `HUD_API_KEY`
- **AND** the test asserts the error payload includes the `source_id` and registry metadata

#### Scenario: Rate-Limit Retry Captured

- **WHEN** a connector receives an HTTP 429 during testing (simulated via recording)
- **THEN** the retry/back-off policy is exercised and the final result or failure status is asserted in the test output

### Requirement: Failure, Offline, and Schema Drift Coverage

Repository-level tests SHALL ensure connectors degrade gracefully, capture raw payloads on schema drift, and respect offline mode semantics.

#### Scenario: Repository Falls Back to Stale Cache

- **WHEN** a connector returns an HTTP error and a cached artifact exists
- **THEN** `Repository.get` returns `STATUS_STALE`, logs a structured error with correlation id, and surfaces the cached frame

#### Scenario: Schema Drift Captures Payload

- **WHEN** an unexpected payload shape is replayed from recordings
- **THEN** the failure capture directory contains the raw CSV, and the test asserts the path exists with the correct `source_id`

### Requirement: Cache and Provenance Assertions

Tests SHALL confirm that successful connector runs populate cache artifacts and propagate provenance metadata into downstream feature builders.

#### Scenario: Cache Index Updated After Connector Run

- **WHEN** a connector test fetches fresh data
- **THEN** the SQLite cache index contains a new row with the connector `source_id`, hash key, `as_of`, and TTL

#### Scenario: Feature Builder Receives Provenance Metadata

- **WHEN** place or site feature builders consume connector outputs in tests
- **THEN** the resulting feature DataFrame retains `{source_id, observed_at}` columns and provenance sidecar entries for tooltip rendering

### Requirement: API Testing Playbook Documentation

Documentation SHALL describe how to execute live API tests, refresh recordings, and add new connectors.

#### Scenario: Contributor Follows Playbook

- **WHEN** a new developer reads the updated `tests/README.md`
- **THEN** they find step-by-step instructions for setting environment variables, running `pytest -q --live-api-tests`, refreshing recordings, and committing sanitized fixtures
