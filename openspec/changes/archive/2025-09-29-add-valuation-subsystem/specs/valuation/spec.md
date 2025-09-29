## ADDED Requirements

### Requirement: Valuation Data Contracts

Valuation SHALL accept a strict input contract and emit a canonical output.

Inputs (contract): a dict-like object containing:

- `scenario_id` (uuid str), `property_id` (str), `as_of` (YYYY-MM)
- `features.place` (row for the property place context) with at least: `aker_market_fit:int`, `msa_jobs_t12:float`, `msa_jobs_t36:float`, `permits_5plus_per_1k_hh_t12:float`
- `features.site` with at least: `in_sfha:bool|null`, `wildfire_risk_percentile:int|null`, `pga_10in50_g:float|null`, `hdd_annual:float|null`, `cdd_annual:float|null`
- `features.ops` with at least: `utility_rate_note:str|null`, `broadband_gbps_flag:bool|null`
- `user_overrides` including: unit mix, current/target rent, base OpEx $/unit/yr, capex plan buckets, leverage (LTV/rate), cap rate band, flags/toggles

Outputs (canonical table `valuation_outputs`):

- Keys: `scenario_id`, `property_id`, `as_of`
- Columns (subset): `noistab:float`, `cap_rate_low/base/high:float`, `value_low/base/high:float`,
  `yoc_base:float`, `irr_5yr_low/base/high:float`, `dscr_proxy:float`,
  `insurance_uplift:float`, `utilities_scaler:float`, `aker_fit:int`, `deal_quality:int`,
  `sensitivity_matrix:json`, `source_manifest:json`

#### Scenario: Validate contracts

- **WHEN** the orchestrator receives inputs
- **THEN** schemas SHALL be validated; missing/invalid fields raise a SchemaError with context

#### Scenario: Deterministic output

- **WHEN** inputs are identical
- **THEN** outputs SHALL be identical bit-for-bit, including sensitivity entries

### Requirement: Rent Baseline

The system SHALL compute a rent baseline per unit type using a market level (e.g., ZORI) with a constrained uplift from Urban Convenience.

#### Scenario: Baseline from market level

- **WHEN** `zori_level` is provided for the market
- **THEN** baseline rent per unit type derives from `zori_level` with simple type multipliers

#### Scenario: UC uplift with cap

- **WHEN** `aker_market_fit` or the UC pillar percentile is available
- **THEN** apply an uplift capped at +1.5% for UC ≥ p75; linear steps below (see mapping)

#### Scenario: Affordability guardrail

- **WHEN** implied rent-to-income exceeds the guardrail (default 35%)
- **THEN** cap baseline until within guardrail unless an override is provided (override recorded)

### Requirement: Growth Module

The system SHALL compute rent growth for yrs 2–5 from jobs momentum net of supply pressure, with caps and reversion.

#### Scenario: Jobs minus supply formula

- **WHEN** `msa_jobs_t12`, `msa_jobs_t36`, and `permits_5plus_per_1k_hh_t12` are present
- **THEN** compute `growth = g_base + f_jobs(...) − f_supply(...)` with tunable mapping tables

#### Scenario: Caps and reversion

- **WHEN** growth exceeds configured caps/floors
- **THEN** clamp values; after year 5 revert towards long-run trend

### Requirement: OpEx & Insurance Adjustments

The system SHALL adjust base OpEx using utilities and hazard context and surface explicit insurance uplifts.

#### Scenario: Utilities scaler

- **WHEN** `hdd_annual` and `cdd_annual` are present
- **THEN** compute a utilities scaler as a linear function vs US median; apply to base OpEx

#### Scenario: Hazard premiums

- **WHEN** `in_sfha`, `wildfire_risk_percentile`, or high `pga_10in50_g` are present
- **THEN** add mapped insurance uplifts per the rulebook and record a line item

#### Scenario: Winter line

- **WHEN** winter events are high (proxy via storm events peer percentile)
- **THEN** add a small fixed winter line to OpEx; record in outputs

### Requirement: Capex & Contingencies

The system SHALL accept a capex plan and apply hazard contingencies.

#### Scenario: Timing buckets

- **WHEN** capex buckets are specified (interiors, exterior/common, systems)
- **THEN** spread spending across yrs 0–3 per default schedule unless overridden

#### Scenario: Hazard contingencies

- **WHEN** hazard context warrants (e.g., flood/seismic)
- **THEN** add a contingency percent to relevant buckets and reflect in cash flows

### Requirement: DCF & Sensitivity Grid

The system SHALL compute a 10-yr DCF with reversion and a 3×3 sensitivity grid.

#### Scenario: DCF and value band

- **WHEN** base inputs are provided
- **THEN** compute NOI projection, apply cap rate band to produce `value_low/base/high`

#### Scenario: Sensitivity grid

- **WHEN** sensitivity toggles are enabled
- **THEN** compute a 3×3 matrix for rent (±5%), cap (±50 bps), insurance (±20%) and embed JSON

### Requirement: Orchestration & Provenance

The orchestrator SHALL compose modules in order and attach a manifest and module-level provenance.

#### Scenario: Composition order

- **WHEN** orchestrating a run
- **THEN** run: rent baseline → growth → OpEx/insurance → capex → DCF → sensitivity; abort on SchemaError

#### Scenario: Manifest and provenance

- **WHEN** outputs are generated
- **THEN** attach `source_manifest` of (source_id→as_of) and per-module provenance notes

### Requirement: CLI Render

The CLI SHALL expose a command to render valuation for a small Scenario JSON.

#### Scenario: CLI success

- **WHEN** `render --scenario tests/data/scenario_small.json` is invoked
- **THEN** it prints a summary line with value band and writes a Parquet/JSON output in a temp folder
