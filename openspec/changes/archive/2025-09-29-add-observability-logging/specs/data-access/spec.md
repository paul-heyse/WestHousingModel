## ADDED Requirements

### Requirement: Structured Repository Observability

The repository SHALL emit structured logging and explicit stale/fresh indicators for every connector invocation, enabling downstream consumers to trace cache behavior and diagnose failures.

#### Scenario: Fresh cache hit logged

- **WHEN** a request is served from a fresh cache artifact
- **THEN** the system SHALL emit a structured log with `status=fresh`, `source_id`, `cache_key`, and `latency_ms`
- **AND** the `RepositoryResult` SHALL expose the same status metadata to callers.

#### Scenario: Stale fallback logged with correlation id

- **WHEN** the repository returns stale data due to connector failure or offline mode
- **THEN** the log entry SHALL include `status=stale`, the correlation id, failure reason, and cache artifact path
- **AND** the failure capture SHALL append the correlation id to the saved payload metadata.

#### Scenario: Connector error without cache

- **WHEN** no cache exists and a connector raises an error
- **THEN** the repository SHALL emit an ERROR-level log containing the connector context, correlation id, and guidance for remediation.
