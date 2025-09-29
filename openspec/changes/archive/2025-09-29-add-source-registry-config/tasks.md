## 1. Implementation

- [x] 1.1 Create `config/sources.yml` with representative entries (e.g., `bls_timeseries`, `census_acs`, `census_bps`, `zillow_research`, `fema_nfhl`).
- [x] 1.2 Create `config/sources_supplement.yml` for optional/commercial/overrides; keep all entries disabled by default.
- [x] 1.3 Add inline comments describing each field; ensure no secrets or tokens are present.
- [x] 1.4 Add a brief README note in `config/` explaining how to extend and the merge order.

## 2. Validation

- [x] 2.1 Run `openspec validate add-source-registry-config --strict` and resolve any formatting issues.
