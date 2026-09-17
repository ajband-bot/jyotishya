"""Composed daśā-lord analysis (build_plan.md Phase 2 item 7) --
replaces MD x AD canned/prose interpretation as the PRIMARY logic source.

Nothing in this codebase previously hardcoded MD x AD combination prose
(the 81-combination canned-text pattern build_plan.md warns about lives
only in the markdown corpus, which AGENTS.md \u00a76 already treats as
documentation-only, never runtime truth) -- so this module is Phase 2's
forward-looking fix: give the eventual Narrative Composer (Phase 3) a real,
structured, DRY alternative to reach for, built entirely by COMPOSING
already-computed Phase 1/2 primitives for whichever planet is actually
running, rather than a lookup table of 81 static blurbs.

For any dasha-lord planet, the synthesis assembles:
  - functional nature classification (app.derived.functional_nature)
  - houses owned + their Bhava Bala (app.derived.bhava_bala)
  - dispositor chain terminus (app.derived.dispositors)
  - current avastha (app.derived.bhava_bala)
  - current transit quality for that planet, if it is Jupiter or Saturn
    (the two planets app.astro.transits already assesses in depth)
  - Graha Maitri relationship between the MD lord and the running AD lord
    (app.derived.dignities) -- BPHS holds a hostile MD/AD lord pairing to
    behave very differently from a friendly one, regardless of either
    planet's individual strength
"""
from __future__ import annotations

from typing import Any

from app.derived.dignities import naisargika_relationship


def _lord_synthesis(planet: str, ctx: dict[str, Any]) -> dict[str, Any]:
    functional = ctx["functional_nature"]["planets"].get(planet)
    avastha = ctx["avasthas"].get(planet)
    dispositor = ctx["dispositors"]["chains"].get(planet)
    owned_houses = functional["owned_houses"] if functional else []
    bhava_bala_for_owned = {
        house: ctx["bhava_bala"]["houses"][house]["verdict"] for house in owned_houses
    }

    transit_note = None
    if planet in ("Jupiter", "Saturn"):
        key = "jupiter_assessment" if planet == "Jupiter" else "saturn_assessment"
        transit_note = ctx["transits"].get(key, {}).get("quality")

    return {
        "planet": planet,
        "functional_classification": functional["classification"] if functional else "data_gap -- Rahu/Ketu functional nature via sign-lordship does not apply",
        "owned_houses": owned_houses,
        "bhava_bala_of_owned_houses": bhava_bala_for_owned,
        "avastha": avastha,
        "dispositor_terminus": dispositor,
        "current_transit_quality": transit_note,
    }


def dasha_stack_synthesis(ctx: dict[str, Any]) -> dict[str, Any]:
    """Compose synthesis for whichever MD/AD/PD is currently running, per
    `ctx['current_dasha']` (app.astro.dashas.current_dasha_antar output)."""
    current = ctx.get("current_dasha") or {}
    stack: dict[str, Any] = {}
    md_planet = current.get("mahadasha", {}).get("planet")
    ad_planet = current.get("antardasha", {}).get("planet")
    pd_planet = current.get("pratyantardasha", {}).get("planet")

    for role, planet in (("mahadasha", md_planet), ("antardasha", ad_planet), ("pratyantardasha", pd_planet)):
        if planet:
            stack[role] = _lord_synthesis(planet, ctx)

    md_ad_relationship = None
    if md_planet and ad_planet and md_planet != ad_planet:
        md_ad_relationship = {
            "md_to_ad": naisargika_relationship(md_planet, ad_planet),
            "ad_to_md": naisargika_relationship(ad_planet, md_planet),
            "citation": "BPHS Ch.4 Graha Maitri -- MD/AD lord mutual disposition modulates the sub-period's tone",
        }

    return {
        "stack": stack,
        "md_ad_relationship": md_ad_relationship,
        "citation": "Composed synthesis of already-computed Phase 1/2 primitives -- not a canned MDxAD lookup table (build_plan.md Phase 2 item 7)",
    }
