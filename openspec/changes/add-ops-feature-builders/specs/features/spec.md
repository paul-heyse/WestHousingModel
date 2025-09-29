## ADDED Requirements

### Requirement: Ops Feature Builders

The system SHALL provide pure, deterministic functions to compute site-level operational context features.

#### Scenario: Utilities and broadband mapping

- **WHEN** EIA v2 and FCC BDC inputs are provided
- **THEN** the builder SHALL map inputs to typed ops feature columns (utilities notes/scaler, `broadband_gbps_flag`), validate with Pandera, and emit provenance

#### Scenario: Zoning context note

- **WHEN** optional zoning inputs exist
- **THEN** the builder SHALL map to `zoning_context_note` with validation and provenance
