## ADDED Requirements

### Requirement: Deal Quality Scoring

The system SHALL compute Deal Quality (0..100) as Returns minus Penalties (hazard, supply, affordability, data confidence) using explicit, configurable mapping tables.

#### Scenario: Returns mapping

- **WHEN** YoC, IRR, DSCR are provided
- **THEN** the system SHALL map each to 0..100 via default tables and combine via weights (0.45,0.35,0.20).

#### Scenario: Hazard penalties

- **WHEN** hazard flags/values exceed thresholds (e.g., in_sfha, wildfire percentile, PGA, winter events)
- **THEN** the system SHALL subtract configured penalty points (bounded).

#### Scenario: Supply penalty

- **WHEN** permits per 1k HH ≥ thresholds
- **THEN** the system SHALL subtract mapped penalty points.

#### Scenario: Affordability guardrail

- **WHEN** rent-to-income exceeds threshold and not overridden
- **THEN** the system SHALL subtract penalty; the system SHALL record a note if overridden.

#### Scenario: Data confidence

- **WHEN** required features are missing or stale
- **THEN** the system SHALL subtract a data-confidence penalty.

#### Scenario: Clamping

- **WHEN** total exceeds 100 or drops below 0
- **THEN** the system SHALL clamp result to [0,100].

#### Scenario: Determinism

- **WHEN** inputs repeat
- **THEN** outputs SHALL be identical.
