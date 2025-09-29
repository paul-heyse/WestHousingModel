## Why

Golden datasets and JSON snapshots protect valuation and feature pipelines, but the process for updating them is manual and error-prone. Contributors can accidentally regenerate goldens without review, or forget to update them when intentional changes occur. Currently there is no automated diff or guardrail that highlights when parquet/JSON expectations change. We need a golden snapshot guard that detects modifications, requires explicit opt-in (`--accept-goldens`), and provides human-readable diffs in CI to ensure reviewers understand behavioral changes.

## What Changes

- Introduce a golden management utility (pytest plugin or custom script) that compares generated outputs with committed goldens and fails tests unless `ACCEPT_GOLDENS=1`.
- Add tooling to produce structured diffs (JSON summary or Markdown) attached to CI artifacts, making it easy to review numerical differences.
- Provide a command to regenerate goldens intentionally, updating metadata (e.g., timestamp, spec version) and documenting the rationale in PR templates.
- Update documentation (tests/README.md) with instructions on regenerating goldens, reviewing diffs, and the approval process for snapshot updates.

## Impact

- **Affected specs**: testing/golden governance.
- **Affected code**:
  - `tests/` golden utilities and fixtures, possibly under `tests/golden_utils.py`.
  - CI workflows to upload diff artifacts and require explicit acceptance.
  - PR template/README to document golden update steps.
- **Dependencies**: optional adoption of a diff tool (`deepdiff`, `jsondiff`, or in-house summary). No runtime impact.
