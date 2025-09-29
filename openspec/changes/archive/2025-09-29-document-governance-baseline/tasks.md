## 1. Planning

- [x] 1.1 Catalog existing features, scores, and valuation metrics to seed the Feature Dictionary.
- [x] 1.2 Define Rulebook structure (pillars, scoring adjustments, override policy) and align with stakeholders.
- [x] 1.3 Establish ADR template and select initial decisions to capture (logging, repository schema, testing cadence).

## 2. Implementation

- [x] 2.1 Write Feature Dictionary with sources, column descriptions, units, and data provenance.
- [x] 2.2 Author Rulebook detailing scoring/valuation formulas, thresholds, and governance of overrides.
- [x] 2.3 Create ADR directory with template, ADR-0001 (logging/observability), ADR-0002 (testing strategy).
- [x] 2.4 Update README/CONTRIBUTING with governance workflow, linking to new docs.
- [x] 2.5 Add checklist items (tasks/PR template) requiring updates to docs when features/rules change.

## 3. Validation

- [x] 3.1 Review docs with stakeholders for completeness and accuracy.
- [x] 3.2 Ensure ADR template integration (CI lint/check for ADR IDs in changelog).
- [x] 3.3 Run documentation spell/style checks and ensure docs build (if MkDocs/Sphinx pipeline exists).
- [x] 3.4 Run openspec validate and update architecture appendix references.
