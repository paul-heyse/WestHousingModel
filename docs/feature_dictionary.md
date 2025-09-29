# Feature Dictionary

This document catalogs core feature tables, selected columns, and provenance.

## place_features

- place_id (str) — key
- aker_market_fit (int) — score 0..100; source: computed from pillars
- pillar_uc, pillar_oa, pillar_ij, pillar_sc (float 0..1) — computed percentiles
- broadband_gbps_flag (bool) — source: `fcc_bdc`; as_of: semiannual
- public_land_acres_30min (float acres) — source: `pad_us`; as_of: annual

Provenance: each column lists `source_id` and `as_of` month where applicable; computed columns include a transformation note.

## site_features

- property_id (str) — key
- in_sfha (bool) — source: `fema_nfhl`
- wildfire_risk_percentile (int 0..100) — source: `usfs_wildfire_risk`
- pga_10in50_g (float g) — source: `usgs_seismic_designmaps`
- hdd_annual, cdd_annual (float) — source: `noaa_normals`

## valuation_outputs

- scenario_id, property_id — keys
- noistab (float $/yr)
- value_low/value_base/value_high (float $)
- deal_quality (int 0..100) — computed from returns minus penalties (see Rulebook)
- source_manifest (json) — `{ as_of, sources{ id: YYYY-MM } }`

Refer to `architecture.md` §10 for the broader schema and to the Rulebook for formulas.
