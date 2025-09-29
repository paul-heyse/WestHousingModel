## ADDED Requirements

### Requirement: CLI Developer Utilities

The system SHALL provide a CLI with commands `refresh`, `features`, `render`, and `validate` to operate data workflows non-interactively.

#### Scenario: Global flags and structured logs

- **WHEN** the CLI is invoked with `--offline`, `--cache-root`, `--log-level`, or `--json`
- **THEN** the system SHALL honor the flags across subcommands and emit structured logs (`timestamp, level, action, source_id, params_hash, duration_ms, cache_hit`) to stdout/stderr.

#### Scenario: `refresh` caches sources

- **WHEN** `refresh <source_id> --param key=value` is invoked
- **THEN** the system SHALL resolve the source in the registry, use the `Repository` to read-through fetch/update cache respecting TTL and per-source locks, and exit with code 0 on success.
- **AND** on network errors with an existing stale cache, the system SHALL return stale with exit code 0 and include a `stale=true` field when `--json` is set; otherwise exit code 2.

#### Scenario: `features` builds features for inputs

- **WHEN** `features --input places.csv --type place` is invoked
- **THEN** the system SHALL compute features using pure builders, validate outputs with Pandera, and write Parquet/CSV artifacts under the cache root (or `--output` path), including a `source_manifest.json` with `(source_id → as_of)`.
- **AND** the system SHALL fail fast on schema errors (exit code 3) with a clear message.

#### Scenario: `render` produces early artifacts

- **WHEN** `render --scenario scenario.json --output out/` is invoked
- **THEN** the system SHALL load the scenario, recompute dependent features/scores, and write a JSON summary and a CSV row for inspection; if a PDF renderer is present, it MAY also produce a draft one‑pager.

#### Scenario: `validate` performs health checks

- **WHEN** `validate [<source_id>] [--offline]` is invoked
- **THEN** the system SHALL validate the registry and run connector dry‑run checks with fixtures, verifying schema and TTL logic; exit code 0 if all pass, 1 if any fail, and print a short table or JSON details.

#### Scenario: Determinism and reproducibility

- **WHEN** the same inputs and registry versions are used
- **THEN** the outputs (artifacts and manifests) SHALL be identical across runs.
