## 1. Implementation

- [x] 1.1 Define ACS tables/fields and expected schema in `catalog.py`
- [x] 1.2 Implement `census_acs` connector (params → request → normalize DF)
- [x] 1.3 Integrate connector with repository (keying, TTL, artifact write/read)
- [x] 1.4 Implement failure logging and offline fallback behaviors
- [x] 1.5 Tests: unit (schema, normalization), integration (read‑through, offline, failure)
- [x] 1.6 CLI: add `refresh --source census_acs` for a small geography
- [x] 1.7 Docs: brief connector doc and OpenSpec references
