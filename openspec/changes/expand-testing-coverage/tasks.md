## 1. Planning

- [x] 1.1 Audit existing unit/integration/golden coverage against architecture testing matrix.
- [x] 1.2 Define fixture strategy (factories for connectors, repository, feature builders) and document in tests README.
- [x] 1.3 Update test plan outlining new suites, data sources, and expected run time.

## 2. Implementation

- [x] 2.1 Add unit tests for repository logging, correlation IDs, and connector error pathways.
- [x] 2.2 Expand connector tests (ACS, wildfire, design maps) with edge-case payloads and schema drift assertions.
- [x] 2.3 Create integration tests covering CLI refresh/validate, offline fallback, and structured log assertions.
- [x] 2.4 Introduce golden datasets for place/site/ops features and valuation output snapshots.
- [x] 2.5 Refactor shared fixtures/factories to reduce duplication across tests.

## 3. Validation

- [x] 3.1 Ensure pytest matrix (unit/integration/golden) runs locally and in CI with acceptable duration.
- [x] 3.2 Update coverage reports and include in PR template.
- [x] 3.3 Document testing strategy updates in README/architecture appendices.
- [x] 3.4 Run full QA suite (ruff, mypy, black, pytest, openspec validate).
