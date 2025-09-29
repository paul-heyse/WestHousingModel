## Why

We need to implement the valuation subsystem that transforms features and user overrides into defensible, reproducible valuation outputs. This enables consistent decision-making via rent baselines, growth, OpEx/insurance adjustments, capex handling, and a concise DCF with a sensitivity grid—aligned with architecture and contracts.

## What Changes

- Introduce sequential valuation modules: rent baseline, growth, OpEx & insurance adjustments, capex handling, DCF & sensitivity grid.
- Define strict data contracts (inputs/outputs) and Pandera schemas for validation.
- Implement a thin orchestration API that composes modules deterministically.
- Add CLI to render valuation from a sample Scenario JSON for smoke tests.
- **BREAKING**: Add canonical table `valuation_outputs`.

## Impact

- Affected specs: valuation (ADDED); features (read-only), scoring (read-only)
- Affected code: `src/west_housing_model/valuation/*`, `tests/test_valuation_*`, CLI wiring
- Non-goals: UI screens; golden export formatting (separate change)

## Why

The next milestone is to implement the valuation subsystem to turn features and user inputs into deal-ready outputs. This enables consistent, defensible evaluations aligned with the architecture and contracts.

## What Changes

- Add sequential valuation modules: rent & growth baselines, OpEx & insurance adjustments, capex handling, DCF & sensitivity grid.
- Define strict data contracts and Pandera schemas for inputs/outputs.
- Expose thin orchestration API that ties features and user overrides to computation.
- **BREAKING**: Introduce new canonical table .

## Impact

- Affected specs: valuation, scoring (read), features (read)
- Affected code: src/west_housing_model/valuation/*, tests/valuation/*, cli hooks.
