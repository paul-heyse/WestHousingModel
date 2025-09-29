## Context

Centralized, deterministic data access with provenance, caching, and offline fallback is required to satisfy performance, reproducibility, and auditability goals.

## Decisions

- Repository façade is the single entry point for data access
- SQLite index stores cache metadata; artifacts are Parquet/GeoParquet under stable paths
- Deterministic keying via normalized connector params → stable `key_hash`
- Offline mode returns stale cache where present; never hits network
- Per‑source file lock prevents duplicate writes
- Failures and schema drift are captured to `cache/failures/<source_id>/...`

## Risks / Trade‑offs

- Added complexity vs direct connector calls → mitigated by clear interfaces/tests
- Disk footprint growth → mitigated by TTL and periodic cleanup

## Migration Plan

1. Introduce repository and index alongside connectors
2. Update callers to use repository
3. Add cleanup utilities and document TTL policy
