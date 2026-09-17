"""Dedicated Functional Benefic/Malefic engine (build_plan.md Phase 2 item 2)
-- deliberately separate from `app.derived.dignities` (Graha Maitri).

Dignity answers "how strong/comfortable is this planet in its sign."
Functional nature answers a completely different question: "does the
HOUSES THIS PLANET RULES for THIS Lagna help or hurt the native" -- and per
AGENTS.md Cardinal Rule 7, this overrides the planet's natural
benefic/malefic status. The two must never be merged into one score,
which is exactly the failure mode this dedicated module exists to prevent
(Cardinal Rule 3: distinct classical mechanisms, never blended).

Doctrine implemented (BPHS Ch.34):
  - A planet ruling a dusthana (6/8/12) is functionally malefic, full stop
    -- with ONE documented textual exception: a planet that is simultaneously
    the Lagna lord (rules H1) AND rules H8 keeps its auspicious character,
    because Lagna lordship (the single most important dispositorship) is
    held to outweigh the 8th's ordinarily inauspicious nature. Computing
    all 12 lagnas shows this exception is structurally possible for exactly
    one case (Aries Lagna, Mars owns H1+H8) -- flagged generically below,
    not hardcoded to Aries, so the logic stays correct if BPHS's own-sign
    table is ever revised.
  - A planet ruling a trikona (1/5/9) is functionally benefic (raja-yoga
    potential), regardless of natural nature.
  - A planet ruling a kendra (4/7/10) ONLY (no trikona) inverts natural
    nature: natural malefics become functionally benefic (the yoga-karaka
    mechanism for kendra-only rulership); natural benefics suffer
    "Kendradhipati Dosha" -- they do not turn malefic, but lose some of
    their unconditioned benefic purity (BPHS Ch.34's own qualification,
    most cited for Jupiter/Venus as sole kendra lords).
  - A planet ruling BOTH a kendra and a trikona (non-trivially, i.e. not
    just via H1's dual membership) is a yoga-karaka -- the strongest
    functional-benefic case, reusing the exact test already verified in
    `app.derived.factors.is_yoga_karaka` (DRY, not re-derived here).
  - 2nd/7th lordship (maraka) is an orthogonal flag, not a classification
    tier -- a trikona lord that also happens to rule a maraka house keeps
    its functional-benefic classification with the maraka flag noted
    alongside, never silently dropped.
"""
from __future__ import annotations

from typing import Any

KENDRA = {1, 4, 7, 10}
TRIKONA = {1, 5, 9}
DUSTHANA = {6, 8, 12}
MARAKA = {2, 7}

NATURAL_MALEFICS = {"Sun", "Mars", "Saturn", "Rahu", "Ketu"}
NATURAL_BENEFICS = {"Moon", "Mercury", "Jupiter", "Venus"}
CLASSICAL_7 = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]


def owned_houses(lagna_sign: int, planet: str, house_lord_fn) -> list[int]:
    return [house for house in range(1, 13) if house_lord_fn(lagna_sign, house) == planet]


def _is_yoga_karaka(owned: set[int]) -> bool:
    """Same non-trivial-membership test as app.derived.factors.is_yoga_karaka,
    restated on a house-set directly so this module has no import-cycle
    dependency on factors.py (factors.py already imports engines this module
    could plausibly need later)."""
    return any(h in {4, 7, 10} for h in owned) and any(h in {5, 9} for h in owned)


def classify_planet(lagna_sign: int, planet: str, house_lord_fn) -> dict[str, Any]:
    owned = owned_houses(lagna_sign, planet, house_lord_fn)
    owned_set = set(owned)
    if not owned:
        return {
            "planet": planet, "owned_houses": [], "classification": "no_lordship_for_this_lagna",
            "is_maraka": False, "is_yoga_karaka": False, "notes": [],
        }

    is_maraka = bool(owned_set & MARAKA)
    in_dusthana = owned_set & DUSTHANA
    in_trikona = owned_set & TRIKONA
    in_kendra = owned_set & KENDRA
    yoga_karaka = _is_yoga_karaka(owned_set)
    natural = "malefic" if planet in NATURAL_MALEFICS else ("benefic" if planet in NATURAL_BENEFICS else "neutral")

    notes: list[str] = []
    lagna_lord_exception = 1 in owned_set and in_dusthana == {8}

    if in_dusthana and not lagna_lord_exception:
        classification = "functional_malefic"
        notes.append(f"Rules dusthana house(s) {sorted(in_dusthana)} -- functional nature overrides natural nature (BPHS Ch.34).")
    elif in_dusthana and lagna_lord_exception:
        classification = "functional_benefic_with_dusthana_mitigation"
        notes.append(
            "Also rules H8 (dusthana), but is Lagna lord -- BPHS's documented Lagna-lordship-outweighs-8th exception applies; "
            "not classified as a straightforward functional malefic."
        )
    elif yoga_karaka:
        classification = "yoga_karaka"
        notes.append(f"Rules both a kendra and a trikona ({sorted(owned_set)}) -- strongest functional-benefic case (BPHS Ch.34).")
    elif in_trikona:
        classification = "functional_benefic"
        notes.append(f"Rules trikona house(s) {sorted(in_trikona)} -- functionally benefic regardless of natural nature.")
    elif in_kendra:
        if natural == "malefic":
            classification = "functional_benefic"
            notes.append(f"Natural malefic ruling kendra house(s) {sorted(in_kendra)} only -- functional nature overrides natural nature (BPHS Ch.34).")
        elif natural == "benefic":
            classification = "kendradhipati_dosha"
            notes.append(f"Natural benefic ruling kendra house(s) {sorted(in_kendra)} only -- Kendradhipati Dosha; loses some benefic purity, does not turn malefic.")
        else:
            classification = "neutral"
    else:
        classification = "neutral"
        notes.append(f"Rules only non-angular, non-trine house(s) {sorted(owned_set)} -- no functional-nature override applies.")

    if is_maraka:
        notes.append("Also rules a maraka house (2nd/7th) -- flagged independently of the classification above, never overriding it.")

    return {
        "planet": planet,
        "owned_houses": owned,
        "classification": classification,
        "natural_nature": natural,
        "is_maraka": is_maraka,
        "is_yoga_karaka": yoga_karaka,
        "notes": notes,
    }


def functional_nature_report(lagna_sign: int, house_lord_fn) -> dict[str, Any]:
    """Functional-nature classification for all 7 classical planets. Rahu/Ketu
    are deliberately excluded -- they do not own signs in core BPHS Ch.4/34
    doctrine, so "functional lordship" does not apply to them the same way
    (their functional role is judged via nakshatra/conjunction lordship, a
    separate and not-yet-built topic -- reported as data_gap, never guessed)."""
    return {
        "lagna_sign": lagna_sign,
        "planets": {planet: classify_planet(lagna_sign, planet, house_lord_fn) for planet in CLASSICAL_7},
        "rahu_ketu": "data_gap -- functional nature via sign-lordship does not apply to nodes; nakshatra/conjunction-lordship basis not yet implemented",
        "citation": "BPHS Ch.34",
    }
