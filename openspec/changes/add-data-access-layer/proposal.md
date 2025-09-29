## Why

We need a read-through data access layer that fronts connectors with a local Parquet/GeoParquet cache and a SQLite index, per the architecture. This enables offline mode, TTL freshness, and consistent provenance.

## What Changes

- Implement `data/repository.py` exposing a unified facade over connectors with read-through caching.
- Implement `data/cache_index.sqlite` schema (created on demand) and file layout under `data/cache/`.
- Add per-source file locks to prevent duplicate writes.
- Provide stale fallback behavior for offline mode and network failures.

## Impact

- Affected specs: data-access
- Affected code: `src/WestHousingModel/data/repository.py`, `src/WestHousingModel/data/cache/` (gitignored), optional helpers.

## Why

Reliable, offline‑capable data access is foundational for the project. We need a repository façade that centralizes read‑through caching, a durable SQLite cache index, and Parquet/GeoParquet artifact handling to ensure reproducibility, performance, and failure transparency.

## What Changes

- Add a repository façade that mediates all connector reads via a read‑through cache
- Create a SQLite cache index recording `source_id, key_hash, path, created_at, as_of, ttl_days, rows, schema_version`
- Persist artifacts as Parquet/GeoParquet under `src/west_housing_model/data/cache/` with deterministic paths
- Support offline mode (stale‑ok) with explicit status propagation
- Implement failure logging and schema‑drift handling to `cache/failures/<source_id>/...`
- Add developer utilities and minimal docs

## Impact

- Affected specs: data‑access (new capability)
- Affected code: `src/west_housing_model/data/repository.py`, `src/west_housing_model/data/catalog.py`, `src/west_housing_model/data/cache/`, `src/west_housing_model/config/settings.py`, `src/west_housing_model/cli/`
