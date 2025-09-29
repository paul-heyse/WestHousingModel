## Why

Feature generation and valuation runs are expected to stay interactive (<10s on a laptop), but we lack automated checks to prevent performance regressions. As more connectors and transformations are added, execution time can degrade silently until users notice sluggish behavior. A lightweight performance smoke test will catch unexpected slowdowns early and provide baseline metrics across releases.

## What Changes

- Define representative scenarios (small place/site/valuation batches) and capture baseline timings.
- Introduce a pytest marker or standalone script that measures runtime and fails when thresholds are exceeded (with hysteresis to avoid flakiness).
- Integrate timings into CI artifacts (JSON/Markdown) so reviewers can see trends, and document how to update thresholds when intentional performance changes are made.
- Optionally expose a local `make perf-smoke` command that developers can run before pushing.

## Impact

- **Affected specs**: testing/performance coverage update.
- **Affected code**: new performance tests under `tests/performance/` or marked scenarios in existing tests; adjustments to CLI/feature workflows to support timing hooks.
- **Documentation**: README/tests guide to explain how to run the smoke test and update thresholds.
