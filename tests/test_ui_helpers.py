import pandas as pd

from west_housing_model.ui import (
    SPEC_VERSION,
    build_manifest,
    choose_manifest,
    deterministic_export_filename,
    export_csv,
    export_pdf_onepager,
    load_scenario,
)


def test_manifest_and_filenames():
    manifest = build_manifest(as_of=pd.Timestamp("2025-09-01"), sources={"census_acs": "2023-12"})
    assert manifest["as_of"] == "2025-09"
    assert manifest["sources"]["census_acs"] == "2023-12"
    assert deterministic_export_filename("csv", "scn1", "2025-09") == "valuation-scn1-2025-09.csv"
    assert deterministic_export_filename("pdf", "scn1", "2025-09") == "valuation-scn1-2025-09-onepager.pdf"


def test_choose_manifest_locked_and_unlocked():
    saved = {"as_of": "2025-08", "sources": {"x": "1"}}
    current = {"as_of": "2025-09", "sources": {"x": "2"}}
    assert choose_manifest(locked=True, saved_manifest=saved, current_manifest=current) == saved
    assert choose_manifest(locked=False, saved_manifest=saved, current_manifest=current) == current


def test_save_and_load_scenario_roundtrip():
    store = {}
    scn = {
        "scenario_id": "scn1",
        "property_id": "prop1",
        "as_of": pd.Timestamp("2025-09-01"),
        "user_overrides": {"target_rent": 1500},
        "source_manifest": {"as_of": "2025-09", "sources": {}},
    }
    # save
    from west_housing_model.ui.state import Scenario, save_scenario  # type: ignore

    save_scenario(store, Scenario(**scn))
    # load
    loaded = load_scenario(store)
    assert loaded is not None
    assert loaded.spec_version == SPEC_VERSION
    assert loaded.scenario_id == "scn1"
    assert str(loaded.as_of)[:7] == "2025-09"


def test_exporters_embed_manifest(tmp_path):
    frame = pd.DataFrame({"a": [1]})
    manifest = {"as_of": "2025-09", "sources": {"x": "1"}}
    csv_bytes = export_csv(frame, manifest=manifest)
    assert b"source_manifest" in csv_bytes
    pdf_bytes = export_pdf_onepager("Summary", manifest=manifest)
    assert b"Sources & Vintages" in pdf_bytes


