## Why

We rely on Pandera schemas for datasets (place/site/ops features, repository outputs), but schema validation is opt-in and inconsistently applied. Several connectors (ACS, wildfire) run validations only in targeted tests, while feature builders and golden flows disable checks for performance. As we expand API coverage, unvalidated frames can silently introduce column drift, resulting in downstream runtime errors. We need an explicit schema validation pipeline that guarantees every critical dataset passes through a Pandera contract during CI and provides tooling to regenerate schema artifacts when the spec evolves.

## What Changes

- Centralise schema definitions (Pandera or Pydantic models) for repository outputs, feature builders, valuation inputs/outputs, and ensure the repository enforces validation before caching.
- Add a dedicated pytest session (`pytest -m schema_validation`) that runs fast contractual checks on representative frames, including golden fixtures, to detect drift early.
- Introduce a `schema validate` CLI/Make target that developers can run locally to verify new datasets and regenerate auto-documented schemas if needed.
- Update connectors and feature builders to call validation helpers by default (with explicit opt-outs for performance-critical contexts), logging any coerced values or schema adjustments.
- Document schema governance in architecture/testing appendices, including how to amend schemas, approval process, and updating golden data when columns change.

## Impact

- **Affected specs**: testing/schema governance updates.
- **Affected code/config**:
  - Shared validation utilities (likely under `west_housing_model/data/schemas.py`) for reuse.
  - Repository and feature modules updated to call validators.
  - Tests/goldens updated to exercise `pytest -m schema_validation` marker.
  - Documentation updates for new commands and schema lifecycle.
- **Dependencies**: Possibly upgrade Pandera or add Pydantic if we choose typed models; no runtime impact if optional.
