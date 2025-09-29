## 1. Planning

- [ ] 1.1 Audit current `mypy` configuration, catalog `type: ignore` usages (with counts per module), and prioritise packages for strict adoption.
- [ ] 1.2 Draft a strict-type rollout matrix (modules → required flags) and circulate with maintainers for agreement.

## 2. Implementation

- [ ] 2.1 Update `pyproject.toml` / `mypy.ini` to enable per-module strict settings and require reasoned `type: ignore` comments.
- [ ] 2.2 Refactor high-priority modules (repository, connectors, features, valuation, CLI) to satisfy strict mode, introducing Protocols/TypedDicts as needed.
- [ ] 2.3 Annotate shared fixtures (`tests/factories.py`, `tests/conftest.py`) and eliminate implicit `Any` propagation in tests.
- [ ] 2.4 Add developer tooling (`poetry run mypy-strict` or `make mypy-strict`) and document usage in README/tests guide.

## 3. Validation

- [ ] 3.1 Run `mypy --strict` for configured modules locally and in CI.
- [ ] 3.2 Run full QA suite (ruff, black, pytest, mypy) to confirm no regressions.
- [ ] 3.3 Execute `openspec validate add-mypy-strict-checks --strict` and resolve any spec issues.
