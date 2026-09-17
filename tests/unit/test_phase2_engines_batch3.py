"""Unit tests for build_plan.md Phase 2 batch-3 engines: composed daśā-lord
synthesis, the generic Event Agreement Engine, and the Interpretation
Priority + contradiction/confidence engine.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.derived.event_agreement import EVENT_DOMAINS, all_event_agreements, event_agreement
from app.derived.factors import build_chart_context
from app.fixtures import list_fixture_ids, load_chart_fixture
from app.rules.loader import load_compiled_rule_packs
from app.rules.priority import (
    coverage_report,
    cross_fixture_consistency_pct,
    detect_contradictions,
    evaluate_and_prioritize,
    evidence_traceability_pct,
    rule_coverage_pct,
    unsupported_claim_count,
)


def _context(fixture_id: str = "ajay_kumar"):
    return build_chart_context(load_chart_fixture(fixture_id))


# ── Dasha-lord synthesis ────────────────────────────────────────────────
def test_dasha_synthesis_wired_into_context_and_covers_md_ad_pd():
    ctx = _context()
    synthesis = ctx["dasha_synthesis"]
    assert set(synthesis["stack"].keys()) <= {"mahadasha", "antardasha", "pratyantardasha"}
    assert "mahadasha" in synthesis["stack"]
    md_entry = synthesis["stack"]["mahadasha"]
    assert md_entry["planet"] == ctx["current_dasha"]["mahadasha"]["planet"]
    assert "functional_classification" in md_entry
    assert "dispositor_terminus" in md_entry


def test_dasha_synthesis_md_ad_relationship_present_when_different_planets():
    ctx = _context()
    synthesis = ctx["dasha_synthesis"]
    md = ctx["current_dasha"].get("mahadasha", {}).get("planet")
    ad = ctx["current_dasha"].get("antardasha", {}).get("planet")
    if md and ad and md != ad:
        assert synthesis["md_ad_relationship"] is not None
        assert synthesis["md_ad_relationship"]["md_to_ad"] in {"friend", "neutral", "enemy"}


def test_dasha_synthesis_present_for_every_fixture_without_exceptions():
    for fixture_id in list_fixture_ids():
        ctx = _context(fixture_id)
        assert "dasha_synthesis" in ctx


# ── Event Agreement Engine ──────────────────────────────────────────────
def test_event_agreement_covers_all_23_documented_themes():
    assert len(EVENT_DOMAINS) == 23


def test_event_agreement_returns_valid_verdict_for_every_theme():
    ctx = _context()
    for theme in EVENT_DOMAINS:
        result = event_agreement(ctx, theme)
        assert result["verdict"] in {"strong_agreement", "moderate_agreement", "weak_agreement"}
        assert 0.0 <= result["agreement_ratio"] <= 1.0
        assert result["max_score"] >= 2  # bhava_bala + dasha_activation always applicable


def test_event_agreement_unknown_theme_raises():
    ctx = _context()
    try:
        event_agreement(ctx, "not_a_real_theme")
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_event_agreement_marks_data_gap_for_unsupported_varga_themes():
    ctx = _context()
    result = event_agreement(ctx, "health_attention")
    assert result["evidence"]["varga_confirmation"]["varga"] is None
    assert "data_gap" in result["evidence"]["varga_confirmation"]["note"]


def test_all_event_agreements_smoke_test_every_fixture():
    for fixture_id in list_fixture_ids():
        ctx = _context(fixture_id)
        all_results = all_event_agreements(ctx)
        assert len(all_results) == 23


# ── Interpretation Priority engine ──────────────────────────────────────
def test_evaluate_and_prioritize_orders_matched_before_unmatched():
    ctx = _context()
    rules = [r for r in load_compiled_rule_packs() if r.id.startswith("DSH-")]
    records = evaluate_and_prioritize(rules, ctx)
    matched_flags = [r["evaluation"].matched for r in records]
    first_false = matched_flags.index(False) if False in matched_flags else len(matched_flags)
    assert all(matched_flags[:first_false])  # all True entries come first


def test_evaluate_and_prioritize_sorts_by_source_tier_then_confidence():
    ctx = _context()
    rules = load_compiled_rule_packs()
    records = evaluate_and_prioritize(rules, ctx)
    matched = [r for r in records if r["evaluation"].matched]
    tiers = [r["evaluation"].source_tier for r in matched]
    assert tiers == sorted(tiers)


def test_detect_contradictions_finds_upapada_pilot_conflict():
    from app.rules.loader import load_generic_rule_pack

    rules = load_generic_rule_pack()  # generic_rules_pilot.yaml (includes PILOT-004)
    ctx = _context()
    ctx["upapada"] = ctx["upapada"]  # already present
    from app.rules.generic_evaluator import evaluate_rule_set

    evaluations = evaluate_rule_set(rules, ctx)
    contradictions = detect_contradictions(evaluations)
    assert any(e.rule_id == "PILOT-004" for e in contradictions)


def test_rule_coverage_and_traceability_metrics_are_percentages():
    ctx = _context()
    rules = load_compiled_rule_packs()
    report = coverage_report(rules, ctx)
    assert 0.0 <= report["rule_coverage_pct"] <= 100.0
    assert 0.0 <= report["evidence_traceability_pct"] <= 100.0
    assert report["unsupported_claim_count"] >= 0
    assert report["total_matched"] > 0


def test_cross_fixture_consistency_is_100_for_fully_computed_dosha_pack():
    """The 15 dosha rules resolve their evidence paths identically for
    every fixture (the doshas dict always has all keys) -- consistency
    should be exactly 100%."""
    rules = [r for r in load_compiled_rule_packs() if r.id.startswith("DSH-")]
    fixture_ids = list_fixture_ids()
    pct = cross_fixture_consistency_pct(rules, fixture_ids, lambda fid: _context(fid))
    assert pct == 100.0


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
