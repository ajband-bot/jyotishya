"""Unit tests for app.derived.compatibility -- the 8-fold Ashtakuta Guna
Milan engine + Mangal Dosha matching (build_plan.md Phase 4a items 1-2).

The primary cross-check target is the existing LLM-authored
Ajay_Sravani_Compatibility.md, whose raw (14/36) and dosha-cancelled
(25/36) Ashtakuta totals this engine reproduces exactly end-to-end, even
though two individual kutas (Yoni, Gana) use richer, independently
cross-checked tables that differ from that document's simplified
per-kuta labels -- see docs/marriage-compatibility-notes.md for the full
discrepancy log.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.derived.compatibility import (
    ashtakuta_report,
    bhakut_kuta,
    gana_kuta,
    graha_maitri_kuta,
    mangal_dosha_match,
    nadi_kuta,
    tara_kuta,
    varna_kuta,
    vasya_kuta,
    yoni_kuta,
)
from app.derived.factors import build_chart_context
from app.fixtures import load_chart_fixture


def _ctx(chart_id: str):
    return build_chart_context(load_chart_fixture(chart_id))


def test_ashtakuta_report_matches_known_worked_example():
    """Cross-check against Ajay_Sravani_Compatibility.md's own worked
    Ashtakuta table: raw total 14/36, dosha-cancelled effective total
    25/36, both partners Manglik (mutually cancelled)."""
    groom, bride = _ctx("ajay_kumar"), _ctx("sravani")
    report = ashtakuta_report(groom, bride)
    assert report["raw_total"] == 14.0
    assert report["effective_total"] == 25.0
    assert report["interpretation"] == "good"
    assert report["mangal_dosha"]["both_manglik"] is True
    assert report["mangal_dosha"]["verdict"] == "mutually_cancelled"


def test_ashtakuta_report_varna_vasya_tara_graha_maitri_exact_match():
    """These 4 kutas have no ambiguity in the source material -- exact
    score match expected (unlike Yoni/Gana, see module docstring)."""
    groom, bride = _ctx("ajay_kumar"), _ctx("sravani")
    kutas = ashtakuta_report(groom, bride)["kutas"]
    assert kutas["varna"]["raw_score"] == 1.0
    assert kutas["vasya"]["raw_score"] == 2.0
    assert kutas["tara"]["raw_score"] == 3.0
    assert kutas["graha_maitri"]["raw_score"] == 5.0
    assert kutas["bhakut"]["raw_score"] == 0.0 and kutas["bhakut"]["effective_score"] == 7.0
    assert kutas["nadi"]["raw_score"] == 0.0 and kutas["nadi"]["effective_score"] == 4.0


def test_varna_kuta_groom_must_be_equal_or_higher():
    # Aries (Kshatriya) groom, Cancer (Brahmin) bride -> groom is "lower" -> 0
    assert varna_kuta(1, 4)["raw_score"] == 0.0
    # Cancer (Brahmin) groom, Aries (Kshatriya) bride -> groom is "higher" -> 1
    assert varna_kuta(4, 1)["raw_score"] == 1.0
    # Equal varna (both Aries/fire=Kshatriya) -> 1
    assert varna_kuta(1, 5)["raw_score"] == 1.0


def test_vasya_kuta_sagittarius_capricorn_degree_split():
    # Sagittarius 1st half (Manava) vs Sagittarius 2nd half (Chatushpada)
    manava = vasya_kuta(9, 5.0, 9, 5.0)
    assert manava["groom_group"] == manava["bride_group"] == "Manava"
    chatushpada = vasya_kuta(9, 25.0, 9, 25.0)
    assert chatushpada["groom_group"] == chatushpada["bride_group"] == "Chatushpada"


def test_tara_kuta_both_janma_is_perfect_score():
    # Krittika(3) <-> Uttara Ashadha(21), the guide's own worked example
    result = tara_kuta(3, 21)
    assert result["groom_to_bride_remainder"] == 1
    assert result["bride_to_groom_remainder"] == 1
    assert result["raw_score"] == 3.0


def test_yoni_kuta_same_animal_is_perfect():
    # Ashwini(1) and Ashwini(1) both "Horse"
    assert yoni_kuta(1, 1)["raw_score"] == 4.0


def test_graha_maitri_kuta_same_lord_is_perfect():
    # Aries(1) and Leo(5) both Sun/Mars-ruled trine signs with same lord
    # case: Cancer(4, Moon-ruled) paired with itself
    result = graha_maitri_kuta(4, 4)
    assert result["raw_score"] == 5.0
    assert result["groom_to_bride_relationship"] == "same_planet"


def test_gana_kuta_matches_asymmetric_saravali_table():
    # Deva(Ashwini=1) groom + Rakshasa(Krittika=3) bride: PyJHora gana_array[bride=Rakshasa][groom=Deva] = row2 col0 = 1
    assert gana_kuta(1, 3)["raw_score"] == 1.0
    # Rakshasa(Krittika=3) groom + Deva(Ashwini=1) bride: row0(Deva) col2(Rakshasa) = 0
    assert gana_kuta(3, 1)["raw_score"] == 0.0


def test_bhakut_kuta_59_axis_cancelled_when_lords_are_friends():
    groom, bride = _ctx("ajay_kumar"), _ctx("sravani")
    result = bhakut_kuta(groom["chart"]["Moon"]["sign"], bride["chart"]["Moon"]["sign"], groom["chart"], bride["chart"])
    assert result["axis"] == "5/9"
    assert result["dosha_present_raw"] is True
    assert result["cancelled"] is True
    assert result["effective_score"] == 7.0


def test_nadi_kuta_different_nadi_is_full_score_no_dosha():
    # Ashwini(Adi) vs Bharani(Madhya) -- different nadi groups
    result = nadi_kuta(1, 1, 2, 1, 1, 1, {"Jupiter": {"sign": 4}}, {"Jupiter": {"sign": 4}})
    assert result["dosha_present_raw"] is False
    assert result["effective_score"] == 8.0


def test_nadi_kuta_same_nadi_applies_mitigation_heuristic():
    groom, bride = _ctx("ajay_kumar"), _ctx("sravani")
    g_nak = groom["nakshatra_analysis"]["Moon"]
    b_nak = bride["nakshatra_analysis"]["Moon"]
    result = nadi_kuta(
        g_nak["nakshatra_id"], g_nak["pada"], b_nak["nakshatra_id"], b_nak["pada"],
        groom["chart"]["Moon"]["sign"], bride["chart"]["Moon"]["sign"], groom["chart"], bride["chart"],
    )
    assert result["dosha_present_raw"] is True
    assert result["conditions_met"] == 4
    assert result["effective_score"] == 4.0


def test_mangal_dosha_match_one_sided_is_a_concern():
    """Synthetic doshas dicts (not fixture-derived) to exercise the
    one-sided branch, which the real fixture pair doesn't hit."""
    groom_ctx = {"doshas": {"mangal_dosha": {"present": True}}}
    bride_ctx = {"doshas": {"mangal_dosha": {"present": False}}}
    result = mangal_dosha_match(groom_ctx, bride_ctx)
    assert result["both_manglik"] is False
    assert result["verdict"] == "one_sided_concern"


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
