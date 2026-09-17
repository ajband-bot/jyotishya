"""Rule Engine v2 — generic, data-driven Rule schema (Pydantic).

This is the schema referenced in docs/technical-architecture.md §4.3.
It exists to fix the single largest spec-compliance gap in the codebase:
`app/rules/evaluator.py` (v1) is a hardcoded `if rule_id == "RC-001": ...`
chain — every new rule requires editing Python. That violates the build
spec's §6 mandate ("Never store rules as prose only... keep all rules
data-driven and editable") and the DRY principle.

v1 (`app/rules/bphs_top20_rule_cards_v1.yaml` + `evaluator.py`) is NOT
deleted or broken by this module — it remains the rich provenance/citation
layer and keeps passing `tests/run_suite.py` unchanged. This module is the
new, generic execution path that future rules (and eventually migrated v1
rules) should target.
"""
from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

Operator = Literal[
    "eq", "neq", "in", "not_in", "gt", "lt", "gte", "lte",
    "house_in", "contains",
]

# 2026-09-16 (build_plan.md Phase 0 finding): extended from the original 9
# categories. docs/rule-v1-to-v2-parity.md §2 found roughly half of the 48
# v1 rule cards (all 18 nakshatra rules, both arudha/bhavapada rules, both
# argala rules, both karaka rules, and the two strength-aggregation rules)
# had no honest home in the original enum. Added rather than force-fit, per
# AGENTS.md Cardinal Rule 2 (never fabricate) applied to metadata, not just
# chart facts -- a rule mis-categorized as "lord_placement" when it's really
# a nakshatra rule is a small but real dishonesty.
RuleCategory = Literal[
    "functional_nature", "lord_placement", "dignity", "aspect",
    "yoga", "dasha", "transit", "varga", "event",
    "nakshatra", "arudha", "argala", "karaka", "bhava_signification", "strength",
    # 2026-09-16 (build_plan.md Phase 2 groundwork, same precedent as Phase 0's
    # 6-category addition): docs/dosha-registry.md mandates 6 doshas + Sade
    # Sati be checked for every chart, and the target rule inventory names
    # "Dosha rules + cancellations (~15)" as a distinct compiled set -- yet no
    # category existed for it (doshas were never force-fit into "yoga" here,
    # since the corpus and app/derived/doshas.py both treat dosha as its own
    # first-class concept, not a yoga subtype). Additive only, per Cardinal
    # Rule 2 applied to metadata -- no existing rule reclassified.
    "dosha",
    # 2026-09-17 (build_plan.md Phase 6 groundwork, same additive precedent as
    # Phase 0/2's earlier extensions): domain-playbooks.md's Marriage/Career
    # frameworks and the Remedy Safety Rules are each their own first-class
    # classical topic -- distinct from generic lord_placement/bhava_signification
    # (which describe a single house/planet fact, not a domain-specific synthesis
    # or a safety-gated prescription). Additive only, per Cardinal Rule 2 applied
    # to metadata -- no existing rule reclassified.
    "marriage", "career", "remedy",
]

RuleStatus = Literal[
    "DRAFT", "SOURCE_FOUND", "VERIFIED", "ACTIVE", "DEPRECATED", "CONTESTED",
]

Confidence = Literal["high", "medium", "low"]


class RuleCondition(BaseModel):
    """A single evaluable condition against the chart-context dict.

    `path` is a dotted lookup, e.g. "chart.Mercury.house" or
    "combustion.Mercury.combust". Resolved via `resolve_path()` below.
    """

    path: str
    op: Operator
    value: Any = None
    description: str | None = None


class RuleOutput(BaseModel):
    """What a matched rule produces — never raw prose, always structured."""

    kind: Literal["classification", "connection", "yoga_flag", "score_modifier"]
    payload: dict[str, Any]


class Rule(BaseModel):
    id: str
    title: str
    category: RuleCategory
    source_tier: Literal[1, 2, 3, 4, 5]
    source_ref: str
    tradition: str = "parasari"
    conditions: list[RuleCondition] = Field(default_factory=list)
    outputs: list[RuleOutput] = Field(default_factory=list)
    confidence: Confidence = "medium"
    status: RuleStatus = "DRAFT"
    contradictions: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)
    # 2026-09-16 (build_plan.md Phase 2, compositional rule sets): additive
    # field for rules whose outputs are a deterministic synthesis of
    # already-cited primitives (e.g. combining two houses' significations,
    # per BPHS's own bhava-connection teaching method) rather than a direct
    # verse-by-verse citation for that exact combination. Mirrors the
    # existing computed_simplified quality label's own "practical proxy"
    # definition (docs/validation-document-spec.md) -- lets the generic
    # evaluator honestly downgrade quality even when every condition
    # resolves cleanly (Cardinal Rule 4/9: say so, don't silently claim
    # full-fidelity citation depth).
    computation_model: Literal["classical", "practical_proxy"] = "classical"

    def is_executable(self) -> bool:
        """A rule with zero conditions can never be data-driven-evaluated —
        it's documentation only, not yet compiled (see architecture §4.3
        migration path / `compiled` flag concept)."""
        return len(self.conditions) > 0


class RuleEvaluation(BaseModel):
    rule_id: str
    title: str
    matched: bool
    chart_evidence: dict[str, Any]
    outputs: list[RuleOutput]
    confidence: Confidence
    source_tier: int
    status: RuleStatus
    quality: Literal["computed", "computed_simplified", "computed_with_conflict", "data_gap"]
