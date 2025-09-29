# Rulebook

Authoritative formulas and governance for scoring and valuation.

## Scoring

### Aker Fit (AF)

AF = round(100 * (w_uc*UC + w_oa*OA + w_ij*IJ + w_sc*SC)), defaults w=0.25 each.

- Components normalized to percentiles within peer group; invert times where needed.

### Deal Quality (DQ)

DQ = clamp(0,100, round(R - (Pen_haz + Pen_supply + Pen_aff + Pen_data)))

- R = weighted YoC/IRR/DSCR mapped to 0..100 via tables.
- Penalties follow thresholds in `architecture.md` §6.4.2.

## Valuation

- Rent baseline from ZORI; UC-based uplift capped at +1.5%.
- Growth = g_base + f_jobs − f_supply (caps/floors).
- OpEx & Insurance: HDD/CDD scaler; flood/wildfire/seismic uplifts.
- DCF: 10-year NOI projection; terminal value via exit cap; discount rate applied.
- Sensitivity grid: rent ±5%, cap ±50 bps, insurance ±20%.

## Overrides & Governance

- Rent-to-income guardrail default upper bound 35%. Overrides allowed; must record justification in Scenario; DQ applies a small data-confidence penalty if critical data is missing/stale.
- Changes to weights, tables, or thresholds require updating this Rulebook and regenerating goldens.
- Record significant decisions as ADRs in `docs/adr/`.
