## Why

The architecture mandates a feature dictionary, rulebook, and ADR process (architecture.md §§21-22), but the repo lacks baseline docs. Without them, new contributors cannot map specs to code or record design decisions, and governance tasks remain ambiguous.

## What Changes

- Draft the initial Feature Dictionary covering place/site/ops features, connector outputs, and valuation metrics.
- Author the Rulebook summarizing scoring/valuation rules, parameter ranges, and override policy.
- Establish the ADR process with templates, initial ADRs (logging, repository design), and documentation on usage.
- Integrate governance docs into README/onboarding and add CI/task checklist items to enforce updates.

## Impact

- Affected specs: governance/documentation
- Affected code/docs: `docs/feature-dictionary.md`, `docs/rulebook.md`, `docs/adr/`, README/CONTRIBUTING updates, task templates.
