"""Declarative data catalog describing connector outputs.

The catalog lists logical tables and their expected schemas. Future changes will
replace these placeholders with concrete Pandera schemas and helper functions.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence


@dataclass(frozen=True)
class TableSchema:
    """Placeholder for table metadata and expected columns."""

    name: str
    columns: Sequence[str]
    primary_key: Sequence[str]


CATALOG: Mapping[str, TableSchema] = {}


__all__ = ["TableSchema", "CATALOG"]
