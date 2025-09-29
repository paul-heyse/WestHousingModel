## 1. Planning

- [ ] 1.1 Evaluate tool options (Bandit vs. Ruff security rules, pip-audit vs. safety) and decide on baseline severity thresholds.
- [ ] 1.2 Inventory existing CI/pre-commit stages to determine insertion points and caching strategy.

## 2. Implementation

- [ ] 2.1 Add security scanner configuration (Bandit or Ruff `S` rules) and integrate into CI and optional pre-commit hooks.
- [ ] 2.2 Wire dependency vulnerability auditing (`pip-audit` or `safety`) with exit-on-high alerts; create allowlist file for known issues with expiry dates.
- [ ] 2.3 Remediate or suppress (with justification) any findings surfaced by the new scanners.
- [ ] 2.4 Document local usage and suppression workflow in README/architecture/testing appendix.

## 3. Validation

- [ ] 3.1 Run security lint (`bandit`/`ruff --select S`) locally and ensure no unexpected findings remain.
- [ ] 3.2 Run dependency audit command and validate allowlist behaviour.
- [ ] 3.3 Execute `openspec validate add-security-scanning --strict`.
