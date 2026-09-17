"""Validation tests for build_plan.md Phase 4's compiled yoga rule content
(18 rules, app/rules/compiled/yoga_v2.yaml) -- mirrors
tests/unit/test_compiled_rule_packs.py's pattern for the Phase 2 packs.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.derived.factors import build_chart_context
from app.fixtures import list_fixture_ids, load_chart_fixture
from app.rules.generic_evaluator import evaluate_rule_set
from app.rules.loader import load_compiled_rule_packs


def _context(fixture_id: str = "ajay_kumar"):
    return build_chart_context(load_chart_fixture(fixture_id))


def _yoga_rules():
    return [r for r in load_compiled_rule_packs() if r.id.startswith("YOG-")]


def test_yoga_pack_has_18_active_classical_rules():
    rules = _yoga_rules()
    assert len(rules) == 18
    assert all(r.status == "ACTIVE" and r.computation_model == "classical" and r.category == "yoga" for r in rules)


def test_total_compiled_rule_count_includes_yoga_pack():
    """Not the grand total (that's tracked in test_nakshatra_analysis.py's
    test_total_compiled_rule_count_is_420, updated as later packs land) --
    just confirms this pack's own 18 rules are present among whatever the
    current total is."""
    rules = load_compiled_rule_packs()
    yoga_rules = [r for r in rules if r.id.startswith("YOG-")]
    assert len(yoga_rules) == 18


def test_yoga_rules_agree_with_direct_yogas_dict_for_every_fixture():
    rules = _yoga_rules()
    for fixture_id in list_fixture_ids():
        ctx = _context(fixture_id)
        evaluations = {e.rule_id: e for e in evaluate_rule_set(rules, ctx)}
        assert evaluations["YOG-001"].matched == ctx["yogas"]["gajakesari"]["present"]
        assert evaluations["YOG-008"].matched == ctx["yogas"]["pancha_mahapurusha"]["any_present"]
        assert evaluations["YOG-011"].matched == ctx["yogas"]["kendradhipati_dosha"]["present"]
        for evaluation in evaluations.values():
            assert evaluation.quality != "data_gap"


def test_ajay_kumar_ruchaka_yoga_rule_matches_via_compiled_pack():
    """Closes the exact gap docs/phase3-composer-vs-llm-diff.md flagged:
    Ruchaka Mahapurusha Yoga is now renderable through the compiled v2 pack."""
    rules = _yoga_rules()
    ctx = _context("ajay_kumar")
    evaluations = {e.rule_id: e for e in evaluate_rule_set(rules, ctx)}
    assert evaluations["YOG-008"].matched is True


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
