## ADDED Requirements

### Requirement: Read-Through Cache Repository

The system SHALL provide a repository that fronts data connectors with a read-through cache using Parquet/GeoParquet artifacts and a SQLite index.

#### Scenario: Fresh cache hit

- **WHEN** a request is made with a key whose cached artifact is within `cache_ttl_days`
- **THEN** the repository SHALL return the cached dataset without invoking the connector.

#### Scenario: Cache miss or expired

- **WHEN** no cached artifact exists or it is expired
- **THEN** the repository SHALL invoke the connector, validate the result, persist the artifact, update the index, and return the result.

#### Scenario: Network failure with stale cache

- **WHEN** the connector fails and a stale cached artifact exists
- **THEN** the repository SHALL return the stale dataset and mark the status as `stale`.

#### Scenario: Network failure without cache

- **WHEN** the connector fails and no cached artifact exists
- **THEN** the repository SHALL raise an explicit error identifying the `source_id` and key.

## ADDED Requirements

### Requirement: Repository Read‑Through Cache

The system SHALL provide a repository façade that mediates all connector reads via a read‑through cache backed by a SQLite index and Parquet/GeoParquet artifacts.

#### Scenario: Cache hit returns fresh artifact

- **WHEN** a connector request is made with parameters that map to an existing, non‑expired cache entry
- **THEN** the repository SHALL return the cached DataFrame without network calls
- **AND** include `{source_id, as_of}` provenance

#### Scenario: Cache miss fetches, validates, persists, and returns

- **WHEN** a connector request is made with parameters that have no fresh cache entry
- **THEN** the repository SHALL invoke the connector, validate schema, persist Parquet/GeoParquet
- **AND** upsert the SQLite index with `created_at, as_of, ttl_days, rows, schema_version`
- **AND** return the resulting DataFrame

### Requirement: Offline Mode (Stale‑OK)

The system SHALL support an offline mode where stale cache entries may be returned when the network is unavailable or disabled.

#### Scenario: Offline returns latest stale artifact with status

- **WHEN** offline mode is enabled or a network failure occurs
- **AND** a stale cache artifact exists for the request
- **THEN** the repository SHALL return the stale DataFrame with a `stale=True` status propagated to the caller/UI

#### Scenario: Offline with no cache raises clear error

- **WHEN** offline mode is enabled or network fails
- **AND** no cache artifact exists for the request
- **THEN** the repository SHALL raise a clear error indicating data is unavailable offline

### Requirement: Failure Logging & Schema Drift

The system MUST capture connector failures and schema drift for diagnosis.

#### Scenario: Network or connector error with prior cache

- **WHEN** a connector fetch fails
- **AND** a prior cache artifact exists
- **THEN** the repository SHALL return the stale DataFrame and log failure metadata under `cache/failures/<source_id>/...`

#### Scenario: Schema drift detected

- **WHEN** the connector output does not match the expected schema
- **THEN** the system SHALL save the raw payload to `cache/failures/<source_id>/...` and raise a clear error with mitigation steps
