## Why

Current tests cover repository basics but lack structured assertions for logging, multi-connector workflows, and golden scenarios tying feature builders to valuation outputs. Architecture.md §17 calls for unit, integration, and golden coverage before rollout.

## What Changes

- Expand unit tests for connectors, repository logging, and feature builders to cover edge cases and failure paths.
- Add integration suites for CLI refresh/validate commands, offline fallback, and structured logging assertions.
- Introduce golden datasets for place/site/ops + valuation flows to detect regressions.
- Standardize test fixtures and data factories to reduce duplication and improve readability.

## Impact

- Affected specs: testing/coverage
- Affected code: `tests/` tree, `src/west_housing_model/tests` fixtures, QA automation scripts.
- Requires coordination with logging/governance changes to align expectations and documentation.
