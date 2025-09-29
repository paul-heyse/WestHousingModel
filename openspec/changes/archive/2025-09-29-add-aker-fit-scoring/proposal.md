# Why

Implement Aker Fit scoring immediately after place features with percentile-normalized components and configurable pillar weights.

## What Changes

- Add scoring module and spec for Aker Fit.
- Define inputs, outputs, and normalization policy.
- Add tasks to implement functions, schemas, tests, and UI wiring.

## Impact

- Affects specs: scoring.
- Affects code: features/place_features.py, scoring/aker_fit.py, UI Settings.
