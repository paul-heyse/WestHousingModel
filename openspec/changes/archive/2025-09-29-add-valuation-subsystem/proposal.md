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
