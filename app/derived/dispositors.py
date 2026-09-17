"""First-class dispositor-chain engine (build_plan.md Phase 2 item 4).

A "dispositor" is simply the lord of the sign a planet occupies (BPHS
Ch.4's sign-lordship table, applied iteratively). Following a planet's
dispositor, then that lord's own dispositor, and so on, is a standard
Parashari technique for tracing a factor back to its ultimate source of
strength (most commonly applied to the Atmakaraka's dispositor in Jaimini
work, but the underlying mechanism is generic and reusable for any
planet/karaka). Before this module the codebase only ever looked one hop
deep (e.g. `app.derived.factors.arudha_pada`'s single lord lookup) -- this
is the first place the FULL chain is walked and terminated correctly.

A chain terminates one of two ways:
  - `self_disposed`  -- the chain reaches a planet sitting in its own sign
                        (BPHS calls this planet's placement "swakshetra";
                        it cannot be disposited further).
  - `cycle`           -- the chain loops back onto a planet already seen.
                        A 2-member cycle is a MUTUAL RECEPTION (each planet
                        sits in the other's sign) -- exposed here as raw
                        structural evidence only. This is deliberately NOT
                        asserted to be the formal Parivartana Yoga (that
                        classification, with its own strength/type rules,
                        is build_plan.md's YL-001, scheduled for Phase 4) --
                        Cardinal Rule 3 forbids quietly promoting a raw
                        structural fact into a named yoga verdict.

VARGA-AWARE: takes a plain chart-shaped `{planet: {"sign": n}}` mapping, so
it runs unmodified on D1 or any `compute_varga()` output (which stores sign
under the same key).
"""
from __future__ import annotations

from typing import Any

from app.astro.constants import PLANET_STATES, SIGNS

ALL_PLANETS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
CLASSICAL_7 = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]

MAX_CHAIN_DEPTH = 12  # 9 planets max distinct nodes; generous safety margin


def sign_lord(sign_no: int) -> str:
    return SIGNS[sign_no - 1]["lord"]


def dispositor_of(chart: dict[str, Any], planet: str) -> str:
    return sign_lord(chart[planet]["sign"])


def is_self_disposed(chart: dict[str, Any], planet: str) -> bool:
    return dispositor_of(chart, planet) == planet


def dispositor_chain(chart: dict[str, Any], start_planet: str) -> dict[str, Any]:
    chain = [start_planet]
    visited = {start_planet}
    current = start_planet

    while len(chain) <= MAX_CHAIN_DEPTH:
        lord = dispositor_of(chart, current)
        if lord == current:
            return {"chain": chain, "terminal": "self_disposed", "final_dispositor": current, "cycle": None}
        if lord in visited:
            chain.append(lord)
            cycle_members = chain[chain.index(lord):]
            return {
                "chain": chain,
                "terminal": "cycle",
                "final_dispositor": None,
                "cycle": cycle_members,
                "is_mutual_reception": len(set(cycle_members)) == 2,
            }
        chain.append(lord)
        visited.add(lord)
        current = lord

    return {"chain": chain, "terminal": "max_depth_exceeded", "final_dispositor": None, "cycle": None}


def all_dispositor_chains(chart: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {planet: dispositor_chain(chart, planet) for planet in ALL_PLANETS if planet in chart}


def detect_mutual_receptions(chart: dict[str, Any]) -> list[dict[str, Any]]:
    """Direct pairwise check (not chain-walking) that two CLASSICAL planets
    each sit in a sign owned by the other -- the raw structural condition
    for mutual reception. Rahu/Ketu excluded (they own no signs, per BPHS
    Ch.4, so cannot participate)."""
    pairs = []
    for i, planet_a in enumerate(CLASSICAL_7):
        if planet_a not in chart:
            continue
        for planet_b in CLASSICAL_7[i + 1:]:
            if planet_b not in chart:
                continue
            a_in_b_sign = chart[planet_a]["sign"] in PLANET_STATES[planet_b]["own"]
            b_in_a_sign = chart[planet_b]["sign"] in PLANET_STATES[planet_a]["own"]
            if a_in_b_sign and b_in_a_sign:
                pairs.append({"planets": [planet_a, planet_b], "citation": "BPHS Ch.4 own-sign table, pairwise cross-check"})
    return pairs


def dispositor_report(chart: dict[str, Any]) -> dict[str, Any]:
    return {
        "chains": all_dispositor_chains(chart),
        "mutual_receptions": detect_mutual_receptions(chart),
        "citation": "BPHS Ch.4 sign-lordship table, applied iteratively (standard Parashari dispositor-chain technique)",
    }
