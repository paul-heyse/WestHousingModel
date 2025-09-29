## ADDED Requirements

### Requirement: Performance Smoke Testing

Representative feature/valuation scenarios SHALL run under defined time thresholds, and CI SHALL surface performance regressions.

#### Scenario: Smoke test executes under threshold
- **WHEN** the performance smoke test runs locally or in CI
- **THEN** it SHALL fail if execution time exceeds the documented threshold (accounting for configured tolerance).

#### Scenario: Timing artifacts recorded
- **WHEN** the smoke test completes in CI
- **THEN** timing metrics SHALL be uploaded or printed for reviewers to compare against historical baselines.

#### Scenario: Documentation provided
- **WHEN** contributors review documentation
- **THEN** they SHALL find instructions for executing the smoke test, updating thresholds, and interpreting failures.
