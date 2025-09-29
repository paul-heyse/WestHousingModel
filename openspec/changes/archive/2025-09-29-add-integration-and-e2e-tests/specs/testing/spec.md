## ADDED Requirements

### Requirement: Repository Integration Coverage

The system SHALL provide integration tests that exercise the repository read-through cache with connectors, including TTL, offline mode, failure capture, and structured logging.

#### Scenario: Read-through cache populates artifacts

- **WHEN** a connector is fetched for a key without an existing cache
- **THEN** the repository writes a Parquet artifact, updates the index, logs status `refreshed`, and returns the fetched frame

#### Scenario: TTL freshness and expiry behaviour

- **WHEN** a cached artifact is requested within TTL
- **THEN** status `fresh` is returned without invoking the connector
- **AND WHEN** the TTL has expired
- **THEN** the connector is called again, status `refreshed` is returned, and the cache is updated

#### Scenario: Offline fallback serves stale data

- **WHEN** offline mode is enabled and a cached artifact exists
- **THEN** the repository returns status `stale` with the cached frame and includes fallback metadata

#### Scenario: Schema drift is captured

- **WHEN** a connector emits columns that violate its schema
- **THEN** a failure payload (log + sample data) is written and a schema error is raised

#### Scenario: Per-source locks prevent duplicate writes

- **WHEN** multiple refresh operations run in parallel for the same source/key
- **THEN** only one artifact is written and both callers observe consistent cache metadata

### Requirement: CLI Integration Contracts

The CLI SHALL expose deterministic JSON/text contracts, proper exit codes, and structured logging entries for refresh, validate, features, and render commands.

#### Scenario: Refresh command emits JSON contract

- **WHEN** `refresh --json` succeeds online
- **THEN** output includes `status`, `cache_hit`, `cache_key`, `artifact_path`, `correlation_id`, and runtime metadata
- **AND WHEN** run with `--offline`
- **THEN** output reports status `stale` and `cache_hit: true`

#### Scenario: Features command produces canonical artifacts

- **WHEN** place and site feature CSV inputs are supplied
- **THEN** the CLI writes Parquet outputs matching catalog-required columns with exit code 0

#### Scenario: Render command returns valuation manifest

- **WHEN** `render --json` is invoked with a scenario payload
- **THEN** output contains valuation rows with embedded `source_manifest`

#### Scenario: Validate command returns registry status

- **WHEN** `validate --json` runs
- **THEN** payload includes `registry_ok` and serialized registry entries

### Requirement: Structured Logging Assertions

Structured logs SHALL include correlation IDs, cache keys, statuses, and durations for repository and CLI integration paths.

#### Scenario: Repository log fields asserted

- **WHEN** repository integration tests run
- **THEN** emitted logs contain `correlation_id`, `status`, `cache_key`, and `duration_ms`

#### Scenario: CLI commands propagate correlation ids

- **WHEN** `refresh` is executed
- **THEN** both the returned payload and log entries share the same `correlation_id`

### Requirement: Feature Pipeline Golden Integration

Integration tests SHALL produce deterministic feature outputs and validate them against golden snapshots.

#### Scenario: Place and site features match goldens

- **WHEN** building place and site features from sample CSVs
- **THEN** resulting DataFrames match stored golden JSON/Parquet snapshots (ignoring dtype-only differences)

#### Scenario: Ops features match golden snapshot

- **WHEN** building ops features from sample operations data
- **THEN** the resulting DataFrame matches the stored golden snapshot and provenance metadata is available

### Requirement: Valuation Integration Snapshot

Valuation integration tests SHALL exercise the end-to-end valuation pipeline and verify deterministic outputs.

#### Scenario: Valuation matches expected snapshot

- **WHEN** running `run_valuation` with the golden scenario payload
- **THEN** the resulting DataFrame matches the golden valuation JSON, including `source_manifest`

### Requirement: UI and Exporter Smoke Coverage

The system SHALL include smoke tests ensuring Streamlit modules import and exporters produce manifest-rich artifacts.

#### Scenario: Streamlit pages import without Streamlit runtime

- **WHEN** Streamlit is monkeypatched with stubs
- **THEN** `page_explore`, `page_evaluate`, `page_scenarios`, and `page_settings` execute without raising errors

#### Scenario: Exporters return buffers with manifests

- **WHEN** `export_csv` and `export_pdf_onepager` are invoked in integration tests
- **THEN** outputs contain manifest data and non-empty payloads

### Requirement: Performance Smoke Budgets

Integration tests SHALL enforce sub-second smoke budgets for place feature builds and CLI refresh operations on developer hardware.

#### Scenario: Place feature build completes within budget

- **WHEN** building place features for ≤50 rows in-memory
- **THEN** execution completes under 0.5 seconds in CI/dev environments

#### Scenario: CLI refresh completes within budget

- **WHEN** running `refresh --json` against a stub connector
- **THEN** execution completes under 0.5 seconds and returns exit code 0
