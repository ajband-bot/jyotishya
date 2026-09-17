"""Unit tests for app.derived.gochara -- full 9-planet transit report
(build_plan.md Phase 5: "Transit engine -- gochara + Sade Sati status").
"""
from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.derived.factors import build_chart_context
from app.derived.gochara import ALL_9_PLANETS, gochara_report
from app.fixtures import load_chart_fixture


def _ctx(chart_id: str, today: date):
    return build_chart_context(load_chart_fixture(chart_id), today=today)


def test_gochara_report_covers_all_9_planets():
    ctx = _ctx("ajay_kumar", date(2026, 9, 16))
    report = gochara_report(ctx)
    assert set(report["planets"].keys()) == set(ALL_9_PLANETS)


def test_rahu_ketu_are_simple_method_only_data_gap_disclosed():
    """Classical Parashari Ashtakavarga has no Rahu/Ketu row -- must be
    disclosed, never silently backfilled with another planet's bindus."""
    ctx = _ctx("ajay_kumar", date(2026, 9, 16))
    report = gochara_report(ctx)
    for node in ("Rahu", "Ketu"):
        assert report["planets"][node]["ashtakavarga_gochara"]["model"] == "data_gap"
        assert report["planets"][node]["combined_verdict"] == "simple_method_only"
        assert report["planets"][node]["methods_agree"] is None


def test_classical_7_planets_have_a_combined_verdict_from_both_methods():
    ctx = _ctx("ajay_kumar", date(2026, 9, 16))
    report = gochara_report(ctx)
    for planet in ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"):
        verdict = report["planets"][planet]["combined_verdict"]
        assert verdict in {
            "favorable_both_methods_agree", "challenging_both_methods_agree",
            "methods_disagree", "ashtakavarga_mixed_simple_favorable", "ashtakavarga_mixed_simple_unfavorable",
        }


def test_sade_sati_surfaced_in_gochara_report():
    ctx = _ctx("ajay_kumar", date(2026, 9, 16))
    report = gochara_report(ctx)
    assert "active" in report["sade_sati"]


def test_moon_simple_gochara_matches_openjyotish_cross_check():
    """Regression guard for the one row explicitly cross-checked against
    OpenJyotish's calc/muhurta.py _CHANDRA_BALA_GOOD_HOUSES."""
    from app.astro.transits import SIMPLE_GOCHARA_GOOD_HOUSES
    assert SIMPLE_GOCHARA_GOOD_HOUSES["Moon"] == {1, 3, 6, 7, 10, 11}


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
