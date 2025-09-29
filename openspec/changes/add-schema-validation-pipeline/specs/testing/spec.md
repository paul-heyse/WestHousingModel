## ADDED Requirements

### Requirement: Schema Validation Pipeline

All critical dataframes SHALL be validated against maintained schemas, and a dedicated CI step SHALL ensure schema compliance across connectors, feature builders, and valuation outputs.

#### Scenario: Repository and features enforce schemas
- **WHEN** repository or feature builders emit dataframes
- **THEN** they SHALL invoke shared schema validators that raise on missing/extra columns unless explicitly opted out (with a logged justification).

#### Scenario: CI schema validation session exists
- **WHEN** CI executes tests
- **THEN** a `pytest` session (or equivalent) SHALL run schema validation markers over representative datasets/golden fixtures and fail on schema drift.

#### Scenario: Developer tooling documented
- **WHEN** contributors review documentation
- **THEN** they SHALL find commands for running schema validation locally and guidance for updating schemas when business requirements change.
