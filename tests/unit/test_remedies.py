"""Unit tests for app.derived.remedies -- Remedy Safety Rules engine,
build_plan.md Phase 6. Safety-critical: these tests exist to catch any
regression that would recommend a gemstone for a functional malefic.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.derived.factors import build_chart_context
from app.derived.remedies import CLASSICAL_7, remedy_report
from app.fixtures import list_fixture_ids, load_chart_fixture


def _ctx(chart_id: str):
    return build_chart_context(load_chart_fixture(chart_id))


def test_functional_malefic_never_gets_gemstone_appropriate_true():
    """Remedy Safety Rule 1 -- the single most important gate. Checked
    across every fixture and every classical planet, not just one case."""
    for chart_id in list_fixture_ids():
        ctx = _ctx(chart_id)
        report = remedy_report(ctx)
        for planet in CLASSICAL_7:
            entry = report["planets"][planet]
            if entry["classification"] == "functional_malefic":
                assert entry["gemstone_appropriate"] is False, f"{chart_id}:{planet}"
                assert entry["gemstone_contraindicated"] is True, f"{chart_id}:{planet}"


def test_ketu_always_contraindicated_no_fabricated_exception():
    for chart_id in list_fixture_ids():
        ctx = _ctx(chart_id)
        report = remedy_report(ctx)
        assert report["planets"]["Ketu"]["gemstone_appropriate"] is False
        assert report["planets"]["Ketu"]["gemstone_contraindicated"] is True


def test_rahu_gemstone_appropriate_is_always_false_regardless_of_exception():
    """Rule 7's exception is NECESSARY but not by itself SUFFICIENT --
    gemstone_appropriate for Rahu is always reported False; the exception
    condition is surfaced separately (well_placed_and_strong_dispositor)."""
    for chart_id in list_fixture_ids():
        ctx = _ctx(chart_id)
        report = remedy_report(ctx)
        assert report["planets"]["Rahu"]["gemstone_appropriate"] is False


def test_saturn_requires_yoga_karaka_not_merely_functional_benefic():
    ctx = _ctx("ajay_kumar")
    report = remedy_report(ctx)
    saturn = report["planets"]["Saturn"]
    if saturn["classification"] == "functional_benefic":
        assert saturn["blocked_by_yogakaraka_gate"] is True
        assert saturn["gemstone_appropriate"] is False


def test_mantra_and_priority_order_always_present_for_all_9_planets():
    ctx = _ctx("ajay_kumar")
    report = remedy_report(ctx)
    for planet, entry in report["planets"].items():
        assert entry["mantra"]
        assert entry["priority_order"][0] == "mantra"
        assert entry["priority_order"][-2] == "yantra"


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
