## 1. Planning

- [x] 1.1 Inventory existing Pandera schemas and identify gaps across connectors, feature builders, and valuation outputs.
- [x] 1.2 Decide on schema storage (single module vs. package) and validation helper API.

## 2. Implementation

- [ ] 2.1 Create shared schema utilities and enforce validation in repository/feature code paths.
- [ ] 2.2 Add `pytest` marker/session for schema validation and integrate with CI.
- [ ] 2.3 Update tests/golden fixtures to pass through schema checks and log coercions.
- [ ] 2.4 Add developer command/documentation for running schema checks and updating schemas.

## 3. Validation

- [ ] 3.1 Run schema validation pytest session locally and in CI.
- [ ] 3.2 Run full QA suite (ruff, black, mypy, pytest).
- [ ] 3.3 Run `openspec validate add-schema-validation-pipeline --strict`.
