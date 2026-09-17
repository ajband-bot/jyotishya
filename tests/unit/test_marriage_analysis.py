"""Unit tests for app.derived.marriage_analysis -- single-chart Five-
Pillar Marriage Framework, build_plan.md Phase 6.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.derived.factors import build_chart_context
from app.derived.marriage_analysis import five_pillar_marriage_report, married_life_status
from app.fixtures import list_fixture_ids, load_chart_fixture


def _ctx(chart_id: str):
    return build_chart_context(load_chart_fixture(chart_id))


def test_all_five_pillars_present_for_every_fixture():
    for chart_id in list_fixture_ids():
        ctx = _ctx(chart_id)
        report = five_pillar_marriage_report(ctx)
        assert set(report.keys()) >= {
            "seventh_house", "seventh_lord", "venus_karaka", "jupiter_karaka", "darakaraka", "upapada",
        }


def test_seventh_lord_matches_house_lords_and_lord_placements():
    ctx = _ctx("ajay_kumar")
    report = five_pillar_marriage_report(ctx)
    assert report["seventh_lord"]["planet"] == ctx["house_lords"][7]
    assert report["seventh_lord"]["occupies_house"] == ctx["lord_placements"][7]["occupies_house"]


def test_darakaraka_matches_karakas_and_d9():
    ctx = _ctx("ajay_kumar")
    report = five_pillar_marriage_report(ctx)
    assert report["darakaraka"]["planet"] == ctx["karakas"]["darakaraka"]
    assert report["darakaraka"]["d9_sign_en"] == ctx["d9"]["dk_d9_sign_en"]


def test_upapada_matches_canonical_upapada():
    ctx = _ctx("ajay_kumar")
    report = five_pillar_marriage_report(ctx)
    assert report["upapada"]["sign"] == ctx["upapada"]["canonical"]["pada_sign"]


def test_venus_and_jupiter_karaka_reports_are_always_both_present_and_gender_labeled():
    ctx = _ctx("sandeep_0700")
    report = five_pillar_marriage_report(ctx)
    assert report["venus_karaka"]["applies_to_native_gender"] == "male"
    assert report["jupiter_karaka"]["applies_to_native_gender"] == "female"
    assert report["venus_karaka"]["house"] == ctx["chart"]["Venus"]["house"]
    assert report["jupiter_karaka"]["house"] == ctx["chart"]["Jupiter"]["house"]


def test_dominant_influence_is_one_of_the_four_valid_labels():
    for chart_id in list_fixture_ids():
        ctx = _ctx(chart_id)
        report = five_pillar_marriage_report(ctx)
        assert report["seventh_house"]["dominant_influence"] in ("benefic", "malefic", "mixed", "neutral")


def test_married_life_status_returns_strengths_and_cautions_for_every_fixture():
    for chart_id in list_fixture_ids():
        ctx = _ctx(chart_id)
        status = married_life_status(ctx)
        assert isinstance(status["strengths"], list)
        assert isinstance(status["cautions"], list)
        for bucket in (status["strengths"], status["cautions"]):
            for item in bucket:
                assert {"area", "note", "citation"} <= set(item.keys())


def test_married_life_status_reuses_five_pillar_report_verbatim():
    ctx = _ctx("ajay_kumar")
    status = married_life_status(ctx)
    pillars = five_pillar_marriage_report(ctx)
    assert status["five_pillar_summary"] == pillars


def test_married_life_status_active_doshas_only_includes_present_ones():
    ctx = _ctx("ajay_kumar")
    status = married_life_status(ctx)
    for dosha_name, dosha_data in status["active_doshas"].items():
        assert dosha_data.get("present") is True


def test_married_life_status_current_dasha_matches_context():
    ctx = _ctx("ajay_kumar")
    status = married_life_status(ctx)
    current = ctx.get("current_dasha") or {}
    assert status["current_dasha"]["mahadasha"] == (current.get("mahadasha") or {}).get("planet")


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
