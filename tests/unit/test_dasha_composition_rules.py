"""Unit tests for the compiled DASHA-* rule pack (build_plan.md Phase 5,
app/rules/generators/generate_dasha_rules.py).
"""
from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.derived.factors import build_chart_context
from app.fixtures import load_chart_fixture
from app.rules.generic_evaluator import evaluate_rule_set
from app.rules.loader import load_compiled_rule_packs


def _context(chart_id: str, today: date):
    return build_chart_context(load_chart_fixture(chart_id), today=today)


def _dasha_rules():
    return [r for r in load_compiled_rule_packs() if r.id.startswith("DASHA-")]


def test_exactly_81_dasha_rules_covering_all_9x9_pairs():
    rules = _dasha_rules()
    assert len(rules) == 81
    pairs = set()
    for rule in rules:
        md = next(c.value for c in rule.conditions if c.path == "current_dasha.mahadasha.planet")
        ad = next(c.value for c in rule.conditions if c.path == "current_dasha.antardasha.planet")
        pairs.add((md, ad))
    assert len(pairs) == 81


def test_exactly_one_dasha_rule_matches_a_given_chart_and_date():
    """At any date, exactly one of the 81 MD/AD pairs can be true."""
    ctx = _context("ajay_kumar", date(2026, 9, 16))
    evaluations = evaluate_rule_set(_dasha_rules(), ctx)
    matched = [e for e in evaluations if e.matched]
    assert len(matched) == 1
    assert matched[0].rule_id == "DASHA-RAHU-MOON"


def test_matched_rule_quality_is_computed_simplified_practical_proxy():
    """These rules are honestly labeled practical_proxy (general MD/AD
    combination principle, not a verse-cited prediction for this specific
    pairing) -- quality must downgrade accordingly, never claim full
    'computed' fidelity."""
    ctx = _context("ajay_kumar", date(2026, 9, 16))
    evaluations = evaluate_rule_set(_dasha_rules(), ctx)
    matched = next(e for e in evaluations if e.matched)
    assert matched.quality == "computed_simplified"


def test_same_planet_md_ad_uses_intensification_phrase():
    rules = _dasha_rules()
    rule = next(r for r in rules if r.id == "DASHA-JUPITER-JUPITER")
    effect = rule.outputs[0].payload["effect"]
    assert "intensify" in effect


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
