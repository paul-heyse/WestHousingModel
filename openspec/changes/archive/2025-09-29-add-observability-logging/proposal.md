## Why

Repository consumers (Streamlit UI, CLI, future services) need structured observability to diagnose cache decisions and network activity. Today logging is ad-hoc and the stale/fresh state is implicit in return values, making debugging failures and instrumenting metrics expensive. The architecture also mandates explicit stale/fresh indicators (architecture.md §14, §16), which are currently only implicit in tests.

## What Changes

- Introduce structured logging (JSON + context) for repository fetches, cache reads/writes, and connector failures.
- Emit explicit stale/fresh indicators, including latency, cache key, and connector status, and surface them to CLI/consumers.
- Provide configuration toggles (env + settings) for log verbosity and sinks (stderr/file) while keeping defaults sensible for local workflows.
- Capture failure payload metadata with correlation IDs for later Sentry/ELK integration.

## Impact

- Affected specs: data-access/observability
- Affected code: `src/west_housing_model/data/repository.py`, `src/west_housing_model/data/connectors/*`, `src/west_housing_model/cli/main.py`, logging utilities.
- Requires coordination with testing and governance efforts to ensure scenarios validated.
