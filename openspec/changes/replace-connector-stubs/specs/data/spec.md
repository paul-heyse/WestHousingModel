## MODIFIED Requirements

### Requirement: Hazard & Context Connectors

The system SHALL provide validated connectors for public datasets powering hazards and context features (USFS Wildfire, USGS Design Maps, NOAA Storm Events, PAD-US, FCC BDC, HUD FMR, EIA v2, USFS Trails, USGS EPQS) implemented as real fetch/normalize pipelines rather than stubs.

#### Scenario: Real fetch pipeline
- **WHEN** a connector is invoked through the repository
- **THEN** it SHALL perform actual data retrieval (or fixture playback in tests), normalize into the canonical schema, validate via Pandera, and integrate with failure capture.

#### Scenario: Fixture-backed tests
- **WHEN** test suites exercise these connectors
- **THEN** they SHALL load deterministic fixtures that mirror real API responses and assert schema + logging behavior, without relying on stubbed DataFrames.

### Requirement: Observability & Provenance for Connectors

Each connector SHALL emit structured logs, propagate correlation IDs, and expose transformation metadata to downstream callers (place/site/ops feature builders, manifests).

#### Scenario: Logging and failure capture
- **WHEN** a connector succeeds
- **THEN** the repository logs `status=refreshed` with latency, and the connector returns rows with canonical `source_id` / `observed_at` columns; failures SHALL emit `status=error` and capture raw payloads with correlation ids.

### Requirement: Documentation of Connector Utilities

The architecture docs SHALL describe the shared connector utilities (HTTP client, pagination/retry, fixture playback) and reference real connector implementations.
