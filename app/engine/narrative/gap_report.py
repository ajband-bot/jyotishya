"""Gap-report generation (build_plan.md §4 / Phase 3).

Collects every RuleEvaluation with quality == "data_gap" into a structured
ticket the AGENT SESSION (not the API, not silently the LLM) can act on:
either (a) write the missing rule per build_plan.md §3.2, or (b) as an
explicit, visually-labeled last resort, ask an LLM to draft prose for that
gap only, tagged `llm_fallback` -- never silently blended with computed
sections (see composer.py's own docstring for the render-side half of that
contract).
"""
from __future__ import annotations

from typing import Any

from app.rules.priority import evaluate_and_prioritize
from app.rules.schema import Rule

# Where a human should look first to close a gap in this category -- best
# available guess per category, not exhaustive; a gap in a category not
# listed here still gets reported, just with the generic fallback doc.
CATEGORY_DOC_HINTS: dict[str, str] = {
    "yoga": "docs/interpretive-frameworks.md (8-Step Yoga Verification)",
    "dosha": "docs/dosha-registry.md",
    "dasha": "docs/interpretive-frameworks.md (5-Layer Da\u015b\u0101 Reading)",
    "transit": "docs/interpretive-frameworks.md (5-Layer Transit Timing)",
    "nakshatra": "docs/nakshatra-framework.md",
    "arudha": "docs/interpretive-frameworks.md",
    "argala": "docs/interpretive-frameworks.md",
    "karaka": "docs/interpretive-frameworks.md (Six Questions per Planet)",
    "lord_placement": "docs/interpretive-frameworks.md (Kend\u0101dhipati, dispositor chains)",
    "functional_nature": "AGENTS.md Cardinal Rule 7 / BPHS Ch.34",
    "bhava_signification": "docs/interpretive-frameworks.md",
    "strength": "build_plan.md \u00a75 item 10 (Shadbala audit)",
    "varga": "app/astro/vargas.py docstring (BPHS-16 varga scope)",
    "aspect": "docs/interpretive-frameworks.md",
    "dignity": "docs/interpretive-frameworks.md",
    "event": "docs/domain-playbooks.md",
}
_DEFAULT_DOC_HINT = "docs/interpretive-frameworks.md"


def build_gap_report(rules: list[Rule], context: dict[str, Any], chart_id: str) -> list[dict[str, Any]]:
    """One ticket per ACTIVE rule that hit `quality == data_gap` for this
    chart -- i.e. a rule that COULD fire but couldn't resolve its evidence.
    Rules that simply didn't match (condition resolved but was false) are
    NOT gaps -- that is a normal, honest non-match, not missing data."""
    records = evaluate_and_prioritize(rules, context)
    gaps: list[dict[str, Any]] = []
    for record in records:
        rule = record["rule"]
        evaluation = record["evaluation"]
        if evaluation.quality != "data_gap":
            continue
        missing_paths = [path for path, value in evaluation.chart_evidence.items() if value == "not_available"]
        gaps.append({
            "chart_id": chart_id,
            "rule_id": evaluation.rule_id,
            "title": evaluation.title,
            "category": rule.category,
            "missing_paths": missing_paths,
            "candidate_source_docs": [CATEGORY_DOC_HINTS.get(rule.category, _DEFAULT_DOC_HINT)],
        })
    return gaps
