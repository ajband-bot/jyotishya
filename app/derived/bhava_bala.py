"""Bhava Bala (house strength) + planet-condition/avastha layer
(build_plan.md Phase 2 item 5).

Two distinct classical mechanisms, kept separate (Cardinal Rule 3):

1. AVASTHA (planet condition) -- fully mechanical, classical, NOT a
   simplified proxy:
     - Baladi Avastha (BPHS Ch.7): a planet's degree within its sign maps
       to one of 5 life-stages (Bala/infant, Kumara/child, Yuva/youth,
       Vriddha/old, Mrita/dead), with the 6-degree bands read forward for
       odd signs and reversed for even signs. A planet in Mrita avastha is
       considered too weak to deliver its full significations; Bala/Yuva
       are considered capable/vigorous.
     - Jagradadi Avastha (dignity-based, widely cited Parashari
       convention): exalted/own-sign/moolatrikona -> Jagrat (awake, full
       expression); neutral -> Swapna (dreaming, partial expression);
       debilitated/enemy-sign -> Sushupti (sleeping, suppressed
       expression). Reuses `app.astro.engine.planet_state` (DRY).

2. BHAVA BALA (house strength) -- explicitly `computation_model:
   practical_proxy` / quality `computed_simplified`, same honesty pattern
   as `app.derived.strengths`'s simplified Shadbala. True classical Bhava
   Bala (BPHS Ch.27) is expressed in shashtiamsa units across 4 sub-balas
   requiring full Shadbala precision -- explicitly out of scope until the
   Phase 5 Shadbala audit (build_plan.md §5 item 10) resolves the
   Ojha/Drek granularity disagreement flagged in OpenJyotish's own
   TRIAGE.md. This module instead composes 3 already-computed, cited
   primitives into one transparent 0-100 house-strength proxy:
     - bhavadhipati_component : the house lord's simplified Shadbala score
     - occupant_component     : average simplified Shadbala of planets
                                 occupying the house (benefic-weighted)
     - drishti_component      : net benefic-minus-malefic graha-drishti
                                 hits on the house
"""
from __future__ import annotations

from typing import Any

from app.astro.engine import planet_state

ALL_PLANETS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
BENEFICS = {"Moon", "Mercury", "Jupiter", "Venus"}
MALEFICS = {"Sun", "Mars", "Saturn", "Rahu", "Ketu"}

BALADI_STAGES = ["Bala", "Kumara", "Yuva", "Vriddha", "Mrita"]
BALADI_CAPABLE = {"Bala": "developing", "Kumara": "developing", "Yuva": "capable", "Vriddha": "declining", "Mrita": "too_weak"}

JAGRADADI_MAP = {
    "exalted": "Jagrat", "own-sign": "Jagrat",
    "neutral": "Swapna",
    "debilitated": "Sushupti",
}


def baladi_avastha(deg_in_sign: float, sign_no: int) -> dict[str, Any]:
    """BPHS Ch.7: 5 bands of 6 degrees each; odd signs read forward
    (Aries=1 is odd), even signs read in reverse."""
    is_odd_sign = sign_no % 2 == 1
    band_index = min(int(deg_in_sign // 6), 4)
    if not is_odd_sign:
        band_index = 4 - band_index
    stage = BALADI_STAGES[band_index]
    return {
        "stage": stage,
        "capability": BALADI_CAPABLE[stage],
        "citation": "BPHS Ch.7 (Baladi Avastha, 5-fold degree-band life-stage)",
    }


def jagradadi_avastha(planet: str, sign_no: int) -> dict[str, Any]:
    state = planet_state(planet, sign_no)
    stage = JAGRADADI_MAP.get(state, "Swapna")
    return {
        "dignity_state": state,
        "stage": stage,
        "citation": "Widely-cited Parashari convention (dignity-based Jagrat/Swapna/Sushupti); not itself a numbered BPHS chapter table",
    }


def avastha_report(chart: dict[str, Any]) -> dict[str, Any]:
    report = {}
    for planet in ALL_PLANETS:
        if planet not in chart:
            continue
        data = chart[planet]
        report[planet] = {
            "baladi": baladi_avastha(data["deg_in_sign"], data["sign"]),
            "jagradadi": jagradadi_avastha(planet, data["sign"]),
        }
    return report


def _occupant_component(house: int, chart: dict[str, Any], shadbala: dict[str, Any]) -> float:
    occupants = [p for p in ALL_PLANETS if p in chart and chart[p]["house"] == house]
    if not occupants:
        return 50.0  # neutral baseline -- an empty house is neither strengthened nor weakened by occupation
    scores = []
    for planet in occupants:
        score = shadbala[planet]["total_score"]
        if planet in MALEFICS:
            score = 100 - score  # a malefic's *strength* can still stress the house; treat as a drag, not a boost
        scores.append(score)
    return sum(scores) / len(scores)


def _drishti_component(house: int, aspect_map: dict[str, list[int]]) -> float:
    benefic_hits = sum(1 for p in BENEFICS if house in aspect_map.get(p, []))
    malefic_hits = sum(1 for p in MALEFICS if house in aspect_map.get(p, []))
    return max(0.0, min(100.0, 50.0 + (benefic_hits - malefic_hits) * 12.5))


def bhava_bala_report(
    house_lords: dict[int, str],
    chart: dict[str, Any],
    shadbala: dict[str, Any],
    aspect_map: dict[str, list[int]],
) -> dict[str, Any]:
    houses: dict[int, dict[str, Any]] = {}
    for house in range(1, 13):
        lord = house_lords[house]
        bhavadhipati = shadbala[lord]["total_score"]
        occupant = _occupant_component(house, chart, shadbala)
        drishti = _drishti_component(house, aspect_map)
        total = round((bhavadhipati + occupant + drishti) / 3, 2)
        verdict = "strong" if total >= 65 else ("moderate" if total >= 45 else "weak")
        houses[house] = {
            "lord": lord,
            "components": {
                "bhavadhipati_bala": round(bhavadhipati, 2),
                "occupant_bala": round(occupant, 2),
                "drishti_bala": round(drishti, 2),
            },
            "total_score": total,
            "verdict": verdict,
        }
    return {
        "model": "simplified_practical_proxy",
        "houses": houses,
        "citation": "BPHS Ch.27 (Bhava Bala doctrine) -- simplified proxy pending full Shadbala precision (build_plan.md Phase 5)",
    }
