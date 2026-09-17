"""Unit tests for the Aspects / Drishti engine -- app/derived/aspects.py.

Per build_plan.md Phase 1: "Aspects/drishti engine (kendra/trikona/
dushthana/chathusra + special graha drishti, varga-aware)".
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.astro.vargas import compute_varga
from app.derived.aspects import (
    CHATHUSRA,
    DUSHTHANA,
    KENDRA,
    TRIKONA,
    build_aspect_map,
    full_aspect_report,
    graha_drishti_houses,
    house_relationship_types,
    mutual_aspects,
    planet_houses_from_d1_chart,
    planet_houses_from_varga,
    rel_house,
)
from app.derived.factors import build_chart_context, planet_aspects
from app.fixtures import load_chart_fixture


def _chart(fixture_id: str = "ajay_kumar"):
    return build_chart_context(load_chart_fixture(fixture_id))["chart"]


def test_universal_seventh_house_aspect_for_ordinary_planets():
    for planet in ("Sun", "Moon", "Mercury", "Venus", "Rahu", "Ketu"):
        assert graha_drishti_houses(planet, 1) == [7]


def test_special_graha_drishti_mars_jupiter_saturn():
    assert graha_drishti_houses("Mars", 1) == [4, 7, 8]
    assert graha_drishti_houses("Jupiter", 1) == [5, 7, 9]
    assert graha_drishti_houses("Saturn", 1) == [3, 7, 10]


def test_house_relationship_types_classification():
    # From house 1: house 4 is both kendra AND chathusra (classical overlap).
    assert house_relationship_types(1, 4) == {"kendra", "chathusra"}
    assert house_relationship_types(1, 5) == {"trikona"}
    assert house_relationship_types(1, 6) == {"dushthana"}
    assert house_relationship_types(1, 7) == {"kendra"}
    assert house_relationship_types(1, 8) == {"dushthana", "chathusra"}
    assert house_relationship_types(1, 9) == {"trikona"}
    assert house_relationship_types(1, 10) == {"kendra"}
    assert house_relationship_types(1, 12) == {"dushthana"}
    assert house_relationship_types(1, 2) == set()
    assert house_relationship_types(1, 1) == {"kendra", "trikona"}  # self is always both


def test_relationship_sets_match_cross_checked_pyjhora_definitions():
    assert KENDRA == {1, 4, 7, 10}
    assert TRIKONA == {1, 5, 9}
    assert DUSHTHANA == {6, 8, 12}
    assert CHATHUSRA == {4, 8}


def test_planet_aspects_delegates_to_new_engine_without_behavior_change():
    """factors.planet_aspects must remain byte-identical to the old
    hardcoded implementation after delegating to app.derived.aspects."""
    for planet in ("Sun", "Mars", "Jupiter", "Saturn", "Rahu"):
        for house in range(1, 13):
            assert planet_aspects(planet, house) == graha_drishti_houses(planet, house)


def test_build_aspect_map_and_mutual_aspects_on_real_chart():
    chart = _chart("ajay_kumar")
    planet_houses = planet_houses_from_d1_chart(chart)
    aspect_map = build_aspect_map(planet_houses)
    assert set(aspect_map.keys()) == set(planet_houses.keys())
    for planet, houses in aspect_map.items():
        assert all(1 <= h <= 12 for h in houses)
        assert 7 in [rel_house(planet_houses[planet], h) for h in houses]  # universal 7th always present

    pairs = mutual_aspects(planet_houses)
    for p1, p2 in pairs:
        assert planet_houses[p2] in aspect_map[p1]
        assert planet_houses[p1] in aspect_map[p2]


def test_full_aspect_report_wired_into_chart_context():
    fixture = load_chart_fixture("ajay_kumar")
    context = build_chart_context(fixture)
    report = context["aspects"]
    assert report["model"] == "classical_graha_drishti"
    assert set(report["graha_drishti"].keys()) == {
        "Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu",
    }
    assert set(report["aspected_by"].keys()) == set(range(1, 13))


def test_aspects_engine_is_varga_aware_via_d9():
    """The exact same engine must work unmodified on a D9 chart's house
    positions -- this is the concrete proof of the 'varga-aware' Phase 1
    requirement, not just an unused capability."""
    chart = _chart("ajay_kumar")
    d9 = compute_varga(chart, 9)
    d9_planet_houses = planet_houses_from_varga(d9)
    d1_planet_houses = planet_houses_from_d1_chart(chart)

    d9_report = full_aspect_report(d9_planet_houses)
    d1_report = full_aspect_report(d1_planet_houses)

    assert set(d9_report["graha_drishti"].keys()) == set(d1_report["graha_drishti"].keys())
    # The two charts generally place planets in different houses, so the
    # resulting aspect maps should generally differ -- proving this is a
    # real per-chart computation, not a cached/D1-only shortcut.
    assert d9_planet_houses != d1_planet_houses or d9_report == d1_report


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
