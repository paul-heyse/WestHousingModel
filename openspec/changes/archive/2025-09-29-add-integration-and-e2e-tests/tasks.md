## 1. Scoping & Fixture Prep

- [x] 1.1 Inventory existing tests, identify integration gaps per architecture layers.
- [x] 1.2 Define shared fixtures/factories and golden inputs for integration suites.
- [x] 1.3 Select end-to-end scenarios covering online/offline, TTL expiry, schema drift, concurrency, UI smoke, and performance.

## 2. Repository & Connector Integration

- [x] 2.1 Add tests for read-through cache population and fresh cache hits with structured logging assertions.
- [x] 2.2 Cover TTL expiry, offline mode, failure capture, and schema drift payload logging.
- [x] 2.3 Add per-source concurrency lock test ensuring single artifact and shared cache metadata.
- [x] 2.4 Extend repository failure handling to persist JSON samples on schema errors.

## 3. CLI Contract Coverage

- [x] 3.1 Implement CLI tests for `refresh --json` (online/offline) verifying payload structure and logs.
- [x] 3.2 Implement `features` CLI test writing canonical Parquet outputs from sample CSVs.
- [x] 3.3 Implement `render --json` contract test ensuring valuation output and manifest manifesting.
- [x] 3.4 Add `validate --json` contract test and ensure deterministic exit codes.

## 4. Feature & Valuation Golden Integration

- [x] 4.1 Add integration tests comparing place/site/ops features against golden snapshots (with typed normalization).
- [x] 4.2 Capture ops provenance golden and assert against integration output.
- [x] 4.3 Add valuation integration golden test verifying manifest & snapshot alignment.

## 5. UI, Export, & Performance Smokes

- [x] 5.1 Add Streamlit page smoke test with stubbed `streamlit` module to ensure imports execute.
- [x] 5.2 Assert exporters embed manifests via integration test.
- [x] 5.3 Add performance smoke tests for place feature build and CLI refresh (<0.5s budgets).

## 6. Documentation & Validation

- [x] 6.1 Update `tests/README.md` with integration matrix and workflow notes.
- [x] 6.2 Run `pytest -q` and `pytest tests/integration -q` locally.
- [x] 6.3 Run `openspec validate add-integration-and-e2e-tests --strict`.
