"""Pytest configuration ensuring the src directory is importable and shared fixtures."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any, Dict, Generator

import pandas as pd
import pytest

from tests.factories import (
    make_ops_rows,
    make_place_base,
    make_place_components,
    make_scenario_payload,
    make_site_base,
    make_site_hazards,
)

SRC_PATH = Path(__file__).resolve().parents[1] / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))


@pytest.fixture
def place_base_df() -> pd.DataFrame:
    return make_place_base()


@pytest.fixture
def place_components_df() -> pd.DataFrame:
    return make_place_components()


@pytest.fixture
def site_base_df() -> pd.DataFrame:
    return make_site_base()


@pytest.fixture
def site_hazards_df() -> pd.DataFrame:
    return make_site_hazards()


@pytest.fixture
def ops_rows_df() -> pd.DataFrame:
    return make_ops_rows()


@pytest.fixture
def scenario_payload() -> Dict[str, Any]:
    return make_scenario_payload()


@pytest.fixture
def temp_cache_dir(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> Generator[Path, None, None]:
    cache_dir = tmp_path / "cache"
    monkeypatch.setenv("WEST_HOUSING_MODEL_CACHE_ROOT", str(cache_dir))
    yield cache_dir
    monkeypatch.delenv("WEST_HOUSING_MODEL_CACHE_ROOT", raising=False)


@pytest.fixture
def live_api_tests_enabled(monkeypatch: pytest.MonkeyPatch) -> bool:
    value = os.getenv("LIVE_API_TESTS", "0").lower()
    enabled = value in {"1", "true", "yes"}
    monkeypatch.setenv("LIVE_API_TESTS", "1" if enabled else "0")
    return enabled
