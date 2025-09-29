# 1. Implementation

- [x] 1.1 Define valuation input/output contracts and Pandera schemas
- [x] 1.2 Implement rent baseline module (ZORI baseline + UC uplift + guardrail)
- [x] 1.3 Implement growth module (jobs momentum minus supply pressure with caps)
- [x] 1.4 Implement OpEx & insurance module (HDD/CDD scaler, winter line, hazard uplifts)
- [x] 1.5 Implement capex handling (buckets, timing 0–3 yrs, contingencies)
- [x] 1.6 Implement DCF (10-yr annual) + reversion, compute value band (cap rate band)
- [x] 1.7 Implement sensitivity grid (± rent, ± cap, ± insurance)
- [x] 1.8 Orchestrator: compose modules, enforce determinism, return `valuation_outputs`
- [x] 1.9 CLI: `render` valuation for a sample Scenario JSON (local fixture)
- [x] 1.10 Tests: unit per module; integration golden for a small scenario
- [x] 1.11 Docs: update architecture & rulebook references; add mapping tables
