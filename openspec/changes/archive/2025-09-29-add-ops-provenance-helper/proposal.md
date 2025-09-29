## Why

The archived `add-ops-feature-builders` change established the deterministic `build_ops_features` helper, but it never emitted provenance metadata despite the requirement calling for provenance exposure. Downstream consumers (UI tooltips, exports, manifests) therefore cannot trace utilities or broadband context back to their underlying sources. We need to retrofit provenance emission so ops features match the architecture and spec expectations and integrate cleanly with the existing manifest tooling.

## What Changes

- Add an ops-specific provenance helper that surfaces `source_id`, `as_of`, and relevant transformation notes alongside the resulting DataFrame.
- Update `build_ops_features` (and its callers/tests) to return both the validated features frame and the provenance mapping.
- Thread provenance into CLI feature generation and golden pipeline fixtures so exports include the new metadata.
- Expand specs and tests to cover provenance behavior (including absence of optional fields).

## Impact

- Affected specs: features/ops (MODIFIED).
- Affected code: `src/west_housing_model/features/ops_features.py`, CLI features path, manifest tooling, ops feature tests/goldens.
- Tests: unit (ops provenance), CLI regression, golden pipeline update.
