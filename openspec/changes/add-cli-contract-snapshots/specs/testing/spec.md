## ADDED Requirements

### Requirement: CLI Contract Snapshots

Key CLI commands SHALL have snapshot-based contract tests to detect breaking changes in JSON responses.

#### Scenario: Snapshot tests cover CLI JSON
- **WHEN** CLI contract tests run
- **THEN** they SHALL compare actual JSON output to committed snapshots and fail on differences unless snapshots are intentionally updated.

#### Scenario: Snapshot workflow documented
- **WHEN** contributors need to update CLI contracts
- **THEN** documentation SHALL describe the snapshot update process and review expectations.
