## ADDED Requirements

### Requirement: Governance Documentation Baseline

The project SHALL maintain a Feature Dictionary, Rulebook, and ADR log documenting features, scoring rules, and architectural decisions.

#### Scenario: Feature dictionary published

- **WHEN** new features or metrics are added
- **THEN** the Feature Dictionary SHALL list name, description, source, units, and update cadence.

#### Scenario: Rulebook maintained

- **WHEN** scoring/valuation rules change
- **THEN** the Rulebook SHALL capture formulas, thresholds, and override policy before code merges.

#### Scenario: ADR logged

- **WHEN** architectural decisions with lasting impact are made
- **THEN** an ADR SHALL be recorded with context, decision, status, and references to affected specs/code.

#### Scenario: Governance checklist enforced

- **WHEN** changes touch features, rules, or architecture
- **THEN** PR/task checklists SHALL require confirmation that relevant governance docs are updated.
