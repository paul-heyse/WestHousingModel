## 1. Planning

- [ ] 1.1 Audit existing golden files (JSON, parquet) and identify generators.
- [ ] 1.2 Decide on diff mechanism and environment variable/flag to accept new goldens.

## 2. Implementation

- [ ] 2.1 Build golden guard utility (pytest hook or script) enforcing fail-on-diff semantics and optional acceptance flag.
- [ ] 2.2 Integrate diff summaries into CI (upload artifact or print digest) and update PR template to reference them.
- [ ] 2.3 Provide command/documentation for intentional golden regeneration, including version metadata updates.

## 3. Validation

- [ ] 3.1 Run tests with and without acceptance flag to confirm guard behaviour.
- [ ] 3.2 Ensure CI surfaces diff artifacts and blocks unreviewed golden changes.
- [ ] 3.3 Run `openspec validate add-golden-snapshot-guard --strict`.
