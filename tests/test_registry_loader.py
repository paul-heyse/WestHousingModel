from pathlib import Path

import pytest

from west_housing_model.config import load_data_dictionary, load_registry
from west_housing_model.core.exceptions import RegistryError


def test_load_registry_success(tmp_path: Path):
    base = tmp_path / "sources.yml"
    sup = tmp_path / "sources_supplement.yml"
    base.write_text(
        """
sources:
  - id: bls_timeseries
    enabled: true
    endpoint: "https://example.com"
    geography: msa
    cadence: monthly
    cache_ttl_days: 60
    license: public
    rate_limit: "none"
""",
        encoding="utf-8",
    )
    sup.write_text(
        """
sources:
  - id: bls_timeseries
    notes: "overlayed"
""",
        encoding="utf-8",
    )
    reg = load_registry(base, sup)
    assert len(reg) == 1
    s = reg[0]
    assert s.id == "bls_timeseries"
    assert s.notes and "overlayed" in s.notes


def test_missing_required_field_raises(tmp_path: Path):
    base = tmp_path / "sources.yml"
    base.write_text(
        """
sources:
  - id: bad
    enabled: true
    endpoint: "https://example.com"
    geography: msa
    cadence: monthly
    # cache_ttl_days missing
    license: public
    rate_limit: "none"
""",
        encoding="utf-8",
    )
    with pytest.raises(RegistryError):
        _ = load_registry(base, base)


def test_data_dictionary_shape(tmp_path: Path):
    base = tmp_path / "sources.yml"
    base.write_text(
        """
sources:
  - id: census_acs
    enabled: true
    endpoint: "https://example.com"
    geography: tract
    cadence: annual
    cache_ttl_days: 400
    license: public
    rate_limit: "none"
""",
        encoding="utf-8",
    )
    reg = load_registry(base, base)
    dd = load_data_dictionary(reg)
    assert dd and dd[0]["id"] == "census_acs"
    assert set(dd[0].keys()) >= {
        "id",
        "enabled",
        "geography",
        "cadence",
        "cache_ttl_days",
        "license",
        "notes",
    }
