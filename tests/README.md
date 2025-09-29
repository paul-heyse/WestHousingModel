# Testing Overview

## Matrix

| Layer        | Purpose                                                        | Key Suites                                  |
|--------------|----------------------------------------------------------------|---------------------------------------------|
| Unit         | Deterministic logic (connectors, logging, feature builders)    | `tests/test_repository_logging.py`, `tests/test_acs_connector.py`, `tests/data/test_*` |
| Integration  | Repository/CLI/UI flows, cache TTL/offline, logging, concurrency| `tests/integration/test_repository_integration.py`, `tests/integration/test_cli_contracts.py`, `tests/integration/test_logging_integration.py`, `tests/integration/test_ui_smoke.py`, `tests/integration/test_performance_smoke.py` |
| Golden       | Snapshot scenarios covering feature + valuation pipelines      | `tests/test_golden_pipeline.py`, `tests/integration/test_feature_pipeline.py`, `tests/integration/test_valuation_integration.py`, `tests/test_cli_golden.py` |

All layers are required for changes that touch connectors, repository, or valuation logic.

## Fixture & Factory Strategy

Shared data factories live in `tests/factories.py` and are exposed through `pytest` fixtures in `tests/conftest.py`. Use them to obtain canonical place/site/ops datasets, hazards payloads, and scenario dictionaries. The `temp_cache_dir` fixture isolates repository cache state by pointing `WEST_HOUSING_MODEL_CACHE_ROOT` at a temporary directory.

Guidelines:

- Prefer fixtures over ad-hoc CSV strings to keep inputs consistent.
- Extend factories when adding new datasets so golden tests stay centralized.
- When testing failure capture, override `WEST_HOUSING_MODEL_FAILURE_CACHE` with `monkeypatch` and assert saved payloads.

## Test Plan & Commands

- Run full suite: `pytest -q`
- Lint tests: `ruff check tests`
- Format updates: `black tests`
- Golden snapshots are plain JSON/CSV checked into `tests/data/golden/`; update expectations deliberately and review diffs.
- Performance smoke test: `PERF_SMOKE_THRESHOLD=5.0 PERF_SMOKE_REPORT=perf-smoke-report.json pytest -m performance` checks the representative end-to-end pipeline stays within budget and writes a JSON artifact consumed by CI for trend analysis.
- Integration entrypoints: `pytest tests/integration -q` (fast <1s) for repository/CLI/UI smoke. Performance tests assert sub-second execution on dev hardware.

New test suites should stay under ~1s locally. If you introduce heavier workflows, mark them with `@pytest.mark.slow` and gate behind an env flag.
