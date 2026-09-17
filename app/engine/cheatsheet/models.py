"""Data models for the Cheat-Sheet Cross-Validation Console
(docs/technical-architecture.md 4.4) -- Ajay's explicit ask: run every
cheat sheet (rule cards, docs/*.md, guides) against computed chart output
side by side, so disagreements surface instead of silently drifting.
"""
from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel


class ClaimRecord(BaseModel):
    """One extracted, potentially-checkable assertion from a corpus document."""

    claim_id: str
    source_file: str
    section: str
    claim_text: str
    formula_ref: str | None = None       # e.g. rule_id this claim came from
    applies_to_chart: str | None = None  # chart_id, if the claim names a specific person
    # "concept_coverage" (Phase 7): one claim per app.engine.cheatsheet.concepts
    # registry entry -- "this concept has a live, callable calculator", the
    # same coverage-checking pattern the dosha registry already established,
    # generalized to the whole project's concept surface (build_plan.md
    # Phase 7 "Finish extractor.py/differ.py coverage").
    claim_type: Literal["house_ownership", "coverage", "dosha_protocol", "concept_coverage"] = "house_ownership"
    # For house_ownership claims: the structured assertion to check.
    lagna_sign: int | None = None
    planet: str | None = None
    claimed_houses: list[int] = []
    concept_id: str | None = None  # set for concept_coverage claims


class ValidationResult(BaseModel):
    claim: ClaimRecord
    computed_value: Any = None
    verdict: Literal["match", "mismatch", "unverifiable", "data_gap"]
    diff_detail: str


class ConceptEntry(BaseModel):
    """One entry in the Jyotisha + project-architecture learning registry
    (app.engine.cheatsheet.concepts.CONCEPTS) -- the Phase 7 "learning
    platform" cheat sheet. Every field is deliberately plain-text /
    human-readable: this registry is meant to be read top to bottom by a
    person who knows neither Jyotisha nor this codebase and come away
    understanding both the classical concept and exactly how (and how
    completely) this project computes it."""

    concept_id: str
    category: str
    sanskrit_term: str | None = None
    english_gloss: str
    classical_definition: str
    primary_citation: str
    code_ref: str | None = None          # "module:function", importlib-resolvable
    quality_label: Literal[
        "computed", "computed_simplified", "computed_with_conflict", "data_gap",
    ]
    caveats: list[str] = []
    cross_check_note: str = ""
