from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, MutableMapping, cast

import pandas as pd

from west_housing_model.config import load_data_dictionary, load_registry
from west_housing_model.settings import get_pillar_weights
from west_housing_model.ui import (
    SPEC_VERSION,
    build_manifest,
    deterministic_export_filename,
    export_csv,
    load_scenario,
    save_scenario,
)
from west_housing_model.ui.components import (
    format_tooltip,  # noqa: F401 (placeholder for future UI)
)
from west_housing_model.ui.state import Scenario
from west_housing_model.valuation import ValuationInputs, run_valuation


def _run_evaluate(scenario_payload: dict[str, Any]) -> pd.DataFrame:
    inputs = ValuationInputs(
        scenario_id=scenario_payload.get("scenario_id", ""),
        property_id=scenario_payload.get("property_id", ""),
        as_of=(
            pd.to_datetime(scenario_payload.get("as_of")) if scenario_payload.get("as_of") else None
        ),
        place_features=scenario_payload.get("place_features", {}),
        site_features=scenario_payload.get("site_features", {}),
        ops_features=scenario_payload.get("ops_features", {}),
        user_overrides=scenario_payload.get("user_overrides", {}),
    )
    return run_valuation(inputs)


def _build_provenance_from_inputs(payload: dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    prov: Dict[str, Dict[str, Any]] = {}
    pf = payload.get("place_features", {}) or {}
    if pf:
        prov["aker_market_fit"] = {
            "source_id": pf.get("source_id"),
            "as_of": pf.get("as_of"),
            "transformation": "score-aggregation",
        }
    uf = payload.get("user_overrides", {}) or {}
    if uf:
        for key in ("rent_baseline", "cap_base"):
            prov[key] = {
                "source_id": "user.override",
                "as_of": payload.get("as_of"),
                "transformation": "manual-input",
            }
    return prov


def page_explore() -> Dict[str, Any]:  # pragma: no cover - requires Streamlit
    import streamlit as st

    st.title("Explore")
    st.caption("Browse places and properties with simple filters")

    # Minimal placeholder data
    df = pd.DataFrame(
        {
            "place": ["Example MSA"],
            "aker_market_fit": [80],
            "msa_jobs_t12": [0.02],
            "permits_5plus_per_1k_hh_t12": [1.2],
        }
    )
    min_fit = st.slider("Min Aker Fit", 0, 100, 60)
    st.dataframe(df[df["aker_market_fit"] >= min_fit])
    return {"filters": {"min_fit": min_fit}}


def page_evaluate() -> Dict[str, Any]:  # pragma: no cover - requires Streamlit
    import streamlit as st

    st.title("Evaluate")
    st.caption("Edit a few inputs and compute valuation")

    # Offline and cache status (basic UX)
    offline = st.sidebar.checkbox("Offline mode", value=False)
    if offline:
        st.sidebar.warning("Offline (cache only)")
    else:
        st.sidebar.success("Online")

    # Inputs (simple subset)
    scenario_id = st.text_input("Scenario ID", value="scn-1")
    property_id = st.text_input("Property ID", value="prop-1")
    as_of = st.date_input("As of")
    af = st.number_input("Aker Fit", min_value=0, max_value=100, value=75)
    rent = st.number_input("Rent baseline ($)", min_value=0.0, value=1500.0)
    units = st.number_input("Units", min_value=1, value=100)
    cap = st.number_input("Cap rate (base)", min_value=0.01, value=0.065)

    if st.button("Run valuation"):
        payload = {
            "scenario_id": scenario_id,
            "property_id": property_id,
            "as_of": str(as_of),
            "place_features": {"aker_market_fit": int(af)},
            "site_features": {},
            "ops_features": {},
            "user_overrides": {
                "rent_baseline": float(rent),
                "units": int(units),
                "cap_base": float(cap),
            },
        }
        prov = _build_provenance_from_inputs(payload)
        # Re-render inputs with provenance tooltips
        st.caption(format_tooltip("Aker Fit", prov.get("aker_market_fit")))
        st.caption(format_tooltip("Rent Baseline", prov.get("rent_baseline")))
        st.caption(format_tooltip("Cap Rate (base)", prov.get("cap_base")))
        import time

        t0 = time.perf_counter()

        # Cache evaluation by payload signature
        if TYPE_CHECKING:

            def _cached_eval(p: dict[str, Any]) -> pd.DataFrame:
                return _run_evaluate(p)

        else:

            @st.cache_data
            def _cached_eval(p: dict[str, Any]) -> pd.DataFrame:
                return _run_evaluate(p)

        out = _cached_eval(payload)
        dt = time.perf_counter() - t0
        st.dataframe(out)
        st.caption(f"Computed in {dt*1000:.1f} ms")
    return {}


def page_scenarios() -> Dict[str, Any]:  # pragma: no cover - requires Streamlit
    import streamlit as st

    st.title("Scenarios")
    st.caption("Save and load scenarios; persist to disk")

    store = cast(MutableMapping[str, Any], st.session_state.setdefault("whm", {}))
    loaded = load_scenario(store)
    st.write("Loaded:", loaded)

    scenario_json = st.text_area("Scenario JSON", value="{}", height=200)
    if st.button("Save to session"):
        try:
            payload = json.loads(scenario_json)
        except Exception as exc:
            st.error(f"Invalid JSON: {exc}")
        else:
            scenario_obj = Scenario(
                scenario_id=str(payload.get("scenario_id", "")),
                property_id=str(payload.get("property_id", "")),
                as_of=(pd.to_datetime(payload.get("as_of")) if payload.get("as_of") else None),
                user_overrides=dict(payload.get("user_overrides", {})),
                source_manifest=dict(payload.get("source_manifest", {})),
            )
            save_scenario(store, scenario_obj)
            st.success("Saved to session state")

    if st.button("Export CSV"):
        try:
            payload = json.loads(scenario_json)
            out = _run_evaluate(payload)
            manifest = build_manifest(
                as_of=pd.Timestamp(payload.get("as_of") or pd.Timestamp.now()), sources={}
            )
            st.download_button(
                "Download CSV",
                export_csv(out, manifest=manifest),
                file_name=deterministic_export_filename(
                    "csv", payload.get("scenario_id", "scn"), manifest["as_of"]
                ),
            )
        except Exception as exc:
            st.error(str(exc))
    return {}


def page_settings() -> Dict[str, Any]:  # pragma: no cover - requires Streamlit
    import streamlit as st

    st.title("Settings")
    st.caption("Data dictionary and pillar weights")

    try:
        reg = load_registry(Path("config/sources.yml"), Path("config/sources_supplement.yml"))
        dd = load_data_dictionary(reg)
    except Exception:
        dd = []
    st.subheader("Data Dictionary")
    st.json(dd)

    st.subheader("Pillar Weights")
    st.json(get_pillar_weights())
    st.caption(f"Spec version: {SPEC_VERSION}")
    return {}


def main() -> int:  # pragma: no cover - UI entrypoint would be exercised manually
    try:
        import streamlit as st
    except Exception:
        # Fallback: CLI-style single-run from a scenario JSON if present
        scenario_path = Path("scenario.sample.json")
        if scenario_path.exists():
            payload = json.loads(scenario_path.read_text())
            df = _run_evaluate(payload)
            print(df.to_json(orient="records"))
            return 0
        print(
            "Install streamlit and run 'streamlit run -m west_housing_model.ui.app' to launch UI."
        )
        return 0

    st.set_page_config(page_title="West Housing Model", layout="wide")
    tab = st.sidebar.radio("Pages", ("Explore", "Evaluate", "Scenarios", "Settings"))
    if tab == "Explore":
        page_explore()
    elif tab == "Evaluate":
        page_evaluate()
    elif tab == "Scenarios":
        page_scenarios()
    elif tab == "Settings":
        page_settings()
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
