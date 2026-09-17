"""The Jyotisha + project-architecture learning registry (build_plan.md
Phase 7: "make the cheat sheet a learning platform -- just by reading it,
anyone should learn Jyotisha and this project's thought process").

Every entry is a `ConceptEntry` (app.engine.cheatsheet.models) covering ONE
classical concept this codebase actually implements: what it classically
means (with a citation), how this project computes it (file:function),
its current honesty label, and every caveat/known-conflict a reader needs
before trusting it. This is the single generated source for:

  1. `docs/JYOTISHA_CHEATSHEET.md` (scripts/generate_cheatsheet.py) --
     the human-readable learning document.
  2. `cheatsheet_concepts` DB table (app.db.models, synced by
     scripts/sync_db.py) -- queryable concept metadata.
  3. `extract_concept_claims()` (app.engine.cheatsheet.extractor) --
     live "does this concept still have a working calculator" checks,
     feeding the same Cross-Validation Console UI as every other claim.

Editorial rule: this file (and its two data halves,
`concepts_foundations.py` and `concepts_domains.py` -- split purely to
respect this project's 600-line-per-file guideline, not a scope or
ownership split) is DATA, not logic. If a concept's code_ref stops
existing, that's a real regression the differ will catch (verdict
`mismatch`) -- never silently update this file to hide a code deletion.
`docs/*.md` remain the authoritative prose source for anything more than
this summary; every entry's `primary_citation` points a reader there or to
the classical text itself, never claims to replace it.
"""
from __future__ import annotations

from app.engine.cheatsheet.concepts_domains import CONCEPTS_DOMAINS
from app.engine.cheatsheet.concepts_foundations import CONCEPTS_FOUNDATIONS
from app.engine.cheatsheet.models import ConceptEntry

CONCEPTS: list[ConceptEntry] = CONCEPTS_FOUNDATIONS + CONCEPTS_DOMAINS


def get_concept(concept_id: str) -> ConceptEntry | None:
    for entry in CONCEPTS:
        if entry.concept_id == concept_id:
            return entry
    return None


def concepts_by_category() -> dict[str, list[ConceptEntry]]:
    grouped: dict[str, list[ConceptEntry]] = {}
    for entry in CONCEPTS:
        grouped.setdefault(entry.category, []).append(entry)
    return grouped
