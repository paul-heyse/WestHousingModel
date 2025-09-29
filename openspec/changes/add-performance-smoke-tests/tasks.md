## 1. Planning

- [x] 1.1 Select representative scenarios (place/site/valuation) and establish baseline timing targets.
- [x] 1.2 Decide on tooling (pytest marker vs. custom script) and threshold hysteresis to minimise flakiness.

## 2. Implementation

- [x] 2.1 Implement performance smoke test harness that runs selected scenarios and records durations.
- [x] 2.2 Add CI stage to execute the smoke test (optionally nightly) and collect timing artifacts.
- [x] 2.3 Document update process for thresholds and how to review performance regressions.

## 3. Validation

- [x] 3.1 Run smoke tests locally to confirm failure at expected thresholds.
- [ ] 3.2 Ensure CI stage runs and publishes results.
- [ ] 3.3 Run `openspec validate add-performance-smoke-tests --strict`.
