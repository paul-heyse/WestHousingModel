## ADDED Requirements

### Requirement: Site Feature Builders

The system SHALL provide pure, deterministic functions to compute site-level hazard and proximity features from connector outputs.

#### Scenario: Flag computation with provenance

- **WHEN** hazard connector frames are provided (FEMA, USFS, USGS, NOAA)
- **THEN** the builder SHALL compute flags/values (e.g., `in_sfha`, `wildfire_risk_percentile`, `pga_10in50_g`), validate with Pandera, and emit a provenance sidecar

#### Scenario: Proximity flags

- **WHEN** proximity inputs are provided
- **THEN** the builder SHALL compute boolean flags and distances as typed columns, validated and recorded in provenance
