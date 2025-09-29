## ADDED Requirements

### Requirement: Census ACS Connector

The system SHALL provide a `census_acs` connector that fetches selected ACS tables for tract and MSA geographies, normalizes them to a typed DataFrame, and annotates outputs with `{source_id, as_of}`.

#### Scenario: Happy path fetch and normalize

- **WHEN** a request specifies a supported geography and time window
- **THEN** the connector SHALL fetch data, normalize columns, add `{source_id, as_of}`
- **AND** return a small, typed DataFrame matching the expected schema

#### Scenario: Read‑through caching via repository

- **WHEN** the same request repeats within TTL
- **THEN** the repository SHALL return the cached artifact without a network call

#### Scenario: Offline mode uses stale cache

- **WHEN** offline mode is enabled or network fails
- **AND** a stale artifact exists
- **THEN** the repository SHALL return the stale DataFrame and mark it `stale`

#### Scenario: Failure logging on network error

- **WHEN** the connector call fails (e.g., 5xx)
- **THEN** the system SHALL log failure context under `cache/failures/census_acs/`
- **AND** surface a clear error if no cache exists
