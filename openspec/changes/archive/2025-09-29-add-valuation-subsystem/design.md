## Context

Valuation converts features + user overrides into a deterministic value band and metrics. This design follows architecture Section 6.5 and Appendix mappings.

## Goals / Non-Goals

- Goals: deterministic modules, strict contracts, small functions, laptop-fast, testable
- Non-Goals: UI, PDF formatting, multi-tenant concerns

## Decisions

- Time step: annual, 10-yr horizon; reversion via exit cap
- Baseline rent: ZORI level (market) × unit-type multipliers; UC uplift capped at +1.5%
- Growth: jobs momentum net of supply pressure with caps/floors and reversion after yr 5
- OpEx: base $/unit/yr scaled by HDD/CDD; winter fixed line; hazard-driven insurance uplifts
- Capex: buckets with default 0–3 yr schedule; hazard contingencies as % adders
- DCF: simple levered/unlevered toggle; DSCR proxy derived from base; value band from cap rate band
- Sensitivity: 3×3 grid on rent, cap, insurance; embed as compact JSON

## Inputs / Outputs (Contracts)

Inputs: see spec requirement "Valuation Data Contracts" for fields and types.
Outputs: canonical `valuation_outputs` with keys and columns listed in the spec.

## Risks / Trade-offs

- Upstream schema drift: mitigated by Pandera contracts; fail fast with clear messages
- Parameter tuning: mapping tables live in `settings.py`; tests cover guardrails
- Performance: vectorized pandas operations; limit joins; avoid heavy geospatial

## Migration Plan

1) Land modules behind a feature-flag in CLI (render command)
2) Add schemas and tests; no UI dependency
3) Integrate with future UI/export changes

## Open Questions

- Unit-type multipliers source: fixed defaults vs configurable by market
- Cash flow frequency: annual now; monthly later if evidence demands
