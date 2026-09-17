"""Remedy Prescriptions -- docs/domain-playbooks.md's Remedy Safety Rules
(build_plan.md Phase 6: "Remedy prescriptions (20) -- gated on functional-
benefic/malefic classification being rule-driven").

Gated, as the plan requires, on app.derived.functional_nature -- the
already-built, already-tested functional-benefic/malefic engine (BPHS
Ch.34, AGENTS.md Cardinal Rule 7). This module adds NO new dignity/
lordship logic; it only implements the SAFETY GATE on top of it, per
domain-playbooks.md's numbered Remedy Safety Rules:

  1. Never gemstone for a functional malefic.
  2. Gemstone only after triple confirmation: (a) functional benefic for
     Lagna, (b) weak/afflicted, (c) not combust.
  3. Priority order: mantra -> dana -> fasting -> deity worship ->
     gemstone -> yantra -> nadi-specific. (Mantra/dana/fasting are always
     safe per Rule 4 -- reported unconditionally, no gating needed.)
  6. Saturn: NEVER blue sapphire unless Saturn is yogakaraka (Taurus/Libra
     Lagna) -- a STRICTER gate than the generic "functional_benefic" test,
     modeled explicitly below (`_saturn_gemstone_appropriate`).
  7. Rahu: NEVER hessonite unless Rahu is well-placed AND its dispositor
     is strong -- modeled explicitly below (`_rahu_gemstone_appropriate`).

Rahu/Ketu have no functional_nature classification (they don't own signs
-- app.derived.functional_nature's own documented exclusion). Both are
gemstone-INeligible by default here; Rahu has the one documented,
narrow exception above, Ketu has none documented in domain-playbooks.md
(not fabricated: reported as a permanent safe default, not an oversight).
"""
from __future__ import annotations

from typing import Any

from app.astro.constants import SIGNS

CLASSICAL_7 = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
ALL_9 = CLASSICAL_7 + ["Rahu", "Ketu"]
BENEFIC_CLASSIFICATIONS = {"functional_benefic", "yoga_karaka", "functional_benefic_with_dusthana_mitigation"}
GEMSTONE_MANTRA_DEITY = {
    "Sun": ("Om Suryaya Namah", "Surya / Aditya"), "Moon": ("Om Chandraya Namah", "Shiva (Chandrashekhara)"),
    "Mars": ("Om Angarakaya Namah", "Hanuman / Skanda"), "Mercury": ("Om Budhaya Namah", "Vishnu"),
    "Jupiter": ("Om Gurave Namah", "Brihaspati / Dakshinamurthy"), "Venus": ("Om Shukraya Namah", "Lakshmi"),
    "Saturn": ("Om Shanaischaraya Namah", "Hanuman / Shani"),
    "Rahu": ("Om Rahave Namah", "Durga"), "Ketu": ("Om Ketave Namah", "Ganesha"),
}


def _is_weak_or_afflicted(planet: str, ctx: dict[str, Any]) -> bool:
    shadbala_entry = ctx["shadbala"].get(planet, {})
    return shadbala_entry.get("verdict") in ("weak", "moderate")


def _saturn_gemstone_appropriate(classification: str | None, weak: bool, combust: bool) -> bool:
    """Rule 6: strictly yogakaraka-gated, NOT the generic functional_benefic
    test -- a natural-malefic-turned-functional-benefic-via-kendra-only
    inversion (functional_nature's own documented mechanism) is explicitly
    NOT enough for Saturn's blue sapphire."""
    return classification == "yoga_karaka" and weak and not combust


def _rahu_gemstone_appropriate(ctx: dict[str, Any]) -> dict[str, Any]:
    """Rule 7: well-placed (not in a dusthana) AND dispositor strong."""
    chart = ctx["chart"]
    house = chart["Rahu"]["house"]
    well_placed = house not in {6, 8, 12}
    dispositor = SIGNS[chart["Rahu"]["sign"] - 1]["lord"]
    dispositor_strong = ctx["shadbala"].get(dispositor, {}).get("verdict") in ("strong", "very_strong")
    return {
        "well_placed": well_placed,
        "dispositor": dispositor,
        "dispositor_strong": dispositor_strong,
        "well_placed_and_strong_dispositor": well_placed and dispositor_strong,
    }


def _planet_remedy(planet: str, ctx: dict[str, Any]) -> dict[str, Any]:
    mantra, deity = GEMSTONE_MANTRA_DEITY[planet]
    weak = _is_weak_or_afflicted(planet, ctx)
    combust = ctx["combustion"].get(planet, {}).get("combust", False)
    classification = ctx["functional_nature"]["planets"].get(planet, {}).get("classification") if planet in CLASSICAL_7 else None

    entry: dict[str, Any] = {
        "planet": planet,
        "classification": classification,
        "weak_or_afflicted": weak,
        "combust": combust,
        "mantra": mantra,
        "mantra_note": "Always safe (Remedy Safety Rule 4) -- aligns consciousness without amplifying malefic energy.",
        "deity": deity,
        "priority_order": ["mantra", "dana", "fasting", "deity_worship", "gemstone", "yantra", "nadi_specific"],
        "citation": "docs/domain-playbooks.md Remedy Safety Rules",
    }

    if planet == "Rahu":
        rahu_gate = _rahu_gemstone_appropriate(ctx)
        entry.update(rahu_gate)
        entry["gemstone_appropriate"] = False  # Rule 7's exception is a NECESSARY, not sufficient, gate
        entry["gemstone_contraindicated"] = not rahu_gate["well_placed_and_strong_dispositor"]
        entry["dana_preferred"] = True
        entry["remedy_note"] = "Sandalwood, Durga worship, abstinence from intoxicants (Remedy Safety Rule 7)."
        return entry

    if planet == "Ketu":
        entry["gemstone_appropriate"] = False
        entry["gemstone_contraindicated"] = True
        entry["dana_preferred"] = True
        entry["remedy_note"] = "No documented gemstone exception for Ketu in docs/domain-playbooks.md -- permanent safe default, not fabricated."
        return entry

    if planet == "Saturn":
        gemstone_ok = _saturn_gemstone_appropriate(classification, weak, combust)
        entry["gemstone_appropriate"] = gemstone_ok
        entry["gemstone_contraindicated"] = classification == "functional_malefic"
        entry["blocked_by_yogakaraka_gate"] = classification in BENEFIC_CLASSIFICATIONS and classification != "yoga_karaka"
        entry["dana_preferred"] = classification == "functional_malefic"
        entry["remedy_note"] = "Service to elderly/disabled, sesame oil, iron charity. NEVER blue sapphire unless Saturn is yogakaraka (Remedy Safety Rule 6)."
        return entry

    gemstone_ok = classification in BENEFIC_CLASSIFICATIONS and weak and not combust
    entry["gemstone_appropriate"] = gemstone_ok
    entry["gemstone_contraindicated"] = classification == "functional_malefic"
    entry["dana_preferred"] = classification == "functional_malefic"
    entry["remedy_note"] = (
        "Gemstone triple-confirmed (functional benefic + weak/afflicted + not combust) -- Remedy Safety Rule 2."
        if gemstone_ok else
        "Gemstone not indicated -- dana of this planet's significations is preferred (Remedy Safety Rule 5) when functionally malefic."
    )
    return entry


def remedy_report(ctx: dict[str, Any]) -> dict[str, Any]:
    return {
        "planets": {planet: _planet_remedy(planet, ctx) for planet in ALL_9},
        "model": "functional_nature_gated_remedy_safety",
        "citation": "docs/domain-playbooks.md Remedy Safety Rules",
    }
