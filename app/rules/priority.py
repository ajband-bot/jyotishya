"""Interpretation Priority + contradiction/confidence engine
(build_plan.md Phase 2 item 9).

Given a rule pack evaluated against a chart context, this module:
  1. Ranks matched evaluations by authority (source_tier, most authoritative
     first) then confidence -- so a caller assembling a narrative section
     knows which evidence to lead with when multiple rules speak to the
     same topic.
  2. Surfaces contradictions using the ALREADY-ESTABLISHED signal in this
     codebase (`quality == "computed_with_conflict"`, driven by a rule's own
     `contradictions` field, e.g. PILOT-004's Upapada formula conflict) --
     deliberately not a new heuristic guessing at semantic conflicts between
     unrelated rules, which would risk false positives (Cardinal Rule 3).
  3. Computes the 4 metrics build_plan.md names explicitly: Rule Coverage %,
     Evidence Traceability %, Cross-fixture Consistency %, and Unsupported
     Claim Count. Where the plan's wording is ambiguous (no further spec
     exists for these terms anywhere in the corpus), each metric's docstring
     states the concrete interpretation chosen, rather than silently picking
     one without disclosure (Cardinal Rule 4).
"""
from __future__ import annotations

from typing import Any

from app.rules.generic_evaluator import evaluate_rule_set
from app.rules.schema import Rule, RuleCategory, RuleEvaluation

_CONFIDENCE_RANK = {"high": 0, "medium": 1, "low": 2}
ALL_RULE_CATEGORIES: tuple[str, ...] = RuleCategory.__args__  # type: ignore[attr-defined]


def evaluate_and_prioritize(rules: list[Rule], context: dict[str, Any]) -> list[dict[str, Any]]:
    """Evaluate every rule, then sort matched results by (source_tier asc,
    confidence rank asc) -- i.e. most authoritative, highest-confidence
    evidence first. Unmatched evaluations are appended after, unsorted
    among themselves (they carry no interpretive weight to rank)."""
    rule_by_id = {rule.id: rule for rule in rules}
    evaluations = evaluate_rule_set(rules, context)
    records = [{"rule": rule_by_id[e.rule_id], "evaluation": e} for e in evaluations]
    matched = [r for r in records if r["evaluation"].matched]
    unmatched = [r for r in records if not r["evaluation"].matched]
    matched.sort(key=lambda r: (r["evaluation"].source_tier, _CONFIDENCE_RANK.get(r["evaluation"].confidence, 1)))
    return matched + unmatched


def detect_contradictions(evaluations: list[RuleEvaluation]) -> list[RuleEvaluation]:
    """Matched evaluations whose own rule declared a contradiction --
    reuses the existing `computed_with_conflict` quality signal rather than
    inferring new conflicts (see module docstring, point 2)."""
    return [e for e in evaluations if e.matched and e.quality == "computed_with_conflict"]


def rule_coverage_pct(rules: list[Rule], evaluations: list[RuleEvaluation]) -> float:
    """% of RuleCategory values represented in `rules` that have at least
    one matched, ACTIVE-status evaluation. Interpretation chosen: coverage
    means "this category can currently produce a real, active verdict for
    this chart" -- not merely "a rule in this category exists on disk"."""
    categories_present = {rule.category for rule in rules}
    if not categories_present:
        return 0.0
    matched_ids = {e.rule_id for e in evaluations if e.matched and e.status == "ACTIVE"}
    rule_by_id = {rule.id: rule for rule in rules}
    covered = {rule_by_id[rid].category for rid in matched_ids if rid in rule_by_id}
    return round(len(covered) / len(categories_present) * 100, 2)


def evidence_traceability_pct(evaluations: list[RuleEvaluation]) -> float:
    """% of ALL evaluations (matched or not) whose quality is not
    `data_gap` -- i.e. the evidence trail actually resolved, regardless of
    whether the rule ultimately matched."""
    if not evaluations:
        return 0.0
    traceable = sum(1 for e in evaluations if e.quality != "data_gap")
    return round(traceable / len(evaluations) * 100, 2)


def unsupported_claim_count(evaluations: list[RuleEvaluation]) -> int:
    """Count of evaluations where an ACTIVE rule's condition could not be
    fully resolved against the chart (quality == data_gap) -- i.e. a claim
    this rule pack is nominally prepared to make, but cannot currently
    support with available data for this chart."""
    return sum(1 for e in evaluations if e.status == "ACTIVE" and e.quality == "data_gap")


def cross_fixture_consistency_pct(
    rules: list[Rule],
    fixture_ids: list[str],
    context_builder,
) -> float:
    """% of rules whose DATA AVAILABILITY (quality != data_gap) is the same
    across every fixture -- i.e. a rule's ability to resolve does not
    mysteriously depend on which native's chart it's run against. This is
    a stability/consistency check on the rule pack itself, NOT a check that
    every native gets the same verdict (verdicts SHOULD differ by chart --
    only the evidence-resolution behavior should be stable)."""
    if not rules or not fixture_ids:
        return 0.0
    per_fixture_quality: dict[str, list[bool]] = {rule.id: [] for rule in rules}
    for fixture_id in fixture_ids:
        context = context_builder(fixture_id)
        evaluations = evaluate_rule_set(rules, context)
        for evaluation in evaluations:
            per_fixture_quality[evaluation.rule_id].append(evaluation.quality != "data_gap")
    consistent = sum(1 for flags in per_fixture_quality.values() if len(set(flags)) <= 1)
    return round(consistent / len(rules) * 100, 2)


def coverage_report(rules: list[Rule], context: dict[str, Any]) -> dict[str, Any]:
    """One-shot convenience: evaluate once, return all metrics build_plan.md
    names (except cross-fixture consistency, which needs multiple fixtures
    and is therefore a separate call -- see cross_fixture_consistency_pct)."""
    evaluations = evaluate_rule_set(rules, context)
    return {
        "rule_coverage_pct": rule_coverage_pct(rules, evaluations),
        "evidence_traceability_pct": evidence_traceability_pct(evaluations),
        "unsupported_claim_count": unsupported_claim_count(evaluations),
        "contradictions": [e.rule_id for e in detect_contradictions(evaluations)],
        "total_rules_evaluated": len(evaluations),
        "total_matched": sum(1 for e in evaluations if e.matched),
    }
