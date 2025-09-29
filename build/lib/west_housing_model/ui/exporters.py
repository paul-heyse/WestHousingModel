"""Export helpers stub."""

from __future__ import annotations

from pathlib import Path
from typing import Mapping


def export_one_pager(
    output_path: Path, results: Mapping[str, object]
) -> None:  # pragma: no cover - stub
    """Placeholder one-pager export function."""

    raise NotImplementedError("export_one_pager will be implemented in a future change")


__all__ = ["export_one_pager"]
