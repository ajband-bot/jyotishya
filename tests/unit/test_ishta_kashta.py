"""Unit tests for app.derived.ishta_kashta -- classical Ishta/Kashta Phala
(BPHS Ch.28), build_plan.md Phase 6.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.derived.factors import build_chart_context
from app.derived.ishta_kashta import (
    _fold,
    _rasmi,
    classical_ishta_kashta,
    ishta_phala,
    kashta_phala,
)
from app.fixtures import list_fixture_ids, load_chart_fixture


def _chart(chart_id: str):
    return build_chart_context(load_chart_fixture(chart_id))["chart"]


def test_fold_never_exceeds_180():
    for d in (0, 90, 180, 181, 270, 359, 360):
        assert 0 <= _fold(d) <= 180


def test_rasmi_bounds_are_1_to_7():
    assert _rasmi(0) == 1.0
    assert _rasmi(180) == 7.0
    assert _rasmi(90) == 4.0


def test_ishta_kashta_sum_to_exactly_60():
    for uchcha in (1.0, 3.5, 7.0):
        for cheshta in (1.0, 4.2, 7.0):
            ishta = ishta_phala(uchcha, cheshta)
            kashta = kashta_phala(ishta)
            assert round(ishta + kashta, 4) == 60.0


def test_ishta_phala_max_and_min():
    assert ishta_phala(7.0, 7.0) == 60.0
    assert ishta_phala(1.0, 1.0) == 0.0


def test_sun_and_moon_are_classical_for_every_fixture():
    for chart_id in list_fixture_ids():
        chart = _chart(chart_id)
        result = classical_ishta_kashta({"chart": chart})
        for planet in ("Sun", "Moon"):
            entry = result["planets"][planet]
            assert entry["model"] == "classical"
            assert 0.0 <= entry["ishta_phala"] <= 60.0
            assert round(entry["ishta_phala"] + entry["kashta_phala"], 4) == 60.0
            assert 1.0 <= entry["uchcha_rasmi"] <= 7.0
            assert 1.0 <= entry["cheshta_rasmi"] <= 7.0


def test_five_non_luminaries_are_disclosed_data_gap():
    chart = _chart("ajay_kumar")
    result = classical_ishta_kashta({"chart": chart})
    for planet in ("Mars", "Mercury", "Jupiter", "Venus", "Saturn"):
        entry = result["planets"][planet]
        assert entry["model"] == "data_gap"
        assert entry["cheshta_rasmi"] is None
        assert entry["ishta_phala"] is None
        # Uchcha Rasmi alone IS fully computable even for these 5 -- only
        # Cheshta Rasmi (motion-tier dependent) is the disclosed gap.
        assert 1.0 <= entry["uchcha_rasmi"] <= 7.0


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
