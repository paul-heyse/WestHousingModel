from __future__ import annotations

import io
import json
from typing import Any, Mapping, cast

import pandas as pd

from west_housing_model.core.exceptions import ExportError


def export_csv(frame: pd.DataFrame, *, manifest: Mapping[str, Any]) -> bytes:
    try:
        df = frame.copy()
        df["source_manifest"] = json.dumps(dict(manifest))
        csv_data = cast(str, df.to_csv(index=False))
        return csv_data.encode("utf-8")
    except Exception as exc:  # pragma: no cover - defensive
        raise ExportError("CSV export failed", context={"error": str(exc)}) from exc


def export_pdf_onepager(summary_text: str, *, manifest: Mapping[str, Any]) -> bytes:
    """Render a lightweight textual one-pager payload.

    This placeholder keeps dependencies minimal; downstream apps can hand the
    UTF-8 buffer to their preferred PDF renderer once integrated.
    """

    try:
        buf = io.StringIO()
        buf.write("ONE-PAGER\n\n")
        buf.write(summary_text.strip() + "\n\n")
        buf.write("Sources & Vintages\n")
        buf.write(json.dumps(dict(manifest), indent=2))
        return buf.getvalue().encode("utf-8")
    except Exception as exc:  # pragma: no cover - defensive
        raise ExportError("PDF export failed", context={"error": str(exc)}) from exc


__all__ = ["export_csv", "export_pdf_onepager"]
