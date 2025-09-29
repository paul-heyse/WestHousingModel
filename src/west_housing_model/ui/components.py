from __future__ import annotations

from typing import Any, Mapping


def format_tooltip(label: str, provenance: Mapping[str, Any] | None) -> str:
    if not provenance:
        return label
    src = provenance.get("source_id", "")
    as_of = provenance.get("as_of", "")
    xform = provenance.get("transformation", "")
    details = " ".join(part for part in (src, str(as_of), xform) if part)
    return f"{label} (i): {details}".strip()


__all__ = ["format_tooltip"]
