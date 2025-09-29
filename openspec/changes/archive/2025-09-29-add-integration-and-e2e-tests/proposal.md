## Why

- Regression surface has expanded across repository cache, CLI, valuation, UI, and exports.
- Need deterministic, automated coverage that catches contract drift, schema changes, and performance regressions before shipping.

## What Changes

- Build a layered integration suite (`tests/integration/`) covering repository caching (fresh/stale/TTL/offline/failure logging) with concurrency lock assertions.
- Add CLI contract tests for `refresh`, `validate`, `features`, and `render`, validating JSON payloads, exit codes, and structured logs.
- Introduce feature/valuation golden integration tests sharing data fixtures with pipeline unit tests.
- Add Streamlit/UI smoke tests using stubbed `streamlit`, plus exporter manifest assertions.
- Add performance smoke tests for key pathways (place feature build, CLI refresh) with sub-second budgets.
- Document integration coverage & golden refresh workflow in `tests/README.md` and update OpenSpec testing spec.

## Impact

- Specs: `specs/testing/spec.md` (new integration requirements).
- Code: `tests/integration/`, existing golden tests, repository failure handling, ops feature provenance, docs.
- Tooling: pytest suite organization; CI runtime (still under existing budget).
