## ADDED Requirements

### Requirement: Source Registry Files

The system SHALL provide a canonical, git-tracked source registry under `config/sources.yml` and `config/sources_supplement.yml`. Each source entry MUST include fields: `id`, `enabled`, `endpoint`, `geography`, `cadence`, `cache_ttl_days`, `license`, `rate_limit`, `auth_key_name` (optional), and `notes`. The supplement MAY add new sources or override fields for existing sources; merge order is `sources.yml` then `sources_supplement.yml` by `id` (last-one-wins per field).

#### Scenario: Registry files present

- **WHEN** the application starts
- **THEN** the registry loader SHALL locate both files and parse them in order: base then supplement.

#### Scenario: Missing required field

- **WHEN** any required field (except `auth_key_name`) is missing in a source entry
- **THEN** validation SHALL fail with an explicit error naming the `source_id` and missing field.

#### Scenario: Unknown field

- **WHEN** a source entry contains an unknown field
- **THEN** the system SHALL log a warning and continue parsing.
