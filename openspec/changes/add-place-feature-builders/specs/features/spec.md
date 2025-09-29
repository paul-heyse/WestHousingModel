## ADDED Requirements

### Requirement: Place Feature Builders

The system SHALL provide pure, deterministic functions to compute place-level pillar features and percentiles from connector outputs.

#### Scenario: Deterministic transformation with validation

- **WHEN** normalized connector tables (ACS income, BLS jobs, BPS permits, FCC broadband, PAD-US acres, OSM/Routes access) are provided
- **THEN** the builder SHALL validate inputs with Pandera and produce a typed DataFrame matching the place feature schema
- **AND** write a provenance sidecar describing `{source_id, as_of, transformation}` per output column

#### Scenario: Percentile normalization by peer group

- **WHEN** a peer group is specified (regional|national)
- **THEN** pillar components SHALL be normalized to indices and aggregated into pillar scores (0..1)
