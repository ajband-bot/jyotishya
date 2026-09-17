"""Unit tests for Rule Engine v2 -- the generic, data-driven evaluator.

Validates the fix for the top spec-compliance gap identified in
docs/technical-architecture.md 4.3: rules must be evaluable purely from
data (YAML), with zero per-rule Python branching.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.derived.factors import build_chart_context
from app.fixtures import load_chart_fixture
from app.rules.generic_evaluator import (
    PathNotFound,
    evaluate_rule,
    evaluate_rule_set,
    resolve_path,
)
from app.rules.loader import load_generic_rule_pack
from app.rules.schema import Rule, RuleCondition, RuleOutput

FIXTURE_ID = "ajay_kumar"


def _context():
    fixture = load_chart_fixture(FIXTURE_ID)
    return build_chart_context(fixture)


def test_resolve_path_simple_and_nested():
    ctx = {"chart": {"Mercury": {"house": 2}}, "lagna_sign": 8}
    assert resolve_path(ctx, "lagna_sign") == 8
    assert resolve_path(ctx, "chart.Mercury.house") == 2


def test_resolve_path_int_keyed_dict():
    ctx = {"house_lords": {7: "Saturn", 1: "Mars"}}
    assert resolve_path(ctx, "house_lords.7") == "Saturn"


def test_resolve_path_missing_returns_sentinel():
    ctx = {"chart": {}}
    assert resolve_path(ctx, "chart.Nonexistent.house") is PathNotFound


def test_pilot_pack_loads_and_validates_against_schema():
    rules = load_generic_rule_pack()
    assert len(rules) >= 5
    for rule in rules:
        assert isinstance(rule, Rule)
        assert rule.is_executable()


def test_pilot_001_venus_maraka_matches_for_scorpio_lagna_ajay():
    """Ajay is Scorpio Lagna. H7 (maraka house, Taurus) is Venus-ruled --
    NOT Saturn, contrary to bphs_top20_rule_cards_v1.yaml RC-001's own worked
    example. This test locks in the CORRECTED, computed-verified fact and
    documents the audit finding (see generic_rules_pilot.yaml PILOT-001 notes).
    """
    ctx = _context()
    rules = load_generic_rule_pack()
    pilot_001 = next(r for r in rules if r.id == "PILOT-001")
    result = evaluate_rule(pilot_001, ctx)
    assert result.matched is True, f"evidence={result.chart_evidence}"
    assert result.quality == "computed"
    assert result.outputs[0].payload["planet"] == "Venus"


def test_pilot_003_jupiter_aspect_to_lagna():
    ctx = _context()
    rules = load_generic_rule_pack()
    pilot_003 = next(r for r in rules if r.id == "PILOT-003")
    result = evaluate_rule(pilot_003, ctx)
    # cross-check against the same fact tests/run_suite.py already locks in
    # (ajay:h10-aspect-integrity -> jupiter_to_h1 must be True)
    assert result.matched == (1 in ctx["aspect_map"]["Jupiter"])


def test_pilot_004_upapada_conflict_preserved_not_silently_resolved():
    ctx = _context()
    rules = load_generic_rule_pack()
    pilot_004 = next(r for r in rules if r.id == "PILOT-004")
    result = evaluate_rule(pilot_004, ctx)
    assert result.matched == (ctx["upapada"]["matches"] is False)


def test_non_executable_rule_returns_data_gap():
    """A Rule with zero conditions must never silently 'match' -- it's
    documentation-only until compiled (architecture.md 4.3 `compiled` flag)."""
    bare_rule = Rule(
        id="DRAFT-001", title="Not yet compiled", category="yoga",
        source_tier=4, source_ref="pending", conditions=[], outputs=[],
    )
    result = evaluate_rule(bare_rule, {})
    assert result.matched is False
    assert result.quality == "data_gap"


def test_missing_context_path_fails_closed_as_data_gap():
    rule = Rule(
        id="TEST-MISSING", title="References an uncomputed factor",
        category="varga", source_tier=5, source_ref="test",
        conditions=[RuleCondition(path="does.not.exist", op="eq", value=1)],
        outputs=[RuleOutput(kind="classification", payload={"x": 1})],
    )
    result = evaluate_rule(rule, {"chart": {}})
    assert result.matched is False
    assert result.quality == "data_gap"
    assert result.chart_evidence["does.not.exist"] == "not_available"


def test_evaluate_rule_set_runs_all_pilot_rules_without_error():
    ctx = _context()
    rules = load_generic_rule_pack()
    results = evaluate_rule_set(rules, ctx)
    assert len(results) == len(rules)
    for r in results:
        assert r.quality in {"computed", "computed_simplified", "computed_with_conflict", "data_gap"}


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
