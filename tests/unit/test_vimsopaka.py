"""Unit tests for app.derived.vimsopaka -- classical 20-point Vimsopaka
Bala across 4 schemes (build_plan.md Phase 5).
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.derived.factors import build_chart_context
from app.derived.vimsopaka import (
    CLASSICAL_7,
    VIMSOPAKA_SCHEMES,
    all_schemes_vimsopaka_bala,
    vimsopaka_bala,
)
from app.fixtures import load_chart_fixture


def _chart(chart_id: str):
    return build_chart_context(load_chart_fixture(chart_id))["chart"]


def test_all_4_schemes_sum_to_exactly_20():
    """Regression guard for the module-load-time assertion itself --
    cross-checked against PyJHora's const.py amsa_vimsopaka tables."""
    for scheme, weights in VIMSOPAKA_SCHEMES.items():
        assert round(sum(weights.values()), 6) == 20, scheme


def test_vimsopaka_bala_covers_all_7_classical_planets_plus_node_data_gap():
    chart = _chart("ajay_kumar")
    result = vimsopaka_bala(chart, scheme="shadvarga")
    for planet in CLASSICAL_7:
        assert "total" in result["planets"][planet]
        assert 0.0 <= result["planets"][planet]["total"] <= 20.0
    for node in ("Rahu", "Ketu"):
        assert result["planets"][node]["model"] == "data_gap"


def test_mars_own_sign_d1_contributes_full_weight_in_shadvarga():
    """Ajay's Mars is in Scorpio (own sign) in D1 -- the D1 breakdown entry
    must show full 20/20 dignity points and a contribution equal to the
    scheme's own D1 weight (6 for shadvarga)."""
    chart = _chart("ajay_kumar")
    result = vimsopaka_bala(chart, scheme="shadvarga")
    d1_entry = result["planets"]["Mars"]["breakdown"]["D1"]
    assert d1_entry["dignity_points_of_20"] == 20
    assert d1_entry["contribution"] == 6.0


def test_unknown_scheme_raises():
    chart = _chart("ajay_kumar")
    try:
        vimsopaka_bala(chart, scheme="not_a_real_scheme")
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_all_schemes_helper_returns_all_4():
    chart = _chart("ajay_kumar")
    result = all_schemes_vimsopaka_bala(chart)
    assert set(result.keys()) == set(VIMSOPAKA_SCHEMES.keys())


def test_verdict_bands_are_internally_consistent():
    chart = _chart("sandeep_0700")
    result = vimsopaka_bala(chart, scheme="shadvarga")
    for planet in CLASSICAL_7:
        entry = result["planets"][planet]
        if entry["total"] >= 15:
            assert entry["verdict"] == "uttama"
        elif entry["total"] >= 10:
            assert entry["verdict"] == "madhyama"
        else:
            assert entry["verdict"] == "adhama"


if __name__ == "__main__":
    import traceback

    tests = [obj for name, obj in list(globals().items()) if name.startswith("test_")]
    failed = 0
    for t in tests:
        try:
            t()
            print(f"[PASS] {t.__name__}")
        except Exception:
            failed += 1
            print(f"[FAIL] {t.__name__}")
            traceback.print_exc()
    print(f"\n{len(tests) - failed}/{len(tests)} passed")
    raise SystemExit(1 if failed else 0)
