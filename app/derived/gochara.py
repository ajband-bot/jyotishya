"""Full 9-planet Gochara (transit) report -- build_plan.md Phase 5
("Transit engine -- gochara + Sade Sati status").

Composes two ALREADY-BUILT classical transit-judgment methods rather than
inventing a third:

  1. Simple good-house-from-Moon (app.astro.transits.SIMPLE_GOCHARA_GOOD_HOUSES)
     -- the secondary/quick classical heuristic.
  2. Ashtakavarga-bindu-based verdict (app.derived.ashtakavarga.classical_ashtakavarga,
     already Phase-1-built, cross-checked exactly against OpenJyotish's
     calc/gochara.py thresholds) -- the PRIMARY, more rigorous classical
     method for the 7 classical planets (Rahu/Ketu have no classical
     Parashari Ashtakavarga row -- disclosed as data_gap there already,
     inherited here rather than silently patched over).

When the two methods agree, confidence is high. When they disagree (a
real, classically-recognized possibility -- a sign can carry strong
Ashtakavarga bindus while sitting in a "bad" simple house, or vice versa),
this is surfaced explicitly as `computed_with_conflict`-flavoured evidence
rather than one method silently overriding the other (Cardinal Rule 3).
"""
from __future__ import annotations

from typing import Any

from app.astro.transits import SIMPLE_GOCHARA_GOOD_HOUSES, SIMPLE_GOCHARA_CITATION_STATUS, relative_sign

ALL_9_PLANETS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
CLASSICAL_7 = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]


def _simple_verdict(planet: str, house_from_moon: int) -> dict[str, Any]:
    good_houses = SIMPLE_GOCHARA_GOOD_HOUSES[planet]
    return {
        "house_from_moon": house_from_moon,
        "favorable": house_from_moon in good_houses,
        "citation_status": SIMPLE_GOCHARA_CITATION_STATUS[planet],
    }


def gochara_report(ctx: dict[str, Any]) -> dict[str, Any]:
    """Full 9-planet gochara report for a chart's CURRENT transit snapshot
    (`ctx['transits']`, itself computed for whatever date built
    build_chart_context() was called with)."""
    natal_moon_sign = ctx["chart"]["Moon"]["sign"]
    transit_positions = ctx["transits"]["transits"]
    ashtakavarga_transits = ctx["ashtakavarga"]["current_transits"]

    planets: dict[str, Any] = {}
    for planet in ALL_9_PLANETS:
        house_from_moon = relative_sign(natal_moon_sign, transit_positions[planet]["sign"])
        simple = _simple_verdict(planet, house_from_moon)
        av = ashtakavarga_transits.get(planet, {"model": "data_gap"})

        if av.get("model") == "data_gap":
            combined_verdict = "simple_method_only"
            agreement = None
        elif av["verdict"] == "mixed":
            # Ashtakavarga itself calls this sign neither clearly strong nor
            # weak -- don't force a hard agree/disagree verdict against the
            # simple method's binary read.
            combined_verdict = "ashtakavarga_mixed_simple_" + ("favorable" if simple["favorable"] else "unfavorable")
            agreement = None
        else:
            av_favorable = av["verdict"] == "favorable"
            agreement = simple["favorable"] == av_favorable
            if agreement and simple["favorable"]:
                combined_verdict = "favorable_both_methods_agree"
            elif agreement and not simple["favorable"]:
                combined_verdict = "challenging_both_methods_agree"
            else:
                combined_verdict = "methods_disagree"

        planets[planet] = {
            "transit_sign_en": transit_positions[planet]["sign_en"],
            "simple_gochara": simple,
            "ashtakavarga_gochara": av,
            "methods_agree": agreement,
            "combined_verdict": combined_verdict,
        }

    return {
        "planets": planets,
        "sade_sati": ctx["transits"].get("saturn_assessment", {}).get("sade_sati"),
        "citation": "Simple gochara: BPHS/Phaladeepika Parashari convention. Ashtakavarga gochara: BPHS Ashtakavarga adhyaya, cross-checked against OpenJyotish calc/gochara.py thresholds. Sade Sati: classical Saturn-from-Moon doctrine (app.astro.transits.sade_sati_phase).",
    }
