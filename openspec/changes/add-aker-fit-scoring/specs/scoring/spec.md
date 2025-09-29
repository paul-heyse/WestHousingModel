## ADDED Requirements

### Requirement: Aker Fit Scoring

The system SHALL compute Aker Fit (0..100) from four pillar indices (each in [0..1]) using percentile-normalized components and configurable pillar weights.

#### Scenario: Default weights equal

- **WHEN** pillar indices are provided with no weights
- **THEN** the system SHALL use equal weights (0.25 each) and output integer 0..100.

#### Scenario: Custom weights sum to 1

- **WHEN** weights are provided that sum to 1
- **THEN** the system SHALL compute a weighted mean of pillars and scale to 0..100.
- **AND** the system SHALL clamp the final score to [0,100] and round to nearest int.

#### Scenario: Missing pillars handled

- **WHEN** a pillar is missing or NA
- **THEN** it SHALL be treated as 0.0 in the weighted sum.

#### Scenario: Determinism

- **WHEN** inputs repeat
- **THEN** outputs SHALL be identical.

#### Scenario: Validation

- **WHEN** inputs are outside [0,1]
- **THEN** the system SHALL clamp each pillar to [0,1] before aggregation and SHALL reject non-numeric inputs.
