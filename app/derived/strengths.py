"""Simplified practical strength models derived from corpus guidance.

These are explicitly not full classical shastiamsa-precision implementations.
They are transparent, rule-oriented scoring layers intended to unlock runtime
reasoning until full classical calculators are added.
"""
from __future__ import annotations

from typing import Any

from app.astro.constants import PLANETS
from app.astro.engine import planet_state
from app.derived.factors import KENDRA, TRIKONA

NAISARGIKA_SCORES = {
    "Sun": 1.00,
    "Moon": 0.90,
    "Venus": 0.80,
    "Jupiter": 0.70,
    "Mercury": 0.60,
    "Mars": 0.50,
    "Saturn": 0.40,
    "Rahu": 0.45,
    "Ketu": 0.45,
}

DAY_STRONG = {"Sun", "Jupiter", "Venus"}
NIGHT_STRONG = {"Moon", "Mars", "Saturn"}
DIGBALA_HOUSES = {
    "Sun": 10,
    "Mars": 10,
    "Moon": 4,
    "Venus": 4,
    "Jupiter": 1,
    "Mercury": 1,
    "Saturn": 7,
}
BENEFICS = {"Moon", "Mercury", "Jupiter", "Venus"}
MALEFICS = {"Sun", "Mars", "Saturn", "Rahu", "Ketu"}


def _clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def _dignity_score(state: str) -> float:
    return {
        "exalted": 1.0,
        "own-sign": 0.9,
        "neutral": 0.6,
        "debilitated": 0.2,
    }.get(state, 0.55)


def _d9_score(state: str) -> float:
    return {
        "exalted": 1.0,
        "own-sign": 0.9,
        "neutral": 0.6,
        "debilitated": 0.2,
    }.get(state, 0.55)


def _house_bonus(house: int) -> float:
    if house in KENDRA and house in TRIKONA:
        return 0.25
    if house in KENDRA:
        return 0.18
    if house in TRIKONA:
        return 0.16
    if house in {3, 6, 10, 11}:
        return 0.08
    if house in {6, 8, 12}:
        return -0.12
    return 0.0


def _dig_score(planet: str, house: int) -> float:
    ideal = DIGBALA_HOUSES.get(planet)
    if ideal is None:
        return 0.55
    if house == ideal:
        return 1.0
    if house in KENDRA:
        return 0.72
    return 0.5


def _kala_score(planet: str, hour_local: int) -> float:
    is_day = 6 <= hour_local < 18
    if planet == "Mercury":
        return 0.6
    if is_day and planet in DAY_STRONG:
        return 0.8
    if (not is_day) and planet in NIGHT_STRONG:
        return 0.8
    if planet in {"Rahu", "Ketu"}:
        return 0.55
    return 0.45


def _chesta_score(retrograde: bool, speed: float) -> float:
    magnitude = abs(speed)
    if retrograde:
        return 0.9
    if magnitude < 0.2:
        return 0.75
    if magnitude < 0.8:
        return 0.65
    return 0.55


def _drik_score(planet: str, chart: dict[str, Any], aspect_map: dict[str, list[int]]) -> float:
    target_house = chart[planet]["house"]
    benefic_hits = 0
    malefic_hits = 0
    for other, hits in aspect_map.items():
        if other == planet:
            continue
        if target_house in hits:
            if other in BENEFICS:
                benefic_hits += 1
            elif other in MALEFICS:
                malefic_hits += 1
    return _clamp(0.55 + benefic_hits * 0.12 - malefic_hits * 0.12)


def simplified_shadbala_core(
    chart: dict[str, Any],
    d9_planets: dict[str, Any],
    combustion: dict[str, Any],
    aspect_map: dict[str, list[int]],
    hour_local: int,
) -> dict[str, Any]:
    """The one true Shadbala scoring loop -- takes primitives directly so it
    can be shared by both real charts (via simplified_shadbala, which pulls
    hour_local from the fixture) and the Chart Lab sandbox (which has no
    fixture, only a day/night toggle). d9_planets must already be the
    planet-keyed dict (i.e. navamsha_d9(...)["planets"]), not the raw
    navamsha_d9() return value."""
    scores: dict[str, Any] = {}
    for planet in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]:
        d1_state = planet_state(planet, chart[planet]["sign"])
        d9_state = d9_planets[planet]["state"]
        sthana = _clamp(_dignity_score(d1_state) + _house_bonus(chart[planet]["house"]) + (_d9_score(d9_state) - 0.6) * 0.35)
        if planet in combustion and combustion[planet]["combust"]:
            sthana = _clamp(sthana - 0.18)
        dig = _dig_score(planet, chart[planet]["house"])
        kala = _kala_score(planet, hour_local)
        chesta = _chesta_score(chart[planet]["retrograde"], chart[planet]["speed"])
        naisargika = NAISARGIKA_SCORES[planet]
        drik = _drik_score(planet, chart, aspect_map)
        total = round((sthana + dig + kala + chesta + naisargika + drik) / 6 * 100, 2)
        if total >= 78:
            verdict = "very_strong"
        elif total >= 64:
            verdict = "strong"
        elif total >= 48:
            verdict = "moderate"
        else:
            verdict = "weak"
        scores[planet] = {
            "model": "simplified_practical",
            "components": {
                "sthana_bala": round(sthana, 4),
                "dig_bala": round(dig, 4),
                "kala_bala": round(kala, 4),
                "chesta_bala": round(chesta, 4),
                "naisargika_bala": round(naisargika, 4),
                "drik_bala": round(drik, 4),
            },
            "combust": combustion.get(planet, {}).get("combust", False),
            "d9_state": d9_state,
            "total_score": total,
            "verdict": verdict,
        }
    return scores


def simplified_shadbala(context: dict[str, Any]) -> dict[str, Any]:
    chart = context["chart"]
    d9 = context["d9"]["planets"]
    combustion = context["combustion"]
    aspect_map = context["aspect_map"]
    hour_local = int(context["fixture"]["time_local"].split(":")[0])
    return simplified_shadbala_core(chart, d9, combustion, aspect_map, hour_local)


def simplified_varga_quality(context: dict[str, Any]) -> dict[str, Any]:
    chart = context["chart"]
    d9 = context["d9"]["planets"]
    quality = {}
    for planet in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]:
        d1_sign = chart[planet]["sign"]
        d9_sign = d9[planet]["sign"]
        d9_state = d9[planet]["state"]
        vargottama = d1_sign == d9_sign
        score = 50.0
        if vargottama:
            score += 20
        if d9_state == "exalted":
            score += 20
        elif d9_state == "own-sign":
            score += 15
        elif d9_state == "debilitated":
            score -= 20
        quality[planet] = {
            "model": "d1_d9_weighted",
            "vargottama": vargottama,
            "d9_state": d9_state,
            "score": round(_clamp(score / 100, 0, 1) * 100, 2),
        }
    return quality


def simplified_ishta_kashta(context: dict[str, Any], shadbala: dict[str, Any] | None = None) -> dict[str, Any]:
    chart = context["chart"]
    d9 = context["d9"]["planets"]
    combustion = context["combustion"]
    shadbala = shadbala or simplified_shadbala(context)
    out = {}
    for planet in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]:
        total = shadbala[planet]["total_score"]
        ishta = total
        if chart[planet]["house"] in {6, 8, 12}:
            ishta -= 10
        if combustion.get(planet, {}).get("combust"):
            ishta -= 12
        if d9[planet]["state"] == "debilitated":
            ishta -= 15
        if d9[planet]["state"] == "exalted":
            ishta += 10
        if planet in BENEFICS:
            ishta += 4
        if planet in MALEFICS:
            ishta -= 2
        ishta = round(max(0, min(100, ishta)), 2)
        kashta = round(100 - ishta, 2)
        if ishta >= 70:
            verdict = "high_ishta"
        elif ishta >= 50:
            verdict = "balanced"
        else:
            verdict = "high_kashta"
        out[planet] = {
            "model": "simplified_practical",
            "ishta": ishta,
            "kashta": kashta,
            "verdict": verdict,
        }
    return out
