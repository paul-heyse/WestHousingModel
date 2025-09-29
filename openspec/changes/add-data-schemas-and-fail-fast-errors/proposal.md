## Why

To ensure reliability and clarity from day one, connectors and feature builders must validate inputs/outputs against explicit schemas and fail fast on violations (per `architecture.md:557`). This guards against upstream drift and keeps outputs explainable.

## What Changes

- Introduce Pandera schemas for canonical tables (place/site features) and connector outputs.
- Add custom exceptions: `SchemaError`, `ConnectorError`, `ComputationError` with clear, user-actionable messages.
- Enforce schema checks at function boundaries in feature builders; connectors emit versioned schemas.
- Capture raw payloads on schema drift to `cache/failures/{source_id}/…` for debugging.

## Impact

- Affected specs: data-schemas, errors
- Affected code: `src/west_housing_model/core/exceptions.py`, `src/west_housing_model/data/catalog.py` (schemas), feature modules to apply checks.
