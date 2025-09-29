from __future__ import annotations

from west_housing_model.settings import get_pillar_weights, get_returns_weights


def test_pillar_weights_defaults_and_normalization(monkeypatch) -> None:
    # No env vars → equal weights
    w = get_pillar_weights()
    assert sum(w.values()) == 1.0
    assert all(abs(v - 0.25) < 1e-9 for v in w.values())

    # Override to non-normalized values and check normalization
    monkeypatch.setenv("WHM_PILLAR_WEIGHT_UC", "2.0")
    monkeypatch.setenv("WHM_PILLAR_WEIGHT_OA", "1.0")
    monkeypatch.setenv("WHM_PILLAR_WEIGHT_IJ", "1.0")
    monkeypatch.setenv("WHM_PILLAR_WEIGHT_SC", "0.0")
    w2 = get_pillar_weights()
    assert abs(sum(w2.values()) - 1.0) < 1e-9
    assert w2["pillar_uc"] > w2["pillar_oa"] > w2["pillar_sc"]


def test_returns_weights_defaults_and_normalization(monkeypatch) -> None:
    rw = get_returns_weights()
    assert abs(rw.yoy_yoc + rw.irr_5yr + rw.dscr - 1.0) < 1e-9

    monkeypatch.setenv("WHM_RETURNS_WEIGHT_YOC", "1.0")
    monkeypatch.setenv("WHM_RETURNS_WEIGHT_IRR", "1.0")
    monkeypatch.setenv("WHM_RETURNS_WEIGHT_DSCR", "0.0")
    rw2 = get_returns_weights()
    assert abs(rw2.yoy_yoc + rw2.irr_5yr + rw2.dscr - 1.0) < 1e-9
    assert rw2.yoy_yoc >= rw2.irr_5yr >= rw2.dscr


