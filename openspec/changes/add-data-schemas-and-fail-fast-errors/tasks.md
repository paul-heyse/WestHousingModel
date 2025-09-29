## 1. Implementation

- [x] 1.1 Create `src/west_housing_model/core/exceptions.py` with `RegistryError`, `SchemaError`, `ConnectorError`, `ComputationError`, `CacheError`, `ExportError`.
- [x] 1.2 Define Pandera schemas in `src/west_housing_model/data/catalog.py` for canonical tables and connector outputs (initial subset sufficient for bootstrapping).
- [x] 1.3 Add validation calls at feature builder boundaries (place/site/ops) and in connectors.
- [x] 1.4 Implement failure capture path `data/cache/failures/{source_id}/…` when schema drift detected.

## 2. Tests

- [x] 2.1 Unit tests for schema pass/fail cases and exception messages.
- [x] 2.2 Integration test: simulate drift and assert raw payload capture + fail-fast behavior.

## 3. Validation

- [x] 3.1 Run `openspec validate add-data-schemas-and-fail-fast-errors --strict` and resolve issues.
