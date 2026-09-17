"""Aspects / Drishti engine -- planetary (graha) drishti + generic
house-relationship classification (kendra/trikona/dushthana/chathusra).

Two distinct classical aspect systems are kept explicitly separate here
rather than conflated (Cardinal Rule 3 -- never silently blend distinct
classical concepts):

1. GRAHA DRISHTI (planetary aspect, BPHS): every planet aspects the 7th
   house from itself; Mars additionally aspects the 4th/8th, Jupiter the
   5th/9th, Saturn the 3rd/10th (`SPECIAL_GRAHA_DRISHTI`). This is what
   most BPHS-based yoga/dosha rules mean by "aspects" -- previously lived
   only as `app.derived.factors.planet_aspects`, which now delegates here
   so the rule lives in exactly one place (DRY).
2. HOUSE-RELATIONSHIP TYPES (kendra/trikona/dushthana/chathusra): a
   distance-based classification of any two houses' angular relationship,
   independent of which planet occupies them -- used for functional-nature
   classification, dosha logic, and Bhava-relationship rules. Definitions
   (relative house distance, 1-indexed, matching the `rel_house()`
   whole-sign-counting convention already used throughout this codebase):
     kendra     = {1, 4, 7, 10}   (quadrant)
     trikona    = {1, 5, 9}       (trine)
     dushthana  = {6, 8, 12}      (evil/malefic houses)
     chathusra  = {4, 8}          (the specific 4th/8th "square" relation)
   Cross-checked (AD-4, data-only, no code copied) against PyJHora's
   `horoscope/chart/house.py` (`kendra_aspects_of_the_raasi`,
   `trikona_aspects_of_the_raasi`, `dushthana_aspects_of_the_raasi`,
   `chathusra_aspects_of_the_raasi`) -- all four agree exactly on these
   relative-distance sets. A relationship pair can carry more than one
   label (distance 4 is both kendra AND chathusra) -- that overlap is
   classical, never collapsed to a single tag.

VARGA-AWARE: every function below takes a plain `{planet_name: house_no}`
mapping, never a raw D1/varga chart dict directly -- the identical engine
works for D1, D9, D10, or any `app.astro.vargas.compute_varga()` output via
the adapter functions at the bottom of this module. This directly answers
the build_plan.md Phase 1 ask for a "varga-aware" aspects engine.
"""
from __future__ import annotations

from typing import Any

KENDRA = {1, 4, 7, 10}
TRIKONA = {1, 5, 9}
DUSHTHANA = {6, 8, 12}
CHATHUSRA = {4, 8}

ALL_PLANETS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]

# Special graha drishti (BPHS): planet -> EXTRA houses (beyond the
# universal 7th) it aspects, counted from its own occupied house.
SPECIAL_GRAHA_DRISHTI: dict[str, list[int]] = {
    "Mars": [4, 8],
    "Jupiter": [5, 9],
    "Saturn": [3, 10],
}


def rel_house(from_house: int, to_house: int) -> int:
    """1-indexed relative distance from_house -> to_house (whole-sign counting)."""
    return ((to_house - from_house) % 12) + 1


def house_relationship_types(from_house: int, to_house: int) -> set[str]:
    """Classify `to_house` as seen from `from_house` against the four
    named distance-based relationship types (a pair may carry multiple)."""
    distance = rel_house(from_house, to_house)
    types = set()
    if distance in KENDRA:
        types.add("kendra")
    if distance in TRIKONA:
        types.add("trikona")
    if distance in DUSHTHANA:
        types.add("dushthana")
    if distance in CHATHUSRA:
        types.add("chathusra")
    return types


def graha_drishti_houses(planet: str, from_house: int) -> list[int]:
    """Houses a planet aspects via graha drishti (special rules + universal 7th)."""
    offsets = [7] + SPECIAL_GRAHA_DRISHTI.get(planet, [])
    return sorted({((from_house - 1 + offset - 1) % 12) + 1 for offset in offsets})


def build_aspect_map(planet_houses: dict[str, int]) -> dict[str, list[int]]:
    """Graha-drishti aspect map for every planet present in `planet_houses`
    (varga-agnostic -- works for D1 or any varga's house positions)."""
    return {
        planet: graha_drishti_houses(planet, house)
        for planet, house in planet_houses.items()
        if planet in ALL_PLANETS
    }


def mutual_aspects(planet_houses: dict[str, int]) -> list[tuple[str, str]]:
    """Pairs of planets that graha-drishti-aspect EACH OTHER."""
    aspect_map = build_aspect_map(planet_houses)
    pairs: list[tuple[str, str]] = []
    planets = list(planet_houses.keys())
    for i, p1 in enumerate(planets):
        if p1 not in aspect_map:
            continue
        for p2 in planets[i + 1:]:
            if p2 not in aspect_map:
                continue
            if planet_houses[p2] in aspect_map[p1] and planet_houses[p1] in aspect_map[p2]:
                pairs.append((p1, p2))
    return pairs


def _aspected_by(aspect_map: dict[str, list[int]]) -> dict[int, list[str]]:
    """Inverse index: for each house 1-12, which planets graha-drishti-aspect it."""
    result: dict[int, list[str]] = {house: [] for house in range(1, 13)}
    for planet, houses in aspect_map.items():
        for house in houses:
            result[house].append(planet)
    return result


def full_aspect_report(planet_houses: dict[str, int]) -> dict[str, Any]:
    """Combined report: graha-drishti aspect map, its inverse index, and
    mutual aspects -- for any chart's house positions (D1 or varga)."""
    aspect_map = build_aspect_map(planet_houses)
    return {
        "model": "classical_graha_drishti",
        "graha_drishti": aspect_map,
        "aspected_by": _aspected_by(aspect_map),
        "mutual_aspects": mutual_aspects(planet_houses),
    }


# ── Varga-agnostic adapters ────────────────────────────────────────────────
def planet_houses_from_d1_chart(chart: dict[str, Any]) -> dict[str, int]:
    """Extract {planet: house} from a raw D1 chart dict (app.astro.engine output)."""
    return {planet: chart[planet]["house"] for planet in ALL_PLANETS if planet in chart}


def planet_houses_from_varga(varga_data: dict[str, Any]) -> dict[str, int]:
    """Extract {planet: house} from an `app.astro.vargas.compute_varga()` result."""
    return {planet: data["house"] for planet, data in varga_data["planets"].items() if planet in ALL_PLANETS}
