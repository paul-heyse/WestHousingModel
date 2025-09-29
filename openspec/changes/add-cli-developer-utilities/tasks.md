## 1. Implementation

- [x] 1.1 Scaffold `src/west_housing_model/cli/main.py` with argparse and shared options
- [x] 1.2 Implement `refresh` → wire to `Repository.get`; support `--param key=value` and `--offline`
- [x] 1.3 Implement `features` → load inputs (CSV), call feature builders, write Parquet/CSV
- [x] 1.4 Implement `render` → load scenario, write JSON summary (PDF optional later)
- [x] 1.5 Implement `validate` → registry validation; emit JSON with statuses
- [x] 1.6 Structured outputs (action/source_id/cache_hit/stale/duration) for CI
- [x] 1.7 Add CLI entry point in pyproject

## 2. Testing

- [x] 2.1 Unit-style tests for `cmd_validate` and `cmd_features` (strict)
- [x] 2.2 Subprocess smoke tests for `validate` and `features` (JSON + files)
- [ ] 2.3 Golden artifact snapshot for `features` (tiny input)

## 3. Non-Goals

- [x] 3.1 No UI work; PDF rendering optional and stubbed if deps absent
