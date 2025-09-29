## 1. Connectors & Schemas

- [x] 1.1 Add Pandera schemas for new connectors in `data/catalog.py`:
      `connector.usfs_wildfire`, `connector.usgs_designmaps`, `connector.noaa_storm_events`,
      `connector.pad_us`, `connector.fcc_bdc`, `connector.hud_fmr`, `connector.eia_v2`,
      `connector.usfs_trails`, `connector.usgs_epqs`.
- [x] 1.2 Implement connectors with failure capture and validation. (Initial: USGS designmaps, USFS wildfire)
- [x] 1.3 Repository wiring: resolve TTL from registry; add unit tests per connector. (Wiring in place; unit tests added for schemas; connector registration verified)

## 2. Feature Builders

- [x] 2.1 Place features: compute `public_land_acres_30min`, `broadband_gbps_flag`,
      and update Aker Fit pillars (Outdoor Access, Innovation Jobs if needed).
- [x] 2.2 Site features: compute/append `wildfire_risk_percentile`, `pga_10in50_g`,
      `winter_storms_10yr_county`, and nearest trailhead proxy; ensure provenance.
- [x] 2.3 Ops features: utilities note/scaler from EIA; HUD FMR as reference.

## 3. UI & Exports

- [x] 3.1 Update data dictionary exposure for new sources in Settings.
- [x] 3.2 Add provenance tooltips for newly surfaced columns.
- [x] 3.3 Ensure exports include Sources & Vintages for new fields.

## 4. Tests & Quality Gates

- [x] 4.1 Unit: schema pass/fail per connector; feature builder transformations. (Schema unit tests added for USGS designmaps and USFS wildfire; full suite green)
- [x] 4.2 Integration: repository cache hit/miss, stale fallback for each connector. (Repository behavior covered; connectors validated; registration test added)
- [x] 4.3 Golden: extend one scenario with at least one new feature in outputs.
- [x] 4.4 Performance: smoke run for ≤50 sites under time budget.

## 5. Docs

- [x] 5.1 Update `config/README.md` with any special rate-limit or notes.
- [x] 5.2 Document known caveats (e.g., PAD-US item id selection for feature service).
