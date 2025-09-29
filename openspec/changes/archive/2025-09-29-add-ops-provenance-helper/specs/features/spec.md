## MODIFIED Requirements

### Requirement: Ops Feature Builders

The system SHALL provide pure, deterministic functions to compute site-level operational context features and emit provenance metadata.

#### Scenario: Utilities and broadband mapping
- **WHEN** EIA v2 and FCC BDC inputs are provided
- **THEN** the builder SHALL map inputs to typed ops feature columns (utilities note/scaler, `broadband_gbps_flag`), validate with Pandera, and return provenance that includes `source_id`, `as_of`, and transformation notes.

#### Scenario: Zoning context note
- **WHEN** optional zoning inputs exist
- **THEN** the builder SHALL map to `zoning_context_note`, validate outputs, and record provenance for the optional field.

#### Scenario: Missing optional inputs
- **WHEN** optional utilities/broadband/zoning inputs are absent
- **THEN** the builder SHALL surface `pd.NA` for the feature columns and include provenance indicating the absence (e.g., `source_id` remains the ops feature namespace with `as_of = None`).

#### Scenario: CLI feature export
- **WHEN** the CLI `features --ops` command runs
- **THEN** it SHALL persist both the ops feature Parquet and the associated provenance sidecar so downstream manifests can include the ops lineage.
