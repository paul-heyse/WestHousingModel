## ADDED Requirements
### Requirement: Repository Skeleton Mirrors Architecture
The system SHALL provide a Python package skeleton that mirrors the layout defined in `architecture.md:397`, including top-level packages for config, core, data (with connectors/cache/repository/catalog), features, scoring, valuation, ui, cli, and utils.

#### Scenario: Developer inspects package layout
- **WHEN** a developer lists `src/west_housing_model/`
- **THEN** they observe directories named `config`, `core`, `data`, `features`, `scoring`, `valuation`, `ui`, `cli`, and `utils`, each containing an `__init__.py` file.

### Requirement: Core Entities Implemented as Dataclasses
The system SHALL define dataclasses for Place, Property, and Scenario in the `core/` package, capturing the identifiers, attributes, and relationships detailed in `architecture.md:64`, and exposing typed enums for geo levels and hazard context.

#### Scenario: Core entity definitions are imported
- **WHEN** another module imports `Place`, `Property`, or `Scenario` from `west_housing_model.core.entities`
- **THEN** the import succeeds and each class exposes the fields described in `architecture.md:64`, including IDs, geo metadata, and provenance manifests.

### Requirement: Shared Utilities Available for Geometry and Logging
The system SHALL expose utility modules under `utils/` that cover geometry helpers (distance calculations, coordinate normalization) and structured logging as described in `architecture.md:421`, suitable for reuse across connectors, features, and the UI.

#### Scenario: Feature builder requests helpers
- **WHEN** a feature builder module imports `west_housing_model.utils.geometry` or `west_housing_model.utils.logging`
- **THEN** helper functions/classes exist to compute distances and emit structured logs with fields `timestamp`, `level`, `module`, `action`, and optional `source_id` context.
