## Why

The CLI (`west-housing-model`) exposes JSON responses for refresh/validate/features/render commands. As we expand logging metadata and repository outputs, response shapes can change silently, breaking downstream scripts or user automation. We lack automated contract tests to snapshot CLI JSON outputs and warn reviewers about breaking changes. Introducing CLI snapshot tests will make these changes explicit and reduce regressions.

## What Changes

- Add snapshot-based tests (e.g., `pytest` + `textual-snapshot` or `snapshottest`) for key CLI commands, capturing JSON responses for representative inputs.
- Provide tooling to update snapshots intentionally (similar to golden data guard) with reviewer-visible diffs.
- Document the contract-testing process and integrate snapshot refresh commands into developer workflow.
- Optionally add schema validation for CLI JSON outputs to ensure required fields persist.

## Impact

- **Affected specs**: testing/CLI coverage update.
- **Affected code**: new tests under `tests/cli/test_contracts_snapshot.py`, snapshot artifacts under `tests/snapshots/`, and CLI code adjustments if snapshots reveal inconsistent fields.
- **Documentation**: README/tests guide to explain snapshot refresh process and contract guarantees.
