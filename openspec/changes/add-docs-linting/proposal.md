## Why

The repository’s markdown documentation (architecture, specs, ADRs) is growing quickly. Without automated linting, formatting inconsistencies, broken links, and trailing whitespace slip into the docs, making them harder to read and contributing to merge conflicts. Establishing a docs linting baseline (markdownlint or Ruff’s MD rules) will keep textual assets consistent and enforce our style guide.

## What Changes

- Add a markdown linting tool (e.g., `markdownlint-cli2` or Ruff `MD` rules) to the development workflow and CI pipeline.
- Configure project-specific rules (line length, heading order, fenced code blocks) and an allowlist for legacy files if needed.
- Update documentation (README or CONTRIBUTING) with instructions on running the linter locally and fixing violations.

## Impact

- **Affected specs**: documentation/testing governance.
- **Affected files**: `.github/workflows/ci.yml`, `.pre-commit-config.yaml`, and documentation files touched by lint fixes.
- **Dependencies**: new dev dependency on markdown linting tool.
