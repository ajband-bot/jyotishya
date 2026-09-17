"""Unit tests for the classical Panchanga engine -- app/astro/panchanga.py.

Per build_plan.md Phase 1: "Full Panchanga (tithi/nakshatra/yoga/karana/vara
-- cross-check against panchanga/drik.py)". Boundary arithmetic is the real
risk here (not a big data table like Ashtakavarga), so these tests pin down
exact index/name transitions at the classical arc boundaries.
"""
from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.astro.panchanga import (
    TITHI_NAMES,
    YOGA_NAMES,
    compute_karana,
    compute_nakshatra_limb,
    compute_panchanga,
    compute_tithi,
    compute_vara,
    compute_yoga,
)
from app.derived.factors import build_chart_context
from app.fixtures import list_fixture_ids, load_chart_fixture


def test_tithi_boundaries_new_moon_full_moon_and_wrap():
    assert compute_tithi(0.0, 0.0)["number"] == 1  # conjunction -> Pratipada
    assert compute_tithi(0.0, 0.0)["paksha"] == "Shukla"
    assert compute_tithi(0.0, 0.0)["name"] == "Pratipada"

    full_moon = compute_tithi(0.0, 179.9)  # just short of exact opposition -> Purnima
    assert full_moon["number"] == 15
    assert full_moon["name"] == "Purnima"

    exact_opposition = compute_tithi(0.0, 180.0)  # exact full-moon instant is the
    # END of Purnima / START of Krishna Pratipada -- classically correct, not a bug.
    assert exact_opposition["number"] == 16
    assert exact_opposition["paksha"] == "Krishna"
    assert exact_opposition["name"] == "Pratipada"

    new_moon_edge = compute_tithi(0.0, 359.9)  # just short of full cycle -> Amavasya
    assert new_moon_edge["number"] == 30
    assert new_moon_edge["paksha"] == "Krishna"
    assert new_moon_edge["name"] == "Amavasya"


def test_tithi_names_cover_first_half_of_each_paksha():
    for ordinal, expected_name in enumerate(TITHI_NAMES, start=1):
        diff = (ordinal - 1) * 12.0 + 1.0  # 1 deg into that tithi's span
        assert compute_tithi(0.0, diff)["name"] == expected_name


def test_yoga_boundaries_wrap_correctly():
    assert compute_yoga(0.0, 0.0)["number"] == 1
    assert compute_yoga(0.0, 0.0)["name"] == "Vishkumbha"
    last = compute_yoga(0.0, 359.9)
    assert last["number"] == 27
    assert last["name"] == "Vaidhriti"
    assert len(YOGA_NAMES) == 27


def test_karana_fixed_head_and_tail_and_cyclic_body():
    # Kimstughna: only the very first half-tithi of the lunation.
    assert compute_karana(0.0, 0.0)["number"] == 1
    assert compute_karana(0.0, 0.0)["name"] == "Kimstughna"

    # Second half of tithi 1 (diff in [6,12)) -> first cyclic karana, Bava.
    second_half = compute_karana(0.0, 7.0)
    assert second_half["number"] == 2
    assert second_half["name"] == "Bava"

    # Last three half-tithis of the lunation are the fixed tail triplet.
    shakuni = compute_karana(0.0, 342.0)  # index 58
    chatushpada = compute_karana(0.0, 348.0)  # index 59
    naga = compute_karana(0.0, 354.0)  # index 60
    assert (shakuni["number"], shakuni["name"]) == (58, "Shakuni")
    assert (chatushpada["number"], chatushpada["name"]) == (59, "Chatushpada")
    assert (naga["number"], naga["name"]) == (60, "Naga")


def test_vara_known_weekday_cross_check():
    """1987-12-31 is an independently-verifiable Thursday (Python's own
    date.weekday() agrees) -- pins the Sunday=0 convention correctly."""
    result = compute_vara(date(1987, 12, 31))
    assert result["name"] == "Thursday"
    assert result["lord"] == "Jupiter"
    assert result["day_boundary"] == "civil_midnight"


def test_nakshatra_limb_matches_engine_get_nakshatra():
    limb = compute_nakshatra_limb(41.0)  # comfortably inside Rohini's 1st pada (40-43.33 deg)
    assert limb["name"] == "Rohini"
    assert limb["lord"] == "Moon"
    assert limb["pada"] == 1
    assert 1 <= limb["number"] <= 27


def test_compute_panchanga_full_wiring_for_every_golden_fixture():
    for fixture_id in list_fixture_ids():
        fixture = load_chart_fixture(fixture_id)
        context = build_chart_context(fixture)
        panchanga = context["panchanga"]
        assert 1 <= panchanga["tithi"]["number"] <= 30
        assert panchanga["tithi"]["paksha"] in {"Shukla", "Krishna"}
        assert 1 <= panchanga["nakshatra"]["number"] <= 27
        assert 1 <= panchanga["yoga"]["number"] <= 27
        assert 1 <= panchanga["karana"]["number"] <= 60
        assert panchanga["vara"]["name"] in {
            "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday",
        }


def test_compute_panchanga_direct_matches_context_wiring():
    fixture = load_chart_fixture("ajay_kumar")
    context = build_chart_context(fixture)
    chart = context["chart"]
    from datetime import date as _date

    direct = compute_panchanga(chart["Sun"]["longitude"], chart["Moon"]["longitude"], _date.fromisoformat(str(fixture["dob"])))
    assert direct == context["panchanga"]


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
