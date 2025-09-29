## Why
The codebase needs a concrete skeleton that matches the agreed architecture so subsequent capabilities can be implemented consistently and tested.

## What Changes
- Create the initial Python package layout (config/core/data/features/scoring/valuation/ui/cli/utils) mirroring the target structure in architecture.md:397.
- Define core domain entities (Place, Property, Scenario) and supporting enums in `core/` as dataclasses, matching architecture.md:64.
- Add shared helper modules for geometry utilities and structured logging in `utils/` as outlined at architecture.md:421.

## Impact
- Affected specs: architecture
- Affected code: src/west_housing_model/config, src/west_housing_model/core, src/west_housing_model/utils, package initialization files
