"""Unit tests for build_plan.md Phase 4: Bhāvapada family (A1-A12) +
Graha Arūḍha calculator (app.derived.bhavapada).
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.derived.bhavapada import bhava_arudha_family, bhavapada_report, graha_arudha_family
from app.derived.factors import build_chart_context
from app.fixtures import list_fixture_ids, load_chart_fixture


def _ctx(fixture_id: str):
    return build_chart_context(load_chart_fixture(fixture_id))


def test_bhava_arudha_family_has_all_12_houses():
    ctx = _ctx("ajay_kumar")
    family = bhava_arudha_family(ctx["lagna_sign"], ctx["chart"])
    assert set(family.keys()) == {f"A{h}" for h in range(1, 13)}


def test_a1_matches_existing_lagna_pada_exactly():
    """A1 IS the Aru\u1e0dha Lagna -- must byte-match app.derived.factors.lagna_pada's
    own independently-verified output, since bhava_arudha_family just calls
    the same underlying arudha_pada() function."""
    from app.derived.factors import lagna_pada

    for fixture_id in list_fixture_ids():
        ctx = _ctx(fixture_id)
        family = bhava_arudha_family(ctx["lagna_sign"], ctx["chart"])
        expected = lagna_pada(ctx["lagna_sign"], ctx["chart"])
        assert family["A1"] == expected


def test_a12_matches_existing_upapada_lagna_canonical_formula():
    """A12 IS Upapada Lagna (Jaimini's specific name for the 12th house's
    Aru\u1e0dha) -- must match app.derived.factors.upapada_lagna exactly."""
    from app.derived.factors import upapada_lagna

    for fixture_id in list_fixture_ids():
        ctx = _ctx(fixture_id)
        family = bhava_arudha_family(ctx["lagna_sign"], ctx["chart"])
        expected = upapada_lagna(ctx["lagna_sign"], ctx["chart"])
        assert family["A12"] == expected


def test_graha_arudha_family_covers_7_classical_planets():
    ctx = _ctx("ajay_kumar")
    family = graha_arudha_family(ctx["lagna_sign"], ctx["chart"])
    assert set(family.keys()) == {"Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"}


def test_graha_arudha_source_house_matches_planet_occupied_house():
    for fixture_id in list_fixture_ids():
        ctx = _ctx(fixture_id)
        family = graha_arudha_family(ctx["lagna_sign"], ctx["chart"])
        for planet, arudha in family.items():
            assert arudha["source_house"] == ctx["chart"][planet]["house"]


def test_bhavapada_report_wired_into_chart_context():
    for fixture_id in list_fixture_ids():
        ctx = _ctx(fixture_id)
        assert "bhavapada" in ctx
        assert len(ctx["bhavapada"]["bhava_arudhas"]) == 12
        assert len(ctx["bhavapada"]["graha_arudhas"]) == 7
        assert ctx["bhavapada"]["aliases"] == {"AL": "A1", "UL": "A12"}


def test_bhavapada_report_no_exceptions_across_every_fixture():
    for fixture_id in list_fixture_ids():
        ctx = _ctx(fixture_id)
        report = bhavapada_report(ctx["lagna_sign"], ctx["chart"])
        assert report["bhava_arudhas"]["A1"]["pada_sign"] >= 1


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
