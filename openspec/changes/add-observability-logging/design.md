## Context

- Repository read-through caching handles network fetches, fallback to stale cache, and failure capture but lacks structured observability.
- Architecture.md §§14-16 call for explicit stale/fresh indicators and logging hooks to support offline workflows and performance budgets.
- CLI and future UI need consistent signals to render status badges and propagate metrics.

## Goals / Non-Goals

- Goals: structured JSON logging, correlation IDs, consistent stale/fresh status emission, configurable verbosity, minimal overhead.
- Non-Goals: external log shipping (Sentry/ELK), metrics aggregation, refactoring connectors beyond logging.

## Decisions

1. **Logging library**: use Python `logging` with a custom JSON formatter + contextvars for correlation IDs. Keeps dependencies minimal.
2. **Configuration**: `WEST_HOUSING_LOG_LEVEL`, `WEST_HOUSING_LOG_FORMAT` env vars + optional settings module to tune sinks; defaults to INFO JSON to stderr.
3. **Structured fields**: `event`, `source_id`, `cache_key`, `status` (`fresh|stale|error`), `latency_ms`, `attempt`, `correlation_id`, `context` (connector/repository metadata).
4. **Stale/fresh propagation**: extend `RepositoryResult` with `status`, ensure CLI prints badges, and UI can subscribe to logs.

## Alternatives Considered

- **Loguru**: richer API but extra dependency and harder to standardize across connectors.
- **OpenTelemetry tracing**: powerful but overkill for initial scope; can wrap later via correlation IDs.

## Risks / Mitigations

- **Performance overhead**: JSON serialization adds cost; mitigate with lazy evaluation and INFO-level gating.
- **Log noise**: Provide `log_level` toggles and sample output guidelines.
- **Correlation drift**: enforce via context manager around repository entry point and propagate to connectors.

## Testing Strategy

- Unit tests: assert log records contain expected keys, correlation IDs unique per request, status toggles correct.
- Integration tests: scenario for fresh hit, stale fallback, schema error, verifying logs and RepositoryResult status.
- Golden fixtures: capture example log lines for docs/regression.

## Rollout Plan

1. Implement logging utility and repository instrumentation.
2. Propagate to CLI, adjust tests.
3. Share sample logs with stakeholders, update README/architecture.
4. Collect feedback before wiring to external sinks.
