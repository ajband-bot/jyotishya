"""Bhāvapada family (A1-A12) + Graha Arūḍha calculator (build_plan.md
Phase 4: "Bhavapada family (A1-A12 + graha arudhas) calculator").

This is a GENERALIZATION, not new astrology math: `app.derived.factors
.arudha_pada()` already correctly implements the classical Arūḍha distance
formula (with the 1st/7th-from-source exception) for exactly two special
cases -- `lagna_pada()` (A1) and `upapada_lagna()` (A12). Both the Bhāva
Arūḍha family (A2-A11, the houses not already covered) and the Graha
Arūḍha family (one per classical planet) use the IDENTICAL algorithm --
only the "source" changes (a house's sign vs. a planet's own occupied
sign, which in this codebase's whole-sign-house system are the same
lookup). Reusing `arudha_pada()` directly keeps this DRY: zero new
distance-counting logic, just correct naming/aliasing.

Jaimini terminology note: the 12th house's Arūḍha is classically named
"Upapada" (UL), not "A12" -- already reflected in
`app.derived.factors.upapada_lagna()`'s own docstring and preserved here
via the `aliases` field rather than silently renamed.
"""
from __future__ import annotations

from typing import Any

from app.derived.factors import arudha_pada

CLASSICAL_7 = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]


def bhava_arudha_family(lagna_sign: int, chart: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """A1 (Aru\u1e0dha Lagna) through A12 (Upapada Lagna) -- one Aru\u1e0dha per house."""
    return {f"A{house}": arudha_pada(lagna_sign, chart, house) for house in range(1, 13)}


def graha_arudha_family(lagna_sign: int, chart: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """One Aru\u1e0dha (Graha Pada) per classical planet, computed from the
    planet's own occupied house exactly like a Bh\u0101va Aru\u1e0dha is computed
    from a house's sign -- same formula, different source."""
    return {planet: arudha_pada(lagna_sign, chart, chart[planet]["house"]) for planet in CLASSICAL_7 if planet in chart}


def bhavapada_report(lagna_sign: int, chart: dict[str, Any]) -> dict[str, Any]:
    return {
        "bhava_arudhas": bhava_arudha_family(lagna_sign, chart),
        "graha_arudhas": graha_arudha_family(lagna_sign, chart),
        "aliases": {"AL": "A1", "UL": "A12"},
        "citation": (
            "Jaimini Aru\u1e0dha doctrine (BPHS/Jaimini S\u016btras) -- generalizes the distance-counting formula "
            "already verified in app.derived.factors.arudha_pada (used there for AL/A1 and UL/A12) to the full "
            "A1-A12 Bh\u0101va Aru\u1e0dha family and the 7-planet Graha Aru\u1e0dha family."
        ),
    }
