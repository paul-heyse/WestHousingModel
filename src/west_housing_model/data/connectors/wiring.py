from __future__ import annotations

from pathlib import Path

# Ensure default connectors are available when this module is imported
from . import make_census_acs_connector  # noqa: F401


def repo_root() -> Path:
    return Path(__file__).resolve().parents[5]
