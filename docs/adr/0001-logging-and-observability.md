# ADR-0001: Logging and Observability

- Status: Accepted
- Date: 2025-09-29

## Context
We need consistent, structured logs across CLI, repository, and connectors.

## Decision
- Use a shared logging utility emitting JSON with correlation IDs and key fields (status, cache_key, duration, artifact_path).
- Default format: json; text optional via env var. Levels configurable.

## Consequences
- Easier troubleshooting and consistent CI logs.
- Minimal runtime overhead.

## Alternatives Considered
- Plain print statements (insufficient structure).
- External log frameworks (overkill for local app).

## References
- `src/west_housing_model/utils/logging.py`
