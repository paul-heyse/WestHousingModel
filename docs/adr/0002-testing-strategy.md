# ADR-0002: Testing Strategy

- Status: Accepted
- Date: 2025-09-29

## Context

We require deterministic behavior and coverage across unit, integration, and golden tests.

## Decision

- Unit tests for pure functions (feature builders, scoring, valuation math).
- Integration tests for connectors using fixtures; no live APIs in CI.
- Golden tests for end-to-end scenarios and CLI artifacts.
- Lint (ruff) and type checks; pytest as runner.

## Consequences

- High confidence, reproducibility, and quick feedback.

## Alternatives Considered

- Live API integration in CI (flaky, rate limits).

## References

- `tests/`, CLI tests, and `openspec/project.md` testing conventions.
