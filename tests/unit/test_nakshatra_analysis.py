"""Unit tests for build_plan.md Phase 4: nakshatra analysis engine
(app.derived.nakshatra_analysis) and its compiled v2 rule pack (27 rules,
NAK-01..NAK-27, keyed on Moon's Janma Nakshatra).
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.derived.factors import build_chart_context
from app.derived.nakshatra_analysis import check_gandanta, nakshatra_profile
from app.fixtures import list_fixture_ids, load_chart_fixture
from app.rules.generic_evaluator import evaluate_rule_set
from app.rules.loader import load_compiled_rule_packs


def _ctx(fixture_id: str):
    return build_chart_context(load_chart_fixture(fixture_id))


# ── Gandanta ──────────────────────────────────────────────────────────
def test_gandanta_exact_junction_is_flagged():
    result = check_gandanta(120.0)  # exact Cancer/Leo boundary
    assert result["in_gandanta"] is True
    assert result["junction"] == "cancer_leo"
    assert result["orb_deg"] == 0.0


def test_gandanta_far_from_junction_not_flagged():
    result = check_gandanta(60.0)  # mid-Taurus, nowhere near a junction
    assert result["in_gandanta"] is False


def test_gandanta_wraps_correctly_at_zero_360_boundary():
    result_low = check_gandanta(1.0)
    result_high = check_gandanta(359.0)
    assert result_low["in_gandanta"] is True and result_low["junction"] == "pisces_aries"
    assert result_high["in_gandanta"] is True and result_high["junction"] == "pisces_aries"


def test_abhukta_mula_only_flagged_within_tight_orb_of_scorpio_sagittarius():
    tight = check_gandanta(240.0 + 0.5)  # 30 arcmin from the Jyeshtha-Mula boundary
    wide = check_gandanta(240.0 + 2.0)   # within the general 3d20' orb but outside Abhukta Mula
    assert tight["abhukta_mula"] is True
    assert wide["in_gandanta"] is True and wide["abhukta_mula"] is False


# ── Nakshatra profile ────────────────────────────────────────────────────
def test_nakshatra_profile_has_all_expected_fields():
    profile = nakshatra_profile(10.0)  # early Ashwini
    for field in ("nakshatra_id", "nakshatra_en", "lord", "deity", "pada", "gana", "gana_temperament", "tattva", "yoni", "motivation", "gandanta", "citation"):
        assert field in profile
    assert profile["nakshatra_en"] == "Ashwini"
    assert profile["gana"] == "Deva"


def test_nakshatra_analysis_wired_into_context_for_all_9_planets():
    ctx = _ctx("ajay_kumar")
    assert set(ctx["nakshatra_analysis"].keys()) == {
        "Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu",
    }


def test_nakshatra_ids_are_valid_range_for_every_fixture():
    for fixture_id in list_fixture_ids():
        ctx = _ctx(fixture_id)
        for profile in ctx["nakshatra_analysis"].values():
            assert 1 <= profile["nakshatra_id"] <= 27
            assert 1 <= profile["pada"] <= 4


# ── Compiled v2 pack ──────────────────────────────────────────────────────
def _nak_rules():
    return [r for r in load_compiled_rule_packs() if r.id.startswith("NAK-")]


def test_nakshatra_pack_has_27_active_classical_rules():
    rules = _nak_rules()
    assert len(rules) == 27
    assert all(r.status == "ACTIVE" and r.computation_model == "classical" and r.category == "nakshatra" for r in rules)


def test_exactly_1_nakshatra_rule_matches_per_fixture():
    rules = _nak_rules()
    for fixture_id in list_fixture_ids():
        ctx = _ctx(fixture_id)
        evaluations = evaluate_rule_set(rules, ctx)
        matched = [e for e in evaluations if e.matched]
        assert len(matched) == 1
        assert matched[0].quality == "computed"
        expected_id = ctx["nakshatra_analysis"]["Moon"]["nakshatra_id"]
        assert matched[0].outputs[0].payload["nakshatra_id"] == expected_id


def test_total_compiled_rule_count_is_591():
    """108+144+108+15+18+27+81+40+30+20 (Phase 6 added MAR-/CAR-/REM- packs)."""
    rules = load_compiled_rule_packs()
    assert len(rules) == 108 + 144 + 108 + 15 + 18 + 27 + 81 + 40 + 30 + 20


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
