from __future__ import annotations

import importlib
import sys
import types
from datetime import date


class _Sidebar:
    def checkbox(self, *_, **__) -> bool:
        return False

    def warning(self, *_, **__) -> None:
        return None

    def success(self, *_, **__) -> None:
        return None

    def radio(self, *_, **__) -> str:
        return "Explore"


def _no_op(*_, **__) -> None:
    return None


def _return_value(value):
    def _inner(*_, **__):
        return value

    return _inner


def _cache_data(func=None, **__):
    def decorator(fn):
        return fn

    if func is not None:
        return decorator(func)
    return decorator


def test_streamlit_pages_smoke(monkeypatch) -> None:
    stub = types.ModuleType("streamlit")
    stub.title = _no_op
    stub.caption = _no_op
    stub.slider = _return_value(60)
    stub.dataframe = _no_op
    stub.checkbox = _return_value(False)
    stub.number_input = _return_value(1)
    stub.text_input = _return_value("scn-1")
    stub.date_input = _return_value(date(2025, 1, 1))
    stub.button = _return_value(False)
    stub.sidebar = _Sidebar()
    stub.session_state = {}
    stub.cache_data = _cache_data
    stub.status = _no_op
    stub.json = _no_op
    stub.subheader = _no_op
    stub.write = _no_op
    stub.text_area = _return_value("{}")
    stub.download_button = _no_op
    stub.set_page_config = _no_op

    original = sys.modules.get("streamlit")
    monkeypatch.setitem(sys.modules, "streamlit", stub)

    app = importlib.import_module("west_housing_model.ui.app")
    importlib.reload(app)

    assert isinstance(app.page_explore(), dict)
    assert isinstance(app.page_evaluate(), dict)
    assert isinstance(app.page_scenarios(), dict)
    assert isinstance(app.page_settings(), dict)

    if original is not None:
        monkeypatch.setitem(sys.modules, "streamlit", original)
    else:
        sys.modules.pop("streamlit", None)
