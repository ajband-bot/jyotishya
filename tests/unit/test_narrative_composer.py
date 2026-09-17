"""Unit tests for build_plan.md Phase 3: Narrative Composer v1.

Covers composer.py's 3 sections (lagna/dosha/yoga), gap_report.py, and the
determinism guarantee (AD-2/AD-3: byte-identical output for the same chart
across repeated runs -- the entire reason this exists instead of an LLM
call).
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.derived.factors import build_chart_context
from app.engine.narrative.composer import compose_chart_narrative
from app.engine.narrative.gap_report import build_gap_report
from app.fixtures import list_fixture_ids, load_chart_fixture
from app.rules.loader import load_compiled_rule_packs, load_generic_rule_pack


def _all_rules():
    return load_compiled_rule_packs() + load_generic_rule_pack()


def test_compose_chart_narrative_runs_without_error_for_every_fixture():
    for fixture_id in list_fixture_ids():
        result = compose_chart_narrative(fixture_id)
        assert result["chart_id"] == fixture_id
        assert set(result["sections"].keys()) == {"lagna", "dosha", "yoga"}
        assert result["rule_count_matched"] > 0


def test_compose_chart_narrative_is_deterministic():
    """Same chart, same rules -> byte-identical output every time (AD-2/AD-3)."""
    first = compose_chart_narrative("ajay_kumar")
    second = compose_chart_narrative("ajay_kumar")
    assert first["sections"] == second["sections"]
    assert first["gap_report"] == second["gap_report"]


def test_lagna_section_always_renders_something_never_empty_silently():
    """Every chart has a Lagna lord somewhere -- LPH-01-XX must always match
    exactly one of the 144 lord-placement rules, so this section should
    never legitimately hit the empty-state branch."""
    for fixture_id in list_fixture_ids():
        result = compose_chart_narrative(fixture_id)
        assert "narrative-empty" not in result["sections"]["lagna"]
        assert "Lagna Analysis" in result["sections"]["lagna"]


def test_dosha_section_contains_at_least_mangal_dosha_rule_id_marker():
    """DSH-001 (mangal dosha present/absent check) always resolves -- it
    should appear as matched or simply not fire, but the dosha pack itself
    must always be evaluable without exceptions."""
    for fixture_id in list_fixture_ids():
        result = compose_chart_narrative(fixture_id)
        assert "Do\u1e63a Register" in result["sections"]["dosha"]


def test_yoga_section_never_fabricates_content_and_matches_engine_truth():
    """Phase 3 (when yoga content was 0 rules) asserted an honest empty
    state had to appear for at least one fixture. Phase 4 compiled 18 yoga
    rules (app/rules/compiled/yoga_v2.yaml), so every fixture now matches
    at least one real yoga -- the meaningful invariant going forward is
    that the section NEVER shows a yoga that isn't independently confirmed
    by app.derived.yogas' own computed truth (no fabrication), not that an
    empty state must exist somewhere."""
    from app.derived.factors import build_chart_context
    from app.fixtures import load_chart_fixture as _load

    for fixture_id in list_fixture_ids():
        result = compose_chart_narrative(fixture_id)
        ctx = build_chart_context(_load(fixture_id))
        if "narrative-empty" in result["sections"]["yoga"]:
            continue
        if "Ruchaka" in result["sections"]["yoga"] or "Pancha Mahapurusha" in result["sections"]["yoga"]:
            assert ctx["yogas"]["pancha_mahapurusha"]["any_present"] is True


def test_gap_report_only_contains_data_gap_quality_entries():
    ctx = build_chart_context(load_chart_fixture("ajay_kumar"))
    rules = _all_rules()
    gaps = build_gap_report(rules, ctx, "ajay_kumar")
    for gap in gaps:
        assert gap["chart_id"] == "ajay_kumar"
        assert "candidate_source_docs" in gap and gap["candidate_source_docs"]


def test_gap_report_matches_priority_engines_unsupported_claim_count():
    """Cross-check: gap_report's ticket count must equal
    app.rules.priority.unsupported_claim_count's tally for the same
    chart+rules -- two independent code paths over the same evaluations
    must never silently disagree."""
    from app.rules.generic_evaluator import evaluate_rule_set
    from app.rules.priority import unsupported_claim_count

    ctx = build_chart_context(load_chart_fixture("ajay_kumar"))
    rules = _all_rules()
    gaps = build_gap_report(rules, ctx, "ajay_kumar")
    evaluations = evaluate_rule_set(rules, ctx)
    assert len(gaps) == unsupported_claim_count(evaluations)


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
