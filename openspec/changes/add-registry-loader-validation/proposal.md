## Why

Before touching any external data, we need a robust registry loader that parses `config/sources.yml` (+ supplement), enforces required fields, warns on unknown fields, and produces a data dictionary for the UI (per `architecture.md:129`).

## What Changes

- Implement a `registry` module to load and merge `sources.yml` and `sources_supplement.yml`.
- Enforce required fields per source and validate enumerations (e.g., `geography`, `cadence`).
- Emit a data dictionary structure consumable by the Settings UI.
- Provide clear error/warning messages with `source_id` context.

## Impact

- Affected specs: registry
- Affected code: `src/west_housing_model/config/registry_loader.py` (new), `src/west_housing_model/config/__init__.py` (export), and a small `ui` contract for the data dictionary.
