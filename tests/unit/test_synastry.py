"""Unit tests for app.derived.synastry -- 7 cross-chart synastry
indicators + 5 D9 cross-compatibility rules (build_plan.md Phase 4a
item 4).
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.derived.factors import build_chart_context
from app.derived.synastry import (
    d9_cross_compatibility,
    h7_lord_cross,
    lagna_lagna_synastry,
    lagna_lord_cross,
    moon_moon_synastry,
    sign_axis,
    sun_moon_synastry,
    synastry_report,
)
from app.fixtures import load_chart_fixture


def _ctx(chart_id: str):
    return build_chart_context(load_chart_fixture(chart_id))


def test_sign_axis_classifies_all_named_axes():
    assert sign_axis(1, 1)["axis"] == "1/1"
    assert sign_axis(1, 7)["axis"] == "1/7"
    assert sign_axis(1, 5)["axis"] == "5/9"
    assert sign_axis(1, 4)["axis"] == "4/10"
    assert sign_axis(1, 6)["axis"] == "6/8"


def test_sun_moon_synastry_ajay_sravani_is_same_sign_conjunction():
    """Cross-check: Ajay_Sravani_Compatibility.md's own headline synastry
    finding -- Ajay's Sun and Sravani's Moon are both in Sagittarius."""
    groom, bride = _ctx("ajay_kumar"), _ctx("sravani")
    result = sun_moon_synastry(groom["chart"], bride["chart"])
    assert result["groom_sun_to_bride_moon"]["axis"] == "1/1"


def test_moon_moon_and_lagna_lagna_are_trikona_for_ajay_sravani():
    """Cross-check: guide's own finding -- Aries/Sagittarius Moons and
    Scorpio/Pisces Lagnas are both 5/9 trikona."""
    groom, bride = _ctx("ajay_kumar"), _ctx("sravani")
    assert moon_moon_synastry(groom["chart"], bride["chart"])["axis"]["axis"] == "5/9"
    assert lagna_lagna_synastry(groom["chart"], bride["chart"])["axis"]["axis"] == "5/9"


def test_lagna_lord_cross_ajay_sravani_are_mutual_friends():
    groom, bride = _ctx("ajay_kumar"), _ctx("sravani")
    result = lagna_lord_cross(groom["chart"], bride["chart"])
    assert result["groom_lagna_lord"] == "Mars"
    assert result["bride_lagna_lord"] == "Jupiter"
    assert result["mutual_friends"] is True


def test_h7_lord_cross_ajay_sravani_are_mutual_friends():
    groom, bride = _ctx("ajay_kumar"), _ctx("sravani")
    result = h7_lord_cross(groom, bride)
    assert result["groom_h7_lord"] == "Venus"
    assert result["bride_h7_lord"] == "Mercury"
    assert result["mutual_friends"] is True


def test_synastry_report_has_all_7_indicators():
    groom, bride = _ctx("ajay_kumar"), _ctx("sravani")
    report = synastry_report(groom, bride)
    assert set(report.keys()) == {
        "sun_moon", "moon_moon", "lagna_lagna", "venus_moon", "jupiter_moon",
        "lagna_lord", "h7_lord", "citation",
    }


def test_d9_cross_compatibility_has_all_5_rules_with_evidence():
    groom, bride = _ctx("ajay_kumar"), _ctx("sravani")
    result = d9_cross_compatibility(groom, bride)
    for rule_key in [
        "rule1_moon_mirror", "rule2_jupiter_mirror", "rule3_shared_exalted_planets",
        "rule4_venus_lagna_match", "rule5_d9_seventh_houses_mutual_aspect",
    ]:
        assert "met" in result[rule_key]


def test_d9_rule3_requires_exalted_not_merely_own_sign():
    """Regression guard for a strictness decision: Marriage_Guide_Part4.md's
    own worked example narratively rounds Sravani's D9 Mars (own sign,
    Aries) up to "both extremely strong" alongside Ajay's D9 Mars
    (exalted, Capricorn) -- but Rule 3's own text requires exalted in BOTH
    charts, not merely strong. Since Sravani's is own-sign (not exalted),
    Rule 3 must NOT be satisfied here even though the guide's prose implies
    otherwise -- verifies this engine follows the rule's literal text, not
    the source document's looser narrative rounding (Cardinal Rule 9:
    never sugarcoat, don't inherit someone else's approximation either)."""
    groom, bride = _ctx("ajay_kumar"), _ctx("sravani")
    result = d9_cross_compatibility(groom, bride)
    assert "Mars" not in result["rule3_shared_exalted_planets"]["planets"]


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
