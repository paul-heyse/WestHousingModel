## Why
Implement Deal Quality (0..100) with explicit penalty tables and data-confidence adjustments after features are assembled.

## What Changes
- Add scoring module and spec for Deal Quality.
- Define mapping tables, penalties, and data confidence rules.
- Add tasks to implement functions, schemas, tests, and UI wiring.

## Impact
- Affects specs: scoring.
- Affects code: scoring/deal_quality.py, features integration, UI.
