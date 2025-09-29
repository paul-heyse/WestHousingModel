# Source Registry

This directory holds the canonical source registry files:

- `sources.yml` — base registry (public/standard sources)
- `sources_supplement.yml` — optional/commercial feeds and local overrides

Merge order is base then supplement by `id` (last-one-wins per field). No secrets are stored here; API keys, if needed, are referenced by name (e.g., `BLS_API_KEY`) and supplied via environment or local secrets files.

## Fields per source

- `id` (string, unique): Stable identifier (e.g., `bls_timeseries`).
- `enabled` (bool): Controls whether the source is active.
- `endpoint` (string): URL or dataset identifier.
- `geography` (enum): one of `msa | county | tract | point`.
- `cadence` (enum): one of `monthly | quarterly | annual | as-updated`.
- `cache_ttl_days` (int): Cache freshness window in days (0 means always refresh).
- `license` (string): License/terms (e.g., `public`, `ODbL`, `restricted`).
- `rate_limit` (string): Human-readable rate limit like `10/s` or `40/min`.
- `auth_key_name` (string, optional): Name of env var for API key; no secrets here.
- `notes` (string): Brief purpose and caveats.

## Usage

The registry loader will:

1. Load `sources.yml`.
2. Load `sources_supplement.yml` (if present) and overlay by `id`.
3. Validate required fields and warn on unknown fields.
4. Expose a Data Dictionary for the UI Settings page.
