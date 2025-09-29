## 1. Planning

- [ ] 1.1 Catalog existing features, scores, and valuation metrics to seed the Feature Dictionary.
- [ ] 1.2 Define Rulebook structure (pillars, scoring adjustments, override policy) and align with stakeholders.
- [ ] 1.3 Establish ADR template and select initial decisions to capture (logging, repository schema, testing cadence).

## 2. Implementation

- [ ] 2.1 Write Feature Dictionary with sources, column descriptions, units, and data provenance.
- [ ] 2.2 Author Rulebook detailing scoring/valuation formulas, thresholds, and governance of overrides.
- [ ] 2.3 Create ADR directory with template, ADR-0001 (logging/observability), ADR-0002 (testing strategy).
- [ ] 2.4 Update README/CONTRIBUTING with governance workflow, linking to new docs.
- [ ] 2.5 Add checklist items (tasks/PR template) requiring updates to docs when features/rules change.

## 3. Validation

- [ ] 3.1 Review docs with stakeholders for completeness and accuracy.
- [ ] 3.2 Ensure ADR template integration (CI lint/check for ADR IDs in changelog).
- [ ] 3.3 Run documentation spell/style checks and ensure docs build (if MkDocs/Sphinx pipeline exists).
- [ ] 3.4 Run openspec validate and update architecture appendix references.
