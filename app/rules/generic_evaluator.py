"""Rule Engine v2 — generic condition evaluator.

Replaces per-rule `if rule_id == "RC-00N"` branching with a single,
data-driven interpreter: resolve each RuleCondition's dotted `path` against
the chart-context dict, apply its `op`, AND all conditions together, and
emit a structured RuleEvaluation with a full evidence trace.

No astrology-specific branching lives in this file -- it is pure condition
evaluation. All Jyotisha knowledge lives in the Rule data (YAML/JSON), never
in Python here. This is what makes new rules addable without touching code.
"""
from __future__ import annotations

from typing import Any

from app.rules.schema import Rule, RuleCondition, RuleEvaluation

_OPERATORS = {
    "eq": lambda actual, expected: actual == expected,
    "neq": lambda actual, expected: actual != expected,
    "in": lambda actual, expected: actual in expected,
    "not_in": lambda actual, expected: actual not in expected,
    "gt": lambda actual, expected: actual is not None and actual > expected,
    "lt": lambda actual, expected: actual is not None and actual < expected,
    "gte": lambda actual, expected: actual is not None and actual >= expected,
    "lte": lambda actual, expected: actual is not None and actual <= expected,
    "house_in": lambda actual, expected: actual in expected,
    "contains": lambda actual, expected: expected in actual if actual is not None else False,
}


class PathNotFound:
    """Sentinel distinguishing 'value is None' from 'path does not resolve'."""


def resolve_path(context: dict[str, Any], path: str) -> Any:
    """Resolve a dotted path like 'chart.Mercury.house' against a nested dict.

    Returns PathNotFound (not None) when any segment is missing, so a rule
    referencing a not-yet-computed factor fails closed rather than silently
    matching on `None == None`.
    """
    node: Any = context
    for segment in path.split("."):
        if not isinstance(node, dict):
            return PathNotFound
        if segment in node:
            node = node[segment]
        elif segment.isdigit() and int(segment) in node:
            node = node[int(segment)]
        else:
            return PathNotFound
    return node


def evaluate_condition(context: dict[str, Any], condition: RuleCondition) -> tuple[bool, Any]:
    actual = resolve_path(context, condition.path)
    if actual is PathNotFound:
        return False, PathNotFound
    op_fn = _OPERATORS.get(condition.op)
    if op_fn is None:
        raise ValueError(f"Unsupported operator: {condition.op}")
    try:
        return bool(op_fn(actual, condition.value)), actual
    except TypeError:
        return False, actual


def evaluate_rule(rule: Rule, context: dict[str, Any]) -> RuleEvaluation:
    if not rule.is_executable():
        return RuleEvaluation(
            rule_id=rule.id,
            title=rule.title,
            matched=False,
            chart_evidence={"reason": "rule has no compiled conditions yet -- documentation-only"},
            outputs=[],
            confidence=rule.confidence,
            source_tier=rule.source_tier,
            status=rule.status,
            quality="data_gap",
        )

    evidence: dict[str, Any] = {}
    all_matched = True
    for condition in rule.conditions:
        matched, actual_value = evaluate_condition(context, condition)
        evidence[condition.path] = actual_value if actual_value is not PathNotFound else "not_available"
        all_matched = all_matched and matched

    quality = "computed"
    if any(v == "not_available" for v in evidence.values()):
        quality = "data_gap"
    elif rule.contradictions:
        quality = "computed_with_conflict"
    elif getattr(rule, "computation_model", "classical") == "practical_proxy":
        quality = "computed_simplified"

    return RuleEvaluation(
        rule_id=rule.id,
        title=rule.title,
        matched=all_matched,
        chart_evidence=evidence,
        outputs=rule.outputs if all_matched else [],
        confidence=rule.confidence,
        source_tier=rule.source_tier,
        status=rule.status,
        quality=quality,
    )


def evaluate_rule_set(rules: list[Rule], context: dict[str, Any]) -> list[RuleEvaluation]:
    return [evaluate_rule(rule, context) for rule in rules]
