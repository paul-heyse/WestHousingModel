## Why

Static type checking is currently enforced with a single `mypy src` run in non-strict mode. As the codebase grows, latent interface drift (e.g., optional fields, `Any` leakage, incorrect return unions) is slipping through, forcing runtime failures to surface the issues. Architecture.md (§17 Testing Strategy) calls for “strict typing on `src/`”, but our configuration never graduated beyond permissive defaults and makes no distinction between high-risk packages (connectors, repository, valuation) and experimental ones. We need a structured plan to introduce per-package strict mode, ratchet down ignores, and ensure new modules cannot regress to `Any` without justification.

## What Changes

- Define a staged strict-type road map: identify packages that must run under `mypy --strict` (repository, connectors, features, valuation, CLI) and document a backlog for remaining modules.
- Update `mypy.ini` / `pyproject.toml` to enable per-module strict settings (e.g., `warn-redundant-casts`, `warn-return-any`, `disallow-incomplete-defs`) and block `type: ignore` without a reason token.
- Refactor high-priority modules to eliminate `Any` usage, add explicit Protocols/DataClasses for connector payloads, and annotate fixtures (tests/factories) to keep the pipeline typed.
- Introduce a nightly or CI gate that runs `mypy --strict` across the targeted modules and fails on new warnings; expose a developer command (e.g., `poe mypy-strict`) documented in the README.
- Track and clean up existing `# type: ignore` usages, creating a lint step that enforces the “`type: ignore[code]  # reason`” pattern.

## Impact

- **Affected specs**: testing/typing governance updates to codify strict coverage.
- **Affected code/config**:
  - `pyproject.toml` / `mypy.ini` for strict configuration and module granularity.
  - `src/west_housing_model/...` modules requiring annotation hardening and Protocols.
  - `tests/factories.py`, `tests/conftest.py`, and fixtures to maintain type integrity.
  - Developer docs (README, tests/README) detailing strict type workflow and commands.
- **Dependencies**: No new runtime deps, but the proposal may require upgrading mypy/typing-extensions to unlock stricter rules.
