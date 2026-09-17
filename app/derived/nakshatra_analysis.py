"""Nakṣatra analysis engine (build_plan.md Phase 4: "compile nakshatra
profiles (27)"). Per-planet nakṣatra assignment (id/pada/lord/deity from
app.astro.constants.NAKSHATRAS, gaṇa/tattva/yoni/motivation from
app.knowledge.nakshatras) plus the MANDATORY gaṇḍānta check
(docs/nakshatra-framework.md §5).

VARGA-AWARE in the same sense as app.derived.aspects: every function takes
a plain sidereal longitude, not a raw chart dict, so it works for D1 or any
other longitude source.
"""
from __future__ import annotations

from typing import Any

from app.astro.constants import NAKSHATRAS
from app.astro.engine import get_nakshatra
from app.knowledge.nakshatras import CITATION, GANA_TEMPERAMENT, NAKSHATRA_PROFILES

ALL_PLANETS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]

# docs/nakshatra-framework.md \u00a75: junction longitude, gaṇḍānta orb (3\u00b020'),
# and the tighter Abhukta M\u016bla orb (48 arcminutes) specific to the
# Jyeshtha-M\u016bla (Scorpio-Sagittarius) junction, the most feared of the three.
GANDANTA_JUNCTIONS = {
    "cancer_leo": 120.0,
    "scorpio_sagittarius": 240.0,
    "pisces_aries": 0.0,
}
GANDANTA_ORB_DEG = 200.0 / 60.0  # 3\u00b020'
ABHUKTA_MULA_ORB_DEG = 48.0 / 60.0  # 48 arcminutes


def _circular_distance(a: float, b: float) -> float:
    diff = abs(a - b) % 360.0
    return min(diff, 360.0 - diff)


def check_gandanta(longitude: float) -> dict[str, Any]:
    for junction_name, junction_deg in GANDANTA_JUNCTIONS.items():
        distance = _circular_distance(longitude, junction_deg)
        if distance <= GANDANTA_ORB_DEG:
            abhukta_mula = junction_name == "scorpio_sagittarius" and distance <= ABHUKTA_MULA_ORB_DEG
            return {
                "in_gandanta": True,
                "junction": junction_name,
                "orb_deg": round(distance, 4),
                "abhukta_mula": abhukta_mula,
            }
    return {"in_gandanta": False, "junction": None, "orb_deg": None, "abhukta_mula": False}


def nakshatra_profile(longitude: float) -> dict[str, Any]:
    """Full nakṣatra profile for a single sidereal longitude -- id, name,
    lord, deity, pada (all from NAKSHATRAS), plus gaṇa/tattva/yoni/
    motivation (from NAKSHATRA_PROFILES) and the gaṇḍānta check."""
    result = get_nakshatra(longitude)
    nak = result["nakshatra"]
    profile = NAKSHATRA_PROFILES[nak["id"]]
    gana = profile["gana"]
    return {
        "nakshatra_id": nak["id"],
        "nakshatra_en": nak["en"],
        "lord": nak["lord"],
        "deity": nak["deity"],
        "pada": result["pada"],
        "gana": gana,
        "gana_temperament": GANA_TEMPERAMENT[gana],
        "tattva": profile["tattva"],
        "yoni": profile["yoni"],
        "motivation": profile["motivation"],
        "gandanta": check_gandanta(longitude),
        "citation": CITATION,
    }


def nakshatra_analysis_report(chart: dict[str, Any]) -> dict[str, Any]:
    """Per-planet nakshatra profiles for every planet in the chart, keyed
    by planet name -- Moon's entry is the Janma Nak\u1e63atra (the primary
    application per docs/nakshatra-framework.md \u00a72)."""
    return {
        planet: nakshatra_profile(chart[planet]["longitude"])
        for planet in ALL_PLANETS if planet in chart
    }
