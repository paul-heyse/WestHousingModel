"""UI package: non-UI helpers are importable in tests without Streamlit.

Exports only pure helpers by default to avoid hard dependency on Streamlit
for non-interactive contexts (e.g., pytest, CLI).
"""

from .exporters import export_csv, export_pdf_onepager
from .state import (
    SPEC_VERSION,
    build_manifest,
    choose_manifest,
    deterministic_export_filename,
    load_scenario,
    save_scenario,
)

__all__ = [
    "SPEC_VERSION",
    "build_manifest",
    "choose_manifest",
    "deterministic_export_filename",
    "load_scenario",
    "save_scenario",
    "export_csv",
    "export_pdf_onepager",
]
