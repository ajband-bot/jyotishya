"""Graha Maitri (planetary friendship) dignities -- Naisargika (natural),
Tatkalika (temporal), and Panchadha (5-fold compound).

Three classical layers, per BPHS Ch.4:

1. NAISARGIKA (natural, chart-independent): fixed friend/enemy/neutral
   sets per planet, see `app.astro.constants.NATURAL_RELATIONSHIPS`.
2. TATKALIKA (temporal, chart-dependent): planets occupying houses
   2/3/4/10/11/12 *from a given planet's own house* are its temporal
   friends; those in 1/5/6/7/8/9 are its temporal enemies -- a strict
   2-way partition, no neutral tier. Cross-checked (AD-4, data-only)
   against PyJHora's `const.temporary_friend_raasi_positions` /
   `temporary_enemy_raasi_positions` -- exact agreement.
3. PANCHADHA (5-fold compound): combines the two above via the standard
   classical lookup table below, cross-checked against PyJHora's
   `horoscope/chart/house.py::_get_compound_relationships_of_planets` --
   exact agreement on all 5 compound categories and their score values:
     natural friend + temporal friend -> Adhi Mitra  (Best Friend, 4)
     natural neutral + temporal friend -> Mitra       (Friend, 3)
     natural friend + temporal enemy  -> Sama         (Neutral, 2)
     natural enemy  + temporal friend -> Sama         (Neutral, 2)
     natural neutral + temporal enemy -> Shatru       (Enemy, 1)
     natural enemy  + temporal enemy  -> Adhi Shatru  (Bitter Enemy, 0)

This feeds functional-nature classification (AGENTS.md Cardinal Rule 7)
and Shadbala's Sthana Bala component with a real, explicit basis instead
of an implicit one baked into `app.derived.strengths`'s simplified scoring.

VARGA-AWARE (Tatkalika/Panchadha only -- Naisargika never varies by
chart): takes a plain `{planet: house}` mapping, so the identical engine
works for D1 or any `app.astro.vargas.compute_varga()` output, matching
the same pattern as `app.derived.aspects`.
"""
from __future__ import annotations

from typing import Any

from app.astro.constants import NATURAL_RELATIONSHIPS, NATURAL_RELATIONSHIP_SOURCE_TIER
from app.derived.aspects import ALL_PLANETS, rel_house

TEMPORAL_FRIEND_HOUSES = {2, 3, 4, 10, 11, 12}
TEMPORAL_ENEMY_HOUSES = {1, 5, 6, 7, 8, 9}

PANCHADHA_TABLE = {
    ("friend", "friend"): "adhi_mitra",
    ("neutral", "friend"): "mitra",
    ("friend", "enemy"): "sama",
    ("enemy", "friend"): "sama",
    ("neutral", "enemy"): "shatru",
    ("enemy", "enemy"): "adhi_shatru",
}
PANCHADHA_SCORE = {"adhi_mitra": 4, "mitra": 3, "sama": 2, "shatru": 1, "adhi_shatru": 0}
PANCHADHA_LABEL = {
    "adhi_mitra": "Adhi Mitra (Best Friend)",
    "mitra": "Mitra (Friend)",
    "sama": "Sama (Neutral)",
    "shatru": "Shatru (Enemy)",
    "adhi_shatru": "Adhi Shatru (Bitter Enemy)",
}


def naisargika_relationship(planet: str, other: str) -> str:
    """Fixed natural relationship of `other` as seen from `planet`."""
    relations = NATURAL_RELATIONSHIPS[planet]
    if other in relations["friends"]:
        return "friend"
    if other in relations["enemies"]:
        return "enemy"
    return "neutral"


def tatkalika_relationship(planet_houses: dict[str, int], planet: str, other: str) -> str:
    """Temporal relationship of `other` as seen from `planet`'s current house."""
    distance = rel_house(planet_houses[planet], planet_houses[other])
    return "friend" if distance in TEMPORAL_FRIEND_HOUSES else "enemy"


def panchadha_relationship(naisargika: str, tatkalika: str) -> str:
    return PANCHADHA_TABLE[(naisargika, tatkalika)]


def graha_maitri_report(planet_houses: dict[str, int]) -> dict[str, Any]:
    """Full Naisargika + Tatkalika + Panchadha report for every planet pair
    present in `planet_houses` (varga-agnostic via the same adapters as
    `app.derived.aspects`)."""
    planets = [p for p in ALL_PLANETS if p in planet_houses]
    per_planet: dict[str, Any] = {}
    for planet in planets:
        relationships = {}
        for other in planets:
            if other == planet:
                continue
            naisargika = naisargika_relationship(planet, other)
            tatkalika = tatkalika_relationship(planet_houses, planet, other)
            panchadha = panchadha_relationship(naisargika, tatkalika)
            relationships[other] = {
                "naisargika": naisargika,
                "tatkalika": tatkalika,
                "panchadha": panchadha,
                "panchadha_label": PANCHADHA_LABEL[panchadha],
                "panchadha_score": PANCHADHA_SCORE[panchadha],
            }
        per_planet[planet] = {
            "naisargika_source_tier": NATURAL_RELATIONSHIP_SOURCE_TIER.get(planet, "unknown"),
            "relationships": relationships,
        }
    return {"model": "classical_graha_maitri_panchadha", "planets": per_planet}
