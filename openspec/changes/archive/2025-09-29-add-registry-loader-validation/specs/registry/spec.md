## ADDED Requirements

### Requirement: Registry Loader & Merge

The system SHALL provide a registry loader that reads `config/sources.yml` and `config/sources_supplement.yml`, merges entries by `id` (supplement overrides base), and returns a validated list of sources.

#### Scenario: Successful load and merge

- **WHEN** both files are present and parseable
- **THEN** the loader SHALL validate required fields and merge duplicates by `id` with last-one-wins behavior.

#### Scenario: Unknown field warning

- **WHEN** an entry includes unknown fields
- **THEN** the loader SHALL warn and proceed.

#### Scenario: Missing required field error

- **WHEN** an entry omits a required field (`id`, `enabled`, `endpoint`, `geography`, `cadence`, `cache_ttl_days`, `license`, or `rate_limit`)
- **THEN** the loader SHALL raise `RegistryError` identifying the `source_id` and the missing field.

### Requirement: Data Dictionary Output

The loader SHALL produce a data dictionary suitable for the Settings UI, including for each source: `id`, `geography`, `cadence`, `cache_ttl_days`, `license`, and `notes`.

#### Scenario: Dictionary available to UI

- **WHEN** the UI requests registry metadata
- **THEN** the system SHALL return the data dictionary derived from the active registry entries.
