"""Read-through cache repository interface.

Concrete implementations will hydrate DataFrames from connectors while respecting the
cache policy defined in the architecture document. The placeholder interface keeps
imports stable for upcoming features and tests.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


class Connector(Protocol):
    """Protocol describing the minimal connector contract."""

    def fetch(self, **query: Any) -> Any:  # pragma: no cover - interface stub
        """Fetch a dataset using structured query keywords."""


@dataclass
class Repository:
    """Placeholder repository façade coordinating connectors and cache layers."""

    connectors: dict[str, Connector]

    def get(self, source_id: str, **query: Any) -> Any:  # pragma: no cover - stub
        """Retrieve a dataset, delegating to a connector or returning cached data."""

        raise NotImplementedError("Repository.get will be implemented in a future change")


__all__ = ["Connector", "Repository"]
