Below is a **single, stand‑alone document** you can drop in your repo as `openspec/specs/ARCHITECTURE.md`. It goes into *exceeding* depth so future contributors and IC reviewers can understand exactly **what** we’re building and **how** it fits together.

---

# ARCHITECTURE

**System:** Opportunity Identifier & Evaluator (OIE)
**Audience:** Aker investments & operations (2–4 users)
**Mode:** Local, explainable, small‑team tool—no cloud infra required

---

## 0) Executive Summary

The OIE is a **registry‑driven, data‑first** application that:

1. **Identifies** markets and specific sites that fit Aker’s thesis: *urban convenience + outdoor lifestyles*, backed by **innovation‑driven jobs** in **supply‑constrained** locations (with emphasis on **CO, UT, ID**).
2. **Evaluates** opportunities by converting measurable public datasets into **place features**, **site features**, and **operating context** that feed a compact **Aker Fit** score (brand/location fit) and a **Deal Quality** score (returns + risk).
3. Produces a **defensible valuation** (income approach + light 10‑year DCF) where every material number is traceable to a **source id**, **vintage**, and **transparent transformation**.

The architecture is layered: **Source Registry → Connectors & Cache → Feature Builders → Scoring → Valuation → UI/CLI**. Each layer is intentionally small, deterministic, and testable.

---

## 1) Goals & Non‑Goals

### Goals

* **Explainability:** Inputs and rules must be IC‑ and lender‑friendly; no black boxes.
* **Determinism:** The same inputs produce the same outputs; scenarios are reproducible.
* **Measurability:** Only use sources that can be converted into stable numeric features or explicit booleans.
* **Simplicity:** Keep modules small; favor composition over frameworks; run on a laptop.
* **Traceability:** Every figure in UI/exports shows **(source id, vintage, transformation)**.

### Non‑Goals

* Multi‑tenant SaaS, horizontal scaling, real‑time streaming, or heavy raster processing.
* Parsing news, case law, or unstructured regulatory digests into machine rules.

---

## 2) System Context & Personas

**Personas**

* **Investor/Operator (primary):** explores markets, screens addresses, tweaks a handful of pro‑forma inputs, exports one‑pagers.
* **Data‑savvy teammate (secondary):** updates source registry, adds a connector, tunes weights, refreshes caches.

**Execution Context**

* Single machine; **Streamlit** GUI; local **SQLite + Parquet/GeoParquet** caches; optional internet for source refresh; **Offline mode** reads caches only.

**High‑level Dataflow**

```
+------------------+      +---------------------+      +-----------------+      +----------------+
| Source Registry  | ---> | Connectors + Cache  | ---> | Feature Builders| ---> | Scoring/Val'n  |
| (YAML)           |      | (read-through)      |      | (place/site/ops)|      | + UI/Exports   |
+------------------+      +---------------------+      +-----------------+      +----------------+
```

---

## 3) Domain Model (Entities & IDs)

We model only three entities to keep reasoning clear.

### 3.1 Place

Represents a geographic aggregation used for market selection and percentiles.

* **Keys:** `place_id` (stable string), `geo_level` (`msa|county|tract|block_group`), `geo_code` (e.g., CBSA code), `name`.
* **Attributes:** time‑varying **features** (jobs growth, permits, amenity density percentiles, outdoor access metrics, broadband flag).
* **Use:** percentile baselines for scoring pillars; map context in UI.

### 3.2 Property (Site)

Represents a candidate asset at an approximate centroid (parcel, address).

* **Keys:** `property_id` (UUID), `address`, `lat`, `lon`, `place_id` (foreign key).
* **Attributes:** site-level **hazards** (flood flag/zone, wildfire percentile, PGA screen), **winter/heat metrics**, **proximities**, **ops context** (utilities notes), **zoning/entitlement flags** when available.
* **Use:** gating flags for insurance/capex, convenience/outdoor adjustments, valuation inputs.

### 3.3 Scenario

A saved set of **user overrides** and **data vintages**.

* **Keys:** `scenario_id` (UUID), `property_id`.
* **Attributes:** unit mix, current rent or target rent, base OpEx, capex plan (simple buckets), leverage & cap rate band, weighting sliders; **manifest** of `(source_id → as_of)` used to compute outputs.
* **Use:** reproducible exports and golden tests.

---

## 4) Functional Overview

### 4.1 Opportunity Identification

* **Place scanning:** Compute the **Aker Market Fit** per place using the four pillars (Urban Convenience, Outdoor Access, Innovation Jobs, Supply Constraints). Use these to **rank** MSAs/submarkets.
* **Site screening:** For an address or CSV list, compute **site features** (hazards, winter risk, proximities) and attach the place context. Flag “pass/follow‑up” quickly.

### 4.2 Opportunity Evaluation

* **Valuation workbook:** Establish rent baselines and growth guardrails; compute OpEx (including hazard‑derived adjustments); light DCF; **sensitivity tiles**.
* **Scores:** Aker Fit (brand/location) and Deal Quality (returns + risk) with contribution bars.

### 4.3 Exports & Auditability

* **One‑pager PDF** and **CSV**; both include **Sources & Vintages** appendix and list any manual overrides.

---

## 5) Non‑Functional Requirements

* **Performance:** Feature build for ≤50 sites under **10 seconds** on a typical developer laptop; place scans for a state under **30 seconds** once caches are warm.
* **Resilience:** Connectors tolerate intermittent network; cache prevents repeated downloads; **Offline mode** guarantees usability.
* **Data Quality:** Each connector output is validated against a known schema; each feature builder enforces column names/types.
* **Security:** No secrets in repo or logs; local caches only; optional licenses respected.
* **Portability:** Works via `conda`/`uv` with documented dependencies; devcontainer present.

---

## 6) Layered Architecture (Detailed)

### 6.1 Configuration & Source Registry

**Files**

* `config/sources.yml` and `config/sources_supplement.yml` (checked into git; no secrets).

**Required fields per source**

* `id` (unique), `enabled` (bool), `endpoint` (URL or dataset id), `geography` (msa/county/tract/point), `cadence` (monthly/quarterly/annual/as‑updated), `cache_ttl_days`, `license`, `rate_limit`, `auth_key_name` (if any), `notes`.

**Registry Loader**

* Validates schema at startup; warns on missing/unknown fields; renders a **data dictionary** section in the UI Settings tab.

**Principles**

* **Central truth:** Only the registry decides which sources are active.
* **Provenance:** Each record created from a source carries `{source_id, as_of}` forward.

---

### 6.2 Data Access: Connectors & Read‑Through Cache

**Connector responsibilities (per source family)**

* Accept structured queries (place codes, date spans, bounding boxes).
* Fetch raw data (HTTP request, file read, or tiled overlay).
* Normalize to a **small, typed DataFrame** with **documented columns**.
* Append two metadata columns: `source_id` and `as_of` (year‑month or release date).

**Cache design**

* **Artifacts:** Parquet / GeoParquet files under `src/west_housing_model/data/cache/`.
* **Index:** SQLite with table `cache_index(source_id, key_hash, path, created_at, as_of, ttl_days, rows, schema_version)`.
* **Keying:** Connector computes a **stable key** from query params (e.g., `cbsa=19740&year=2025&gran=msa`) then hashes to `key_hash` for file naming.
* **Read‑through:** Repository checks index → if **fresh** (not expired per TTL), return cached DF; otherwise fetch, validate, persist, update index, return.
* **Offline mode:** Repository returns **stale** cache with a **warning** badge; never goes to network.

**Concurrency**

* Per‑source lock (file lock) to avoid duplicate writes; last writer wins with identical content hash.

**Failure modes & recovery**

* **Network fail:** return stale cache if present; bubble a “stale” status to UI.
* **Schema drift:** connector emits a **versioned schema**; if drift detected, save raw payload to `cache/failures/{source_id}/…` and raise a clear error with mitigation steps.

---

### 6.3 Feature Builders (Pure, Deterministic)

**General rules**

* No I/O; inputs are **DataFrames** from connectors.
* Enforce **column schemas** with Pandera on function boundaries.
* Each output column includes: **name**, **type**, **units**, **provenance** (kept in a sidecar metadata object used by the UI).

#### 6.3.1 Place Features (Pillars)

**Urban Convenience**

* **Amenity counts**: OSM POIs for everyday needs (grocery, pharmacy, primary care, cafes, schools). Metrics:

  * `amenities_15min_walk_count` (count within 15‑min walk isochrone from centroid or gridded average).
  * `grocery_10min_drive_count` (count).
* **Access/Network**:

  * `avg_walk_time_to_top3_amenities` (minutes using routing service; lower is better).
  * `intersection_density` (EPA SLD proxy) — intersections per sq mi.
* **Transit (if available)**:

  * `nearest_transit_stop_distance_m` + simple headway proxy (if GTFS present).
* **Broadband**:

  * `broadband_gbps_flag` (True if ≥1 Gbps available per FCC BDC).

**Outdoor Access**

* `minutes_to_trailhead` (routing to nearest trailhead).
* `public_land_acres_30min` (PAD‑US within 30‑min drive).
* (Optional) `water_access_flag` if significant water bodies within 15 minutes.

**Innovation Jobs**

* `msa_jobs_t12` and `msa_jobs_t36` (%), BLS CES/LAUS.
* `industry_mix_score` (optional): normalized LQs in healthcare, prof‑services, manufacturing.

**Supply Constraints**

* `slope_gt15_pct_within_10km` (% area on slope >15%).
* `protected_land_within_10km_pct` (%).
* `permits_5plus_per_1k_hh_t12` (Census BPS normalized by households).
* (Optional) `water_constraints_flag` (manual or state dataset flag).

**Normalization & Aggregation**

* For each pillar, **z‑score or percentile** within the peer group (e.g., within a state or across all scanned MSAs).
* All components scaled so **higher = better** for the pillar (e.g., invert times: `score = 1 / (1 + minutes)` or percentile of the negative).
* Pillar score = weighted mean of its components (weights documented in `settings`).

#### 6.3.2 Site Features

**Hazards**

* **Flood** (FEMA NFHL):

  * `in_sfha` (bool), `fema_zone` (A/AE/VE/X), `distance_to_sfha_m` (positive outside; 0 if inside).
* **Wildfire** (USFS Wildfire Risk to Communities):

  * `wildfire_risk_percentile` (0–100 at tract/block group).
* **Seismic** (USGS design maps):

  * `pga_10in50_g` (ground acceleration at 10% in 50yr; screen for SRA need).
* **Winter & Heat** (NOAA):

  * `hdd_annual`, `cdd_annual` (1991–2020 normals).
  * `winter_storms_10yr_county` (Storm Events).
* **Proximity Flags** (livability/risk context):

  * `pipelines_within_500m_flag` (PHMSA NPMS).
  * `rail_within_300m_flag` (FRA lines).
  * `regulated_facility_within_1km_flag` (EPA ECHO/FRS).
* **Zoning/Entitlement** (optional where data exists):

  * `mf_allowed_flag`, `max_height_ft` (if present), otherwise `zoning_context_note`.

**Ops Context**

* `utility_rate_context_note` (EIA/URDB; captured as text plus a state‑level cost band).
* `broadband_gbps_flag` (propagated from place if site inherits same coverage).

---

### 6.4 Scoring Engines

#### 6.4.1 Aker Fit (0–100)

**Pillars (equal weight initially)**

1. **Urban Convenience** → `UC`
2. **Outdoor Access** → `OA`
3. **Innovation Jobs** → `IJ`
4. **Supply Constraints** → `SC`

**Computation**

* For each pillar: `pillar_index = percentile_rank(component_1..n within peer group, weights)`.
* **Aker Fit**:
  `AF = round(100 * (w_uc*UC + w_oa*OA + w_ij*IJ + w_sc*SC))`, with `w_*` defaulting to 0.25 each (tunable in settings/UI).
* **Explainability**: UI shows **contribution bars** (each pillar’s share) and a tooltip listing the top three drivers (e.g., “minutes_to_trailhead = 9.7 (p90)”).

#### 6.4.2 Deal Quality (0–100)

**Subcomponents**

* **Returns (R):** stabilized yield‑on‑cost (YoC), 5‑yr levered IRR band, DSCR proxy @ UW rate.
* **Risk (K):** hazard penalties (flood/wildfire/seismic/winter), insurance/OpEx headwinds, supply pressure, rent‑to‑income safety.
* **Data Confidence (C):** penalty for stale/missing data.

**Computation**

* Normalize each R metric to a 0–100 subscore (mapping tables below).
* Apply **downward adjustments** for K and C (penalties are monotonic, bounded).
* Example mapping:

  * **YoC**: 5.5% → 40; 6.0% → 55; 6.5% → 70; 7.0% → 85; ≥7.5% → 95.
  * **IRR band (base)**: 10% → 40; 12% → 60; 14% → 80; ≥16% → 92.
  * **DSCR**: 1.20x → 40; 1.25x → 55; 1.30x → 70; 1.40x → 90.
* **Hazard penalties (examples)**:

  * `in_sfha` → −10 (and force flood insurance line).
  * `wildfire_risk_percentile ≥ 75` → −5; ≥90 → −10.
  * `pga_10in50_g ≥ 0.15` → −5 (and flag SRA).
  * `winter_storms_10yr_county ≥ state_p75` → −3; ≥p90 → −6.
* **Supply pressure**: `permits_5plus_per_1k_hh_t12 ≥ p75` → −5; ≥p90 → −10.
* **Affordability guardrail**: if **pro‑forma rent‑to‑income** exceeds threshold (e.g., 33–35%): −5 to −15.
* **Data confidence**: missing/stale key features → −3 to −10.

**Overall**
`DQ = clamp( 0, 100, round( (w_yoc*YoC + w_irr*IRR + w_dscr*DSCR)  − (pen_haz + pen_supply + pen_aff + pen_data) ) )`
Defaults: `w_yoc=0.45, w_irr=0.35, w_dscr=0.20`.

---

### 6.5 Valuation Engine

**Inputs**

* Unit mix & current/target rent (user).
* Market context: `zori_level`, `zori_yoy`, `rent_to_income`, `msa_jobs_t12`, `permits_5plus_per_1k_hh_t12`.
* Ops: base OpEx $/unit/year (user), utilities scaling (HDD/CDD), insurance adjustments (hazards).
* Capital: capex plan buckets (user), cap rate band, leverage assumptions (user).

#### 6.5.1 Rent Baseline & Growth

* **Baseline rent** per unit type derived from `zori_level` (ZIP/MSA) with a submarket or site uplift/discount derived from **Urban Convenience** percentile (small, capped effect).
* **Affordability guardrail**: implied **rent‑to‑income** using ACS median HH income must fall within a band (e.g., 25–35%) unless user overrides (override recorded).
* **Growth (yrs 2–5)**:
  `growth = g_base + f_jobs(msa_jobs_t12, msa_jobs_t36) − f_supply(permits_per_1k_hh)`
  with caps/floors and reversion to long‑run trend after year 5.

#### 6.5.2 OpEx & Insurance

* **Base OpEx**: user value, adjusted by simple scalars:

  * **Utilities scaler**: linear function of HDD/CDD vs U.S. median.
  * **Snow/ice line**: if winter events high, add fixed $/unit/year.
  * **Insurance**:

    * `in_sfha` → add **flood** premium from rule‑of‑thumb band.
    * `wildfire_risk_percentile` top quartile → property insurance uplift (banded).
    * **Seismic** screen high → modest uplift and contingency line.

#### 6.5.3 Capex & Contingencies

* **User plan**: value‑add scope by bucket (unit interiors, exterior/common, systems).
* **Hazard contingencies**: additive % reserve where warranted (e.g., flood/seismic context).
* **Timing**: simple schedule across years 0–3 for value‑add; exit capex reserve for systems replacement (optional).

#### 6.5.4 Quick Income Approach & DCF

* **Income approach**: stabilized NOI / cap rate (band) → **value range**.
* **DCF (10‑yr)**: NOI projection with rent growth and OpEx adjustments; reversion using **exit cap**; simple financing (interest‑only toggle or amortizing).
* **Sensitivity** tiles: rent ±5%, cap ±50 bps, insurance ±20% → 9‑cell grid, displayed and exported.

---

## 7) UI Architecture

**Framework:** Streamlit (no server maintenance; trivial to run)

**Pages**

1. **Explore**

   * **Map + table** of places/properties.
   * Filters: **Aker Fit**, rent momentum, hazard flags, supply pressure.
   * **CO/UT/ID** quick toggles.
2. **Evaluate**

   * Left pane: **editable inputs** (unit mix, rents, OpEx base, capex plan, leverage, cap rate).
   * Right pane: **auto‑filled features**, **scores**, **valuation outputs**, **sensitivity grid**.
   * **(i)** tooltips show source id, as‑of, transformation.
3. **Scenarios**

   * Save/load scenario JSON; show manifest of **data vintages**.
4. **Settings**

   * Registry viewer (per‑source status & last refresh), API keys (local), pillar weights, optional feeds on/off.

**State & Caching**

* UI state persists per session; saved **Scenario** stores all overrides + manifest.
* Data frames cached in memory after repository returns; invalidation when underlying cache is refreshed.

**Exports**

* **PDF one‑pager** (summary + appendix of sources/vintages).
* **CSV** (feature row + valuation outputs + score breakdown).

---

## 8) CLI (Developer Utilities)

* **`refresh`**: warm caches for a given state/MSA/place list.
* **`features`**: build place/site features for CSV of addresses; write Parquet.
* **`render`**: produce one‑pagers from a saved Scenario file.
* **`validate`**: check registry schemas and connector health.

(Names are illustrative; in code they become thin commands in `src/west_housing_model/cli/`.)

---

## 9) Directory Layout (Target)

```
src/west_housing_model/
  config/                # settings, registry loader, data dictionary
  core/                  # entities, schemas, constants, exceptions
  data/
    connectors/          # one file per source family (bls, census, fema, usgs, noaa, usfs, hud, zillow, osm, routes, zoning)
    cache/               # parquet/geoparquet + sqlite index (gitignored)
    repository.py        # read-through cache facade
    catalog.py           # named tables referencing connectors & expected schemas
  features/
    place_features.py
    site_features.py
    ops_features.py
  scoring/
    aker_fit.py
    deal_quality.py
  valuation/
    rent_and_growth.py
    opex_and_insurance.py
    capex_and_contingency.py
    dcf.py
  ui/
    app.py
    components.py
    exporters.py
  cli/
    main.py
  utils/
    geometry.py
    tables.py
    logging.py
config/
  sources.yml
  sources_supplement.yml
tests/
  unit/
  integration/
  golden/
  data/fixtures/
openspec/
  specs/
  changes/
```

---

## 10) Data Model (Tables & Schemas)

### 10.1 Canonical Tables (examples)

**`place_features`** (GeoParquet)

* Keys: `place_id`, `as_of`
* Columns (subset):
  `amenities_15min_walk_count:int`, `avg_walk_time_to_top3_amenities:float[min]`,
  `public_land_acres_30min:float[acres]`, `minutes_to_trailhead:float[min]`,
  `msa_jobs_t12:float[%]`, `msa_jobs_t36:float[%]`,
  `permits_5plus_per_1k_hh_t12:float`, `slope_gt15_pct_within_10km:float[%]`,
  `broadband_gbps_flag:bool`,
  `pillar_uc:float[0..1]`, `pillar_oa:float[0..1]`, `pillar_ij:float[0..1]`, `pillar_sc:float[0..1]`,
  `aker_market_fit:int[0..100]`,
  `source_id:text`, `as_of:text`

**`site_features`** (GeoParquet)

* Keys: `property_id`, `as_of`
* Columns (subset):
  `lat:float`, `lon:float`, `place_id:text`,
  `in_sfha:bool`, `fema_zone:text`, `distance_to_sfha_m:float[m]`,
  `wildfire_risk_percentile:int[0..100]`,
  `pga_10in50_g:float[g]`,
  `hdd_annual:float`, `cdd_annual:float`, `winter_storms_10yr_county:int`,
  `pipelines_within_500m_flag:bool`, `rail_within_300m_flag:bool`,
  `regulated_facility_within_1km_flag:bool`,
  `mf_allowed_flag:bool|null`, `zoning_context_note:text`,
  `source_id:text`, `as_of:text`

**`valuation_outputs`** (Parquet)

* Keys: `scenario_id`, `property_id`, `as_of`
* Columns (subset):
  `noistab:float[$/yr]`, `cap_rate_low:float[%]`, `cap_rate_base:float[%]`, `cap_rate_high:float[%]`,
  `value_low:value_base:value_high:float[$]`,
  `yoc_base:float[%]`, `irr_5yr_low/base/high:float[%]`, `dscr_proxy:float[x]`,
  `insurance_uplift:float[$/unit/yr]`, `utilities_scaler:float`,
  `aker_fit:int[0..100]`, `deal_quality:int[0..100]`,
  `sensitivity_matrix:json`,
  `source_manifest:json`

### 10.2 Column Conventions

* Lower snake case; no units in names (units live in the **dictionary**).
* Booleans for flags; numeric **floats** for continuous metrics; **ints** for counts/percentile buckets.
* All outputs include a `source_id` or **array of contributing source ids** and the `as_of` vintage.

---

## 11) Data Sources (Registry Examples & TTLs)

*(These are representative; your actual `sources*.yml` define exact fields.)*

| Source id                 | Purpose              | Geography      | Cadence/TTL          | Notes                          |
| ------------------------- | -------------------- | -------------- | -------------------- | ------------------------------ |
| `census_acs`              | income & rent burden | tract/MSA      | annual / 400d        | ACS 1‑yr/5‑yr tables           |
| `bls_timeseries`          | jobs momentum        | MSA/state      | monthly / 60d        | CES & LAUS                     |
| `census_bps`              | permits (5+ units)   | county/MSA     | monthly / 60d        | supply pressure                |
| `zillow_research`         | rent level/momentum  | ZIP/MSA        | monthly / 60d        | ZORI                           |
| `fema_nfhl`               | flood zones          | parcel/point   | map updates / 365d   | SFHA, zone                     |
| `usfs_wildfire_risk`      | wildfire percentile  | tract          | annual / 365d        | percentile 0–100               |
| `usgs_seismic_designmaps` | PGA screen           | point          | model updates / 365d | 10% in 50yr g                  |
| `noaa_normals`            | HDD/CDD              | station/interp | decadal / 3650d      | 1991–2020 normals              |
| `noaa_storm_events`       | winter events        | county         | monthly / 180d       | 10‑yr count                    |
| `osm_overpass`            | POIs                 | point/tiles    | monthly / 60d        | amenity categories             |
| `routes_service`          | travel times         | point→network  | on demand / 0d       | OSRM/ORS, locally rate‑limited |
| `pad_us`                  | protected lands      | polygon        | annual / 365d        | acres within 30 min            |
| `fcc_bdc`                 | broadband            | block          | semiannual / 240d    | gigabit flag                   |
| `hud_fmr`                 | reference rents      | county/MSA     | annual / 400d        | FMR context                    |
| `eia_rates`               | utilities            | state          | monthly / 120d       | $/kWh & $/therm bands          |

---

## 12) Algorithms & Mappings (Explicit)

### 12.1 Percentile Computation

To avoid global outlier skew, **percentiles** are computed within a **peer group**:

* For Aker’s emphasis on CO/UT/ID, default peer group is **state + adjacent states** (configurable: `peer_group = "regional|national|msa_family"`).
* Percentile function uses **rank‑based** approach with mid‑rank handling; values outside observed range saturate at 0 or 1.

### 12.2 Time Alignment

* Every feature carries `as_of` (YYYY‑MM). For place composites, **all components** are aligned to the **latest shared month** among their sources (with a maximum skew tolerance, e.g., ≤90 days). If tolerance exceeded, mark **stale** and apply a small penalty to Data Confidence.

### 12.3 Rent Guardrail (Affordability)

* Compute **rent‑to‑income**: `(pro‑forma rent * 12) / median_hh_income`.
* Guardrail: default upper bound **35%**; if exceeded and not overridden, cap rent increase until within band. Override is allowed but recorded and penalizes Deal Quality slightly unless justification is added in scenario notes.

### 12.4 Insurance Uplift Heuristics

* **Base property insurance**: user baseline $/unit/year; we apply **multipliers**:

  * Flood in SFHA: add placeholder **flood premium** range (configurable by state).
  * Wildfire percentile ≥75: +10–20% to property insurance.
  * Seismic screen high: +5–10%.
* These are **signals**, not quotes. The goal is consistency across deals.

### 12.5 Lease‑Up & Concessions

* Development/value‑add scenarios may apply a **lease‑up curve** driven by:

  * **Urban Convenience** (faster if ≥p75).
  * **Supply pressure** (slower if ≥p75 permits).
* The curve is a small table (month vs occupancy) configurable in settings.

---

## 13) Error Taxonomy & Handling

**Classes (conceptual)**

* **RegistryError:** registry YAML invalid or missing fields.
* **ConnectorError:** fetch failure (network, auth, 4xx/5xx).
* **SchemaError:** connector or feature DataFrame shape mismatch.
* **CacheError:** read/write issues; corruption detection via checksums.
* **ComputationError:** infeasible values (e.g., negative rents) or division by zero.
* **ExportError:** file write fail.

**Policy**

* **Fail fast** on Schema/Computation errors with clear message and mitigation.
* **Degrade gracefully** on Connector errors if cache exists; show **stale** status.
* Always log `source_id`, parameters, and duration; never log secrets.

---

## 14) Observability & Logging

* Repository, connectors, and CLI emit **structured JSON logs** with correlation IDs, cache key hash, status (`fresh|refreshed|stale`), duration, and artifact path.
* Logging is configurable via `WEST_HOUSING_LOG_LEVEL` and `WEST_HOUSING_LOG_FORMAT` (`json` default, `text` optional); callers can reuse the shared formatter/context manager.
* Failure capture writes JSON payloads including correlation IDs alongside raw artifacts, easing post-mortems and future log shipping.
* CLI/UX surfaces the repository status (`fresh|refreshed|stale`) and correlation ID for troubleshooting; UI status bar shows **Fresh / Stale / Missing** badges sourced from the same status metadata.

---

## 15) Security & Licensing

* Secrets are kept **outside** git (`.envrc` / Streamlit `secrets.toml`).
* Caches contain **public data** only. Proprietary or license‑restricted feeds (e.g., third‑party POI ratings) are **off by default**; enabling them requires a license toggle in Settings and adds their **attribution** to exports.
* Exports include a **Sources & Vintages** appendix for compliance and audit.

---

## 16) Performance & Footprint Targets

* **Place scans**: limit feature components to O(N) operations and small geospatial joins; avoid rasters; favor **centroid** sampling and **vector** overlays.
* **Routing**: cap requests via batching and nearest‑k computations; cache results per `lat/lon` rounded to ~30–60 m.
* **Memory**: keep DataFrames narrow (only needed columns), prefer categoricals for small string domains.

---

## 17) Extensibility

**Adding a source**

1. Add to `config/sources_supplement.yml`.
2. Write a **connector** (normalize columns; add `source_id`, `as_of`).
3. Register expected schema in `catalog.py`.
4. Write **unit tests** (fixture) and an **integration test** (connector).
5. If used by features, update **Feature Dictionary** + **Rulebook** + tests.

**Adding a feature**

1. Extend a feature builder (place/site/ops); keep transformation **pure**.
2. Update the **feature schema**; add tests.
3. Add a tooltip description and provenance mapping for the UI.

**Changing a scoring weight or mapping**

* Update `settings.py` defaults and UI sliders.
* Update **Rulebook**, regenerate golden outputs intentionally with a changelog entry.

---

## 18) Testability Hooks (Architectural)

* Feature builders accept **DataFrames**, not connectors—easy to test with fixtures.
* Connectors have **`dry_run`** mode to emit a small, fixed frame (for integration tests).
* DCF uses a **plain data contract** (dict‑like inputs), so we can snapshot results (“goldens”).

---

## 19) Releases, Versioning, and Data Vintage Manifest

**Versioning:** Semantic (`MAJOR.MINOR.PATCH`).
**Data Manifest:** JSON object stored with each scenario:

```json
{
  "as_of": "2025-09",
  "sources": {
    "census_acs": "2023-12",
    "bls_timeseries": "2025-08",
    "zillow_research": "2025-08",
    "census_bps": "2025-08",
    "fema_nfhl": "2025-06",
    "usfs_wildfire_risk": "2025-01",
    "usgs_seismic_designmaps": "2024-10",
    "noaa_normals": "1991-2020",
    "noaa_storm_events": "2025-08",
    "osm_overpass": "2025-08",
    "pad_us": "2025-05",
    "fcc_bdc": "2025-06"
  }
}
```

Exports embed this manifest; golden tests compare both results **and** manifest.

---

## 20) UI Content Specification (What users see)

**Explore**

* Table columns: `place`, `aker_market_fit`, `zori_yoy`, `msa_jobs_t12`, `permits_5plus_per_1k_hh_t12`, hazard prevalence (% in SFHA), quick chips for **CO/UT/ID**.
* Map layers: places shaded by **Aker Fit**; toggle wildfire percentile and flood zones for context (lightweight).

**Evaluate**

* Inputs: unit mix (# of 0/1/2/3 BR), current/target rents, base OpEx $/unit/yr, capex plan (simple sliders or text inputs), leverage (LTV/rate), cap rate band, toggle for “value‑add” or “stabilized.”
* Outputs: NOI, value band, IRR band, DSCR proxy, **Aker Fit** and **Deal Quality** with contributions, **hazard badges**.
* Sensitivity grid and **(i)** tooltips with provenance.

**Scenarios**

* List of saved scenarios; click to reopen and recalc under current source versions or **lock to vintage** for exact reproduction.

**Settings**

* Registry viewer with **last refresh times**, enable/disable flags, API keys input, pillar weights.

---

## 21) Governance: Documentation & ADRs

* **Feature Dictionary** and **Rulebook** are authoritative for names and formulas.
* **ADRs** record major changes (UI framework, scoring weights policy, cache strategy).
* **Changelog** lives in `openspec/changes/` and drives release notes.

---

## 22) Risk Register (Architecture‑level)

* **Upstream schema drift** (high likelihood): mitigated by Pandera schemas, connector tests, and failing fast with clear messages + raw payload captures.
* **Routing rate limits** (medium): mitigated by caching, rounding coordinates, and batching.
* **Geo heavy operations** (low): ruled out by design; no rasters unless whitelisted.
* **License creep** (medium): all optional commercial feeds are disabled by default and marked in Settings.

---

## 23) Example End‑to‑End Flow (Narrative)

1. **User** enters an address in **Evaluate**.
2. **Geocoding** assigns `lat/lon`, place (MSA/tract); repository fetches/caches site hazards (FEMA/USFS/USGS/NOAA) and proximities (OSM/Routes).
3. **Feature builders** compute site features; **place features** already exist from prior scan (or are built on demand).
4. **Scoring** calculates Aker Fit and Deal Quality; **Valuation** computes NOI, DCF, and sensitivity using ZORI/ACS/BLS/BPS contexts and hazard‑based OpEx/insurance adjustments.
5. **UI** displays outputs with tooltips showing **source id + vintage + transformation**.
6. **User** saves a **Scenario** and exports a **one‑pager**; the **manifest** captures all data vintages for reproducibility.

---

## 24) Appendix A — Mapping Tables (Defaults)

**Convenience uplift to baseline rent (cap at +1.5%):**

* UC percentile < 25 → 0.0%
* 25–50 → +0.5%
* 50–75 → +1.0%
* ≥ 75 → +1.5%

**Wildfire insurance uplift (on property insurance line):**

* percentile < 75 → 0%
* 75–90 → +10%
* ≥ 90 → +20%

**Supply pressure growth haircut (yrs 2–3):**

* permits per 1k HH < p50 → 0 bps
* p50–p75 → −25 bps
* p75–p90 → −50 bps
* ≥ p90 → −75 bps

*(All tunable in `settings` and surfaced in Settings UI; changes require a Rulebook & golden update.)*

---

## 25) Appendix B — Glossary

* **Aker Fit:** Composite score indicating alignment with Aker’s “urban convenience + outdoor lifestyle” thesis.
* **Deal Quality:** Score combining returns and measured risks (hazards, supply, affordability).
* **PGA (10% in 50yr):** Peak ground acceleration with 10% probability of exceedance in 50 years.
* **SFHA:** Special Flood Hazard Area (FEMA A/AE/VE).
* **ZORI:** Zillow Observed Rent Index.
* **BPS (5+):** Census Building Permits Survey for buildings with 5+ units.

---

### Final Word

This architecture deliberately **privileges clarity over cleverness**. By constraining ourselves to **three entities**, **registry‑driven data**, **deterministic features**, and **small scoring/valuation rules**, we build a tool that a two‑person team can maintain—and that an Investment Committee can trust.
