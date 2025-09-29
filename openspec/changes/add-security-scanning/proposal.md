## Why

The codebase currently lacks automated security/static-analysis coverage. Without Bandit- or Ruff-powered security rule sets and dependency auditing, we risk shipping credentials, insecure subprocess usage, or outdated packages without any guardrails. Several connectors interact with external APIs and the CLI exposes filesystem operations; even basic checks for shell injection (`subprocess`, `yaml.load`), weak hashing, or secrets-in-code would immediately increase confidence. Introducing lightweight security scanning in CI will catch issues before deployment and align with architecture governance around safe defaults.

## What Changes

- Add a security linting step (Bandit or Ruff `S` rules) to scan `src/` and fail on high/medium findings, with a documented allowlist process for unavoidable cases.
- Introduce dependency vulnerability auditing (`pip-audit` or `safety`) as part of CI, configured to respect our lockfiles/environment and report actionable advisories.
- Ensure the CLI workflow and connectors avoid unsafe patterns (e.g., unsanitized shell commands, `yaml.load` without `SafeLoader`); refactor offenders if the scanner flags them.
- Document the new security scanning workflow in the README/architecture appendix, including how to run locally, suppress issues with justification, and update allowlists.
- Optionally integrate scanning results into CI status badges or pre-commit hooks to encourage local hygiene.

## Impact

- **Affected specs**: testing/security coverage update.
- **Affected code/config**:
  - CI workflow files (`.github/workflows/ci.yml`) gaining new security stages.
  - `pyproject.toml` / `ruff.toml` / `.pre-commit-config.yaml` updated with Bandit/Ruff security rule sets and commands.
  - Code tweaks where scanners surface real issues (e.g., safe YAML load, secure temp files).
  - Documentation (README/tests/SECURITY.md) describing expectations and remediation paths.
- **Dependencies**: Add dev dependencies (`bandit`, `pip-audit` or `safety`) and cache their invocation to keep CI fast.
