## ADDED Requirements

### Requirement: Schema Validation with Pandera

All connector outputs and feature builder inputs/outputs SHALL be validated against Pandera schemas at function boundaries. Violations MUST raise `SchemaError` and include the `source_id` or feature name in the message.

#### Scenario: Connector output schema mismatch

- **WHEN** a connector returns a DataFrame missing a required column
- **THEN** the system SHALL raise `SchemaError` and capture the raw payload under `data/cache/failures/{source_id}/…`.

#### Scenario: Feature builder input invalid

- **WHEN** a feature builder receives an input frame with wrong dtypes
- **THEN** a `SchemaError` SHALL be raised before any transformation is applied.

### Requirement: Fail-Fast Error Policy

The system SHALL fail fast on `SchemaError` and `ComputationError`, and degrade gracefully on `ConnectorError` if a stale cache is available.

#### Scenario: Degrade gracefully with stale cache

- **WHEN** a network fetch fails for a source with a non-expired cached artifact
- **THEN** the repository SHALL return the cached data with a `stale` status to the UI.
