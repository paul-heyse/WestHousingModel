## 1. Planning

- [ ] 1.1 Identify CLI commands and parameter combinations requiring contract snapshots.
- [ ] 1.2 Select snapshot tooling and decide on file locations/versioning strategy.

## 2. Implementation

- [ ] 2.1 Add snapshot tests for refresh/validate/features/render commands, covering success and error cases.
- [ ] 2.2 Provide developer tooling to update snapshots intentionally (e.g., `pytest --snapshot-update`).
- [ ] 2.3 Document contract expectations and snapshot workflow in tests/README.md.

## 3. Validation

- [ ] 3.1 Run snapshot tests locally and in CI to ensure deterministic results.
- [ ] 3.2 Confirm diffs are surfaced when snapshots change without approval.
- [ ] 3.3 Run `openspec validate add-cli-contract-snapshots --strict`.
