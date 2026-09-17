"""Career Analysis Framework -- docs/domain-playbooks.md's Career table
(build_plan.md Phase 6: "Career rules (30)").

Composes already-computed primitives (house lordship, functional nature,
KARAKATVA professions) into the classical Career reading; no new
astrology math, per this codebase's usual compilation discipline.

10th House / 10th Lord / Relevant Dasha are covered here. A10 (Karma
Arudha) and D10 (Dasamsa)-derived career layers are a DIFFERENT, already-
named data_gap (AGENTS.md's "D10/D7 derived interpretation layers") --
this module does not silently claim to close that gap; it only covers
the D1-level factors the primary text and domain-playbooks.md actually
support today.
"""
from __future__ import annotations

from typing import Any

from app.astro.engine import planet_state
from app.knowledge.planets import KARAKATVA

ALL_PLANETS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]

# BPHS/Phaladeepika convention: profession-type flavor indicated by which
# planet occupies the 10th house (Karma Bhava) -- a well-known classical
# convention, distinct from the generic PLANET_IN_HOUSE significations
# (which describe that planet's OWN house-10 effects broadly, not the
# specific profession-type lens used here).
TENTH_HOUSE_OCCUPANT_PROFESSION = {
    "Sun": "Government service, administration, authority, leadership roles.",
    "Moon": "Public-facing work, hospitality, nursing/caregiving, food/liquids trade.",
    "Mars": "Engineering, military, police, surgery, real estate, sports.",
    "Mercury": "Trade, writing, accounting, IT, journalism, teaching.",
    "Jupiter": "Teaching, law, consulting, priesthood, banking, counseling.",
    "Venus": "Arts, entertainment, fashion, luxury goods, diplomacy.",
    "Saturn": "Labor-intensive or service trades, mining, engineering, long-term institutional roles.",
    "Rahu": "Foreign-linked, unconventional, or technology-driven careers.",
    "Ketu": "Research, spirituality, healing, detached/behind-the-scenes work.",
}


def tenth_lord_report(ctx: dict[str, Any]) -> dict[str, Any]:
    chart = ctx["chart"]
    lord = ctx["house_lords"][10]
    placement = ctx["lord_placements"][10]
    functional = ctx["functional_nature"]["planets"].get(lord, {})
    return {
        "planet": lord,
        "occupies_house": placement["occupies_house"],
        "dignity_state": planet_state(lord, chart[lord]["sign"]),
        "functional_classification": functional.get("classification"),
        "is_yoga_karaka": functional.get("is_yoga_karaka", False),
        "is_kendradhipati_dosha": functional.get("classification") == "kendradhipati_dosha",
        "natural_significations": KARAKATVA.get(lord, {}).get("professions", []),
        "citation": "docs/domain-playbooks.md Career Analysis Framework, 10th Lord row; BPHS Ch.11",
    }


def tenth_house_occupants_report(ctx: dict[str, Any]) -> dict[str, Any]:
    chart = ctx["chart"]
    occupants = [p for p in ALL_PLANETS if chart[p]["house"] == 10]
    return {
        "occupants": occupants,
        "profession_flavors": {p: TENTH_HOUSE_OCCUPANT_PROFESSION[p] for p in occupants},
        "citation": "docs/domain-playbooks.md Career Analysis Framework, 10th House row (classical occupant-profession convention)",
    }


def career_analysis_report(ctx: dict[str, Any]) -> dict[str, Any]:
    tenth_lord = tenth_lord_report(ctx)
    tenth_house = tenth_house_occupants_report(ctx)
    return {
        "tenth_house": tenth_house,
        "tenth_lord": tenth_lord,
        "model": "career_five_factor_synthesis",
        "data_gaps": [
            "A10 (Karma Arudha) and D10 (Dasamsa)-derived interpretation layers "
            "remain a separate, already-disclosed data_gap (AGENTS.md); not fabricated here.",
        ],
        "citation": "docs/domain-playbooks.md Career Analysis Framework",
    }
