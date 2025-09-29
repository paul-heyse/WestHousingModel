# WestHousingModel (replace via scripts/init.sh)

Baseline template for Python projects in Cursor on Ubuntu.

## Quick start (per project)

1. Run `scripts/init.sh <package_name> [python_version] "Description"`.
2. Open folder in Cursor (`cursor .`).
3. Ensure interpreter shows `.venv/bin/python`.
4. Run target tasks: **pytest**, **lint**, **format**.

See `.cursor/rules`, `.vscode/*`, and `environment.yml` for configuration details.

# Testing

```bash
# Run unit + integration tests
pytest -q

# Lint and style
ruff check src tests
black .

# Validate OpenSpec changes (if any)
openspec validate --strict
```

## Running the UI

```bash
streamlit run -m west_housing_model.ui.app
```

Pages:

- Explore: table with basic Aker Fit filter
- Evaluate: minimal valuation, provenance captions, cached evaluation + timing
- Scenarios: save/load scenario JSON (session) and export CSV with manifest
- Settings: registry dictionary (read-only) and pillar weights

## Data Access & Caching

- Connectors registered with `west_housing_model.data.connectors.register_connector` are fronted by the `Repository`
- The repository persists Parquet artifacts and a SQLite index under `WEST_HOUSING_MODEL_CACHE_ROOT` (defaults to `src/west_housing_model/data/cache/`)
- CLI helpers:
  - `west-housing-model refresh <source_id> [--param key=value]` warms the cache via connectors
  - `west-housing-model validate <source_id> --offline` verifies cached artifacts without hitting the network
- Failure payloads and drift logs are captured in `cache/failures/<source_id>/` (configurable via `WEST_HOUSING_MODEL_FAILURE_CACHE`)
- Default connector: `connector.census_acs` (ACS tract/MSA metrics) is pre-registered and ready for refresh/validate commands
- Example: `west-housing-model refresh connector.census_acs --param state=08 --param county=005`
- Structured logging: JSON logs with correlation IDs go to stderr by default; configure via `WEST_HOUSING_LOG_LEVEL` and `WEST_HOUSING_LOG_FORMAT` (`json|text`).

## Testing

- Core commands: `pytest -q`, `ruff check tests`, `black tests`.
- Coverage snapshot: `pytest --cov=west_housing_model --cov-report=term-missing`.
- Layered coverage: unit (connectors/logging), integration (CLI/cache flows), and golden scenarios (feature + valuation snapshots). See `tests/README.md` for the matrix and fixture guides.
- Use the shared factories in `tests/factories.py` to build canonical datasets and keep expectations consistent across suites.
- Performance: `pytest -m performance` runs the smoke test and fails if the end-to-end pipeline exceeds the threshold (override with `PERF_SMOKE_THRESHOLD`).

## Scoring Weights (Environment Overrides)

The app exposes scoring weights via environment variables. Defaults are sensible and normalized to sum to 1.0.

- Aker Fit pillar weights (used by `compute_aker_fit` in `features/place_features.py`):
  - `WHM_PILLAR_WEIGHT_UC` (default 0.25)
  - `WHM_PILLAR_WEIGHT_OA` (default 0.25)
  - `WHM_PILLAR_WEIGHT_IJ` (default 0.25)
  - `WHM_PILLAR_WEIGHT_SC` (default 0.25)

- Deal Quality returns weights (used by `compute_deal_quality`):
  - `WHM_RETURNS_WEIGHT_YOC` (default 0.45)
  - `WHM_RETURNS_WEIGHT_IRR` (default 0.35)
  - `WHM_RETURNS_WEIGHT_DSCR` (default 0.20)

Notes:

- Weights are normalized at runtime if they don’t sum to 1.0.
- Leave variables unset to use defaults. You can set them in your shell or via `.env`/direnv.

# Governance

- Feature Dictionary: see `docs/feature_dictionary.md` for columns, sources, units, and provenance.
- Rulebook: see `docs/rulebook.md` for scoring and valuation formulas, thresholds, and override policy.
- Architecture Decision Records (ADRs): see `docs/adr/` for decisions and rationale; start with `ADR-0001` (Logging/Observability) and `ADR-0002` (Testing Strategy).
