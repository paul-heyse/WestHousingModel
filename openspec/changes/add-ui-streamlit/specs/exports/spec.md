## ADDED Requirements

### Requirement: One-Pager PDF Export

The system SHALL export a one‑page PDF summary including valuation outputs, scores, hazard badges, and a Sources & Vintages appendix.

#### Scenario: PDF includes manifest

- **WHEN** the user clicks Export PDF on Evaluate
- **THEN** the generated PDF embeds the scenario `source_manifest` and lists `source_id`/`as_of` pairs in an appendix

### Requirement: CSV Export

The system SHALL export a CSV with feature row(s), valuation outputs, scores, and the manifest serialized in a `source_manifest` column.

#### Scenario: Deterministic columns

- **WHEN** a scenario is exported to CSV
- **THEN** the column order and names match the documented schema and remain stable across runs for the same version

### Requirement: Deterministic Filenames

The system SHALL name exports deterministically using `scenario_id`, `as_of`, and a short content tag.

#### Scenario: Filename format

- **WHEN** the user exports PDF or CSV
- **THEN** filenames follow `valuation-{scenario_id}-{as_of}-onepager.pdf` and `valuation-{scenario_id}-{as_of}.csv`
