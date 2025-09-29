## ADDED Requirements

### Requirement: Scenario Save/Load & Manifest

The system SHALL save and load scenarios consisting of user overrides and a `source_manifest` capturing data vintages.

#### Scenario: Locked vintage

- **WHEN** the user enables “Lock to vintage” and saves a scenario
- **THEN** loading the scenario reuses the embedded manifest for computations even if newer cache entries exist

### Requirement: Version Compatibility

The system SHALL include a spec version in scenario files and attempt a safe migration for minor changes.

#### Scenario: Minor version bump

- **WHEN** a scenario with `spec_version = 1.1` is loaded by a `1.2` application
- **THEN** the system runs a no‑op migration and warns only if fields are deprecated

### Requirement: Drift Warning

The system SHALL warn when a scenario saved without lock is re‑run under newer `as_of` values.

#### Scenario: Unlocked scenario drift

- **WHEN** a user loads an unlocked scenario and sources have newer `as_of`
- **THEN** the UI shows a “Newer data available” banner with an option to re‑lock to current manifest
