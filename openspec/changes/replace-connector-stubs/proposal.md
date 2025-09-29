## Why

Several connectors in `src/west_housing_model/data/connectors/` remain stub implementations that emit hard-coded payloads. These were placeholders during bootstrap phases, but they now violate both the archived connector specs (e.g., `add-hazards-and-context-sources`) and operational expectations: observability, caching, and tests assume real normalization, failure capture, and provenance handling. Stubs also mask schema drift and prevent end-to-end validation of API integrations. We need to replace all non-test stubs with production-ready connector implementations backed by proper request/normalize/validate pipelines so downstream features, scoring, and CLI tooling behave as specified.

## What Changes

- Audit every connector under `west_housing_model.data.connectors` and replace placeholder returns with full implementations that fetch (or load from fixtures in tests), normalize columns, apply Pandera schemas, and integrate with failure capture.
- Introduce shared utilities for HTTP requests, pagination, rate limiting, and inline fixture playback to support deterministic tests without reintroducing stubs.
- Update schema definitions and tests to reflect the new real connectors, including golden fixtures and repository integration coverage.
- Refresh documentation (architecture + connector specs) to note the removal of stubs and describe the new helper utilities.

## Impact

- Affected specs: connectors (multiple capabilities previously relying on stub behavior) require updates to reflect real fetch logic.
- Affected code: `src/west_housing_model/data/connectors/__init__.py`, new per-connector modules/mixins, repository tests, CLI integration tests.
- Tests: add fixture-backed connector tests, update repository cache tests, adjust golden snapshots to consume the normalized outputs.
