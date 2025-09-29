## Why

Before building the UI, the team needs developer utilities to populate caches, build features, render early artifacts, and validate health. A first-class CLI enables deterministic, non-interactive workflows in CI and local dev, aligned with the architecture's CLI plan.

## What Changes

- Add a CLI entrypoint with four commands: `refresh`, `features`, `render`, `validate`.
- Provide global options: `--offline`, `--cache-root`, `--log-level`, `--json`, `--no-interactive`.
- Wire to the existing `Repository`, registry loader, and exporters to produce deterministic artifacts (Parquet/CSV/JSON) with source manifests.
- Enforce fail-fast on schema/computation errors; degrade gracefully on connector errors with stale caches.
- Emit structured logs and stable exit codes for CI.

## Impact

- Affected specs: `cli`.
- Affected code (planned): `src/west_housing_model/cli/main.py`, integrations in `data/repository.py`, `config/registry_loader.py`, exporters, and minimal docs.
- Tests: new `tests/cli/` covering command behaviors (dry-run fixtures, offline, exit codes, JSON output).
