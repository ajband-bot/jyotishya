"""Simplified transit engine built on Swiss Ephemeris sidereal positions.

This module focuses on rule-triggering transits rather than full predictive prose.
"""
from __future__ import annotations

from datetime import date
from typing import Any

import swisseph as swe

from app.astro.constants import SIGNS
from app.astro.engine import _norm, _resolve_node_id, julian_day

_TRANSIT_PLANETS = [
    (swe.SUN, "Sun"),
    (swe.MOON, "Moon"),
    (swe.MARS, "Mars"),
    (swe.MERCURY, "Mercury"),
    (swe.JUPITER, "Jupiter"),
    (swe.VENUS, "Venus"),
    (swe.SATURN, "Saturn"),
]

_FLAGS = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED

JUPITER_AUSPICIOUS_FROM_MOON = {1, 2, 4, 5, 7, 9, 10, 11}
JUPITER_CHALLENGING_FROM_MOON = {3, 6, 8, 12}
SATURN_SADE_SATI = {12, 1, 2}
SATURN_KANTAKA = {4, 7, 10}
MARRIAGE_JUPITER_TRIGGERS = {1, 5, 7, 9, 11}

# Simple "good house from Moon" gochara table -- build_plan.md Phase 5
# ("Transit engine -- gochara + Sade Sati status"). This is the classical
# SECONDARY/simplified gochara heuristic (BPHS/Phaladeepika); the PRIMARY,
# more rigorous classical method is Ashtakavarga-bindu-based transit
# judgment, already built separately in app.derived.ashtakavarga
# (classical_ashtakavarga()'s current_transits, SAV>=30 + BAV>=4 =
# favorable -- cross-checked exactly against OpenJyotish's calc/gochara.py
# SAV_GOOD_THRESHOLD=30/BAV_GOOD_THRESHOLD=4 constants). Both methods are
# surfaced side by side by app.derived.gochara.gochara_report() rather than
# silently picking one, per Cardinal Rule 3 -- classical texts themselves
# use Ashtakavarga to REFINE, not replace, the simple house-based read.
#
# Sun/Mars/Mercury/Venus/Rahu/Ketu rows below are the widely-taught
# Parashari convention (practically universal across modern practitioner
# references). The Moon row was independently cross-checked (AD-4,
# data-only) against OpenJyotish's calc/muhurta.py
# `_CHANDRA_BALA_GOOD_HOUSES = (1, 3, 6, 7, 10, 11)` -- exact match. The
# Jupiter/Saturn rows reuse this module's OWN existing, already-tested
# JUPITER_AUSPICIOUS_FROM_MOON / (SATURN_KANTAKA complement) sets rather
# than restating a second, possibly-drifting copy.
SIMPLE_GOCHARA_GOOD_HOUSES = {
    "Sun": {3, 6, 10, 11},
    "Moon": {1, 3, 6, 7, 10, 11},
    "Mars": {3, 6, 11},
    "Mercury": {2, 4, 6, 8, 10, 11},
    "Jupiter": JUPITER_AUSPICIOUS_FROM_MOON,
    "Venus": {1, 2, 3, 4, 5, 8, 9, 11, 12},
    "Saturn": {3, 6, 11},
    "Rahu": {3, 6, 10, 11},
    "Ketu": {3, 6, 11},
}
SIMPLE_GOCHARA_CITATION_STATUS = {
    "Sun": "pending_audit", "Moon": "verified_against_openjyotish", "Mars": "pending_audit",
    "Mercury": "pending_audit", "Jupiter": "verified_by_engine", "Venus": "pending_audit",
    "Saturn": "verified_by_engine", "Rahu": "pending_audit", "Ketu": "pending_audit",
}
MARRIAGE_JUPITER_TRIGGERS = {1, 5, 7, 9, 11}


def sign_name(sign_no: int) -> str:
    return SIGNS[sign_no - 1]["en"]


def relative_sign(from_sign: int, to_sign: int) -> int:
    return ((to_sign - from_sign) % 12) + 1


def transit_chart(on_date: date, utc_offset: float = 5.5, node_type: str = "mean") -> dict[str, Any]:
    """Return sidereal transit positions for a calendar date at local noon.

    node_type mirrors app.astro.engine.all_planets_sidereal's knob -- pass
    the same value used for the natal chart so Rahu/Ketu transit-to-natal
    comparisons stay internally consistent (mixing mean-node natal with
    true-node transit, or vice versa, would silently corrupt every
    relative_sign() call downstream).
    """
    node_id = _resolve_node_id(node_type)
    jd = julian_day(on_date.year, on_date.month, on_date.day, 12.0, utc_offset)
    result: dict[str, Any] = {}
    for pid, name in _TRANSIT_PLANETS + [(node_id, "Rahu")]:
        pos, _ = swe.calc_ut(jd, pid, _FLAGS)
        sid_lon = _norm(pos[0])
        sign = int(sid_lon / 30) + 1
        result[name] = {
            "longitude": round(sid_lon, 4),
            "sign": sign,
            "sign_en": sign_name(sign),
            "deg_in_sign": round(sid_lon % 30, 4),
            "retrograde": pos[3] < 0,
            "speed": round(pos[3], 6),
        }
    rahu_lon = result["Rahu"]["longitude"]
    ketu_lon = _norm(rahu_lon + 180.0)
    ketu_sign = int(ketu_lon / 30) + 1
    result["Ketu"] = {
        "longitude": round(ketu_lon, 4),
        "sign": ketu_sign,
        "sign_en": sign_name(ketu_sign),
        "deg_in_sign": round(ketu_lon % 30, 4),
        "retrograde": True,
        "speed": result["Rahu"]["speed"],
    }
    return result


def sade_sati_phase(natal_moon_sign: int, transit_saturn_sign: int) -> dict[str, Any]:
    rel = relative_sign(natal_moon_sign, transit_saturn_sign)
    if rel == 12:
        return {"active": True, "phase": 1, "label": "Phase 1"}
    if rel == 1:
        return {"active": True, "phase": 2, "label": "Phase 2"}
    if rel == 2:
        return {"active": True, "phase": 3, "label": "Phase 3"}
    return {"active": False, "phase": None, "label": "Inactive"}


def transit_assessment(natal_chart: dict[str, Any], on_date: date, node_type: str = "mean") -> dict[str, Any]:
    transits = transit_chart(on_date, node_type=node_type)
    moon_sign = natal_chart["Moon"]["sign"]
    lagna_sign = natal_chart["Lagna"]["sign"]
    sun_sign = natal_chart["Sun"]["sign"]

    jupiter_rel_moon = relative_sign(moon_sign, transits["Jupiter"]["sign"])
    jupiter_rel_lagna = relative_sign(lagna_sign, transits["Jupiter"]["sign"])
    saturn_rel_moon = relative_sign(moon_sign, transits["Saturn"]["sign"])
    saturn_rel_lagna = relative_sign(lagna_sign, transits["Saturn"]["sign"])
    rahu_rel_moon = relative_sign(moon_sign, transits["Rahu"]["sign"])
    ketu_rel_moon = relative_sign(moon_sign, transits["Ketu"]["sign"])

    if jupiter_rel_moon in JUPITER_AUSPICIOUS_FROM_MOON:
        jupiter_quality = "auspicious"
    elif jupiter_rel_moon in JUPITER_CHALLENGING_FROM_MOON:
        jupiter_quality = "challenging"
    else:
        jupiter_quality = "mixed"

    saturn_phase = sade_sati_phase(moon_sign, transits["Saturn"]["sign"])
    saturn_quality = "kantaka" if saturn_rel_moon in SATURN_KANTAKA else ("sade_sati" if saturn_phase["active"] else "neutral")

    marriage_alignment = {
        "jupiter_from_moon": jupiter_rel_moon in MARRIAGE_JUPITER_TRIGGERS,
        "jupiter_from_lagna": jupiter_rel_lagna in {1, 7},
        "saturn_not_ashtama": saturn_rel_moon != 8,
        "rahu_ketu_h1_h7": rahu_rel_moon in {1, 7} or ketu_rel_moon in {1, 7},
    }

    return {
        "date": on_date.isoformat(),
        "transits": transits,
        "references": {
            "from_moon": {
                "Jupiter": jupiter_rel_moon,
                "Saturn": saturn_rel_moon,
                "Rahu": rahu_rel_moon,
                "Ketu": ketu_rel_moon,
            },
            "from_lagna": {
                "Jupiter": jupiter_rel_lagna,
                "Saturn": saturn_rel_lagna,
            },
            "from_sun": {
                "Jupiter": relative_sign(sun_sign, transits["Jupiter"]["sign"]),
                "Saturn": relative_sign(sun_sign, transits["Saturn"]["sign"]),
            },
        },
        "jupiter_assessment": {
            "quality": jupiter_quality,
            "transit_sign": transits["Jupiter"]["sign_en"],
        },
        "saturn_assessment": {
            "quality": saturn_quality,
            "sade_sati": saturn_phase,
            "transit_sign": transits["Saturn"]["sign_en"],
        },
        "marriage_alignment": marriage_alignment,
    }
