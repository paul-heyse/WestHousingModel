## Why

A canonical, git-tracked source registry is required to centrally configure all external datasets, control enablement, cadence, and TTLs, and support deterministic and offline operation before any connectors are implemented.

## What Changes

- Add `config/sources.yml` and `config/sources_supplement.yml` as the authoritative registry files.
- Define required fields per source: `id`, `enabled`, `endpoint`, `geography`, `cadence`, `cache_ttl_days`, `license`, `rate_limit`, `auth_key_name` (optional), `notes`.
- Specify merge semantics: load `sources.yml` then apply `sources_supplement.yml` by `id` (last-one-wins for fields, may also add new sources).
- Document field meanings in-file comments; no secrets stored in these files.

## Impact

- Affected specs: registry
- Affected code: `config/` only (files added now; used by loader in a later change)
