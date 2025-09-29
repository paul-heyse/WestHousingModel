## ADDED Requirements

### Requirement: Explore Page

The system SHALL provide an Explore page with a place/site table and a lightweight map, supporting filters and region quick toggles.

#### Scenario: Filter and toggle interaction

- **WHEN** the user adjusts Aker Fit and hazard filters or toggles CO/UT/ID
- **THEN** the table updates within 200ms and the map layer refreshes within 500ms

### Requirement: Evaluate Page

The system SHALL provide an Evaluate page showing inputs on the left and outputs on the right, including features, scores, valuation, and a sensitivity grid.

#### Scenario: Recompute on input change

- **WHEN** the user edits target rent, OpEx, or capex plan
- **THEN** valuation recomputes deterministically and updates outputs in ≤500ms on a typical laptop for a single property

### Requirement: Scenarios Page

The system SHALL provide a Scenarios page to save/load scenarios and show the data vintage manifest.

#### Scenario: Save and reload scenario

- **WHEN** the user saves a scenario and reloads it later
- **THEN** the UI restores all overrides and re-runs computations using the same manifest when locked, or current sources when unlocked

### Requirement: Settings Page

The system SHALL provide a Settings page with a registry viewer, refresh status, pillar weights, and optional API keys.

#### Scenario: Registry viewer

- **WHEN** the user opens Settings
- **THEN** the UI shows active sources with `as_of`, TTL status (Fresh/Stale), and notes from the registry

### Requirement: Provenance Tooltips

The system SHALL show provenance tooltips for material numbers using sidecar metadata, including `source_id`, `as_of`, and a short transformation note.

#### Scenario: Tooltip content

- **WHEN** the user hovers over a value with an (i) icon
- **THEN** a tooltip shows the contributing `source_id(s)`, `as_of`, and transformation summary

### Requirement: Offline and Stale Indicators

The system SHALL surface offline mode and stale cache states in the UI.

#### Scenario: Offline mode with stale cache

- **WHEN** the repository returns cached data with `is_stale=True` and offline mode is enabled
- **THEN** the UI displays a badge “Stale (Offline)” and disables refresh actions

### Requirement: Performance & Caching

The system SHALL cache expensive data calls within the session and keep interactions responsive.

#### Scenario: Responsive filtering

- **WHEN** the user changes filters on Explore
- **THEN** results update within the stated latency budgets and no network fetch occurs if repository reports fresh cache
