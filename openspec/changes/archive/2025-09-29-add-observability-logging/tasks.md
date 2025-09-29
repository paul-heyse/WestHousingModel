## 1. Research & Design

- [x] 1.1 Audit current logging touchpoints (repository, connectors, CLI) and capture required context per architecture.
- [x] 1.2 Define structured logging schema (fields, levels, correlation id) and configuration strategy.
- [x] 1.3 Update design.md with logging architecture, toggle strategy, and observability roadmap.

## 2. Implementation

- [x] 2.1 Introduce shared logging utility (formatter, context manager, correlation id helper).
- [x] 2.2 Instrument `Repository.get` and cache index operations with structured logs and stale/fresh status emission.
- [x] 2.3 Propagate stale/fresh metadata to CLI output and future UI hooks via RepositoryResult extensions.
- [x] 2.4 Ensure failure capture (schema/network) records correlation metadata alongside raw payloads.

## 3. Validation

- [x] 3.1 Add unit tests for logging utility and repository instrumentation (assert structured payloads, correlation id uniqueness).
- [x] 3.2 Extend integration tests to assert stale/fresh logs surfaced during refresh/offline flows.
- [x] 3.3 Update documentation (README + architecture) with logging usage and toggles.
- [x] 3.4 Run full QA suite (ruff, mypy, black, pytest, openspec validate) and attach log samples in PR. *(openspec CLI not present; attempted execution via `.venv/bin/openspec` and noted in summary)*
