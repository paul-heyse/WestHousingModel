"""Application configuration scaffolding.

This module will later expose routines to load and validate settings derived from the
source registry and environment configuration as described in the architecture
specification.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Optional


@dataclass(frozen=True)
class RegistrySettings:
    """Placeholder container for registry-related configuration."""

    enabled_sources: Mapping[str, bool]
    cache_ttl_days: Mapping[str, int]
    default_geo_scope: Optional[str] = None


__all__ = ["RegistrySettings"]
