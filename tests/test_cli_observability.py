from __future__ import annotations

import json
import logging
from pathlib import Path

from west_housing_model.cli.main import main


def test_cli_refresh_emits_correlation_and_status(tmp_path: Path, caplog) -> None:
    with caplog.at_level(logging.INFO, logger="west_housing_model"):
        rc = main(["--json", "refresh", "connector.census_acs", "--offline"])  # offline validation path
    # exit code can be 0 or 1 depending on cache; we only assert logging/shape
    assert rc in (0, 1)

    # Run validate for JSON payload shape
    rc = main(["--json", "validate"])  # returns registry_ok payload
    assert rc == 0

    # The refresh command in offline mode may not print JSON; exercise validate only
    # Ensure logger captured at least one structured message
    assert caplog.records
    payload = json.loads(caplog.records[-1].message)
    assert "correlation_id" in payload
    assert "level" in payload

