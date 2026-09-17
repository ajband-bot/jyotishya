"""Unit tests for app.derived.career_analysis -- Career Analysis Framework,
build_plan.md Phase 6.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.derived.career_analysis import TENTH_HOUSE_OCCUPANT_PROFESSION, career_analysis_report
from app.derived.factors import build_chart_context
from app.fixtures import list_fixture_ids, load_chart_fixture


def _ctx(chart_id: str):
    return build_chart_context(load_chart_fixture(chart_id))


def test_all_9_planets_covered_by_occupant_profession_table():
    assert set(TENTH_HOUSE_OCCUPANT_PROFESSION.keys()) == {
        "Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu",
    }


def test_tenth_lord_matches_house_lords_and_lord_placements():
    ctx = _ctx("ajay_kumar")
    report = career_analysis_report(ctx)
    assert report["tenth_lord"]["planet"] == ctx["house_lords"][10]
    assert report["tenth_lord"]["occupies_house"] == ctx["lord_placements"][10]["occupies_house"]


def test_tenth_house_occupants_match_chart_directly():
    for chart_id in list_fixture_ids():
        ctx = _ctx(chart_id)
        report = career_analysis_report(ctx)
        expected = [p for p in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
                    if ctx["chart"][p]["house"] == 10]
        assert report["tenth_house"]["occupants"] == expected
        assert set(report["tenth_house"]["profession_flavors"].keys()) == set(expected)


def test_natural_significations_reused_from_karakatva_verbatim():
    from app.knowledge.planets import KARAKATVA

    ctx = _ctx("ajay_kumar")
    report = career_analysis_report(ctx)
    lord = report["tenth_lord"]["planet"]
    assert report["tenth_lord"]["natural_significations"] == KARAKATVA[lord]["professions"]


def test_data_gap_for_a10_d10_is_honestly_disclosed():
    ctx = _ctx("ajay_kumar")
    report = career_analysis_report(ctx)
    assert any("A10" in gap and "D10" in gap for gap in report["data_gaps"])


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
