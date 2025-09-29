## 1. Implementation

- [x] 1.1 Create `src/WestHousingModel/data/repository.py` with read-through cache (Parquet/GeoParquet) and SQLite index.
- [x] 1.2 Add per-source file locks; deterministic file naming by key hash.
- [x] 1.3 Implement TTL freshness checks and stale fallback.
- [x] 1.4 Wire minimal connector interface contract (callable passed in with `source_id` and `params`).

## 2. Tests

- [x] 2.1 Unit tests: fresh cache hit, expired cache refetch, network fail → stale fallback, no cache → raises.

## 3. Validation

- [x] 3.1 Run `openspec validate add-data-access-layer --strict` and resolve issues.

## 1. Implementation

- [x] 1.1 Create SQLite cache index (table `cache_index(...)`) and file layout under `data/cache/`
- [x] 1.2 Implement repository façade with read‑through caching and offline mode
- [x] 1.3 Add artifact writer/reader for Parquet/GeoParquet; deterministic paths by `source_id` and `key_hash`
- [x] 1.4 Add per‑source file lock to avoid duplicate writes; last‑writer‑wins if content hash identical
- [x] 1.5 Implement failure logging & schema‑drift handling to `cache/failures/<source_id>/...`
- [x] 1.6 Add basic CLI `refresh` and `validate` stubs wired to repository
- [x] 1.7 Tests: unit for index/pathing; integration happy path and offline fallback
- [x] 1.8 Docs: short README section and OpenSpec references
