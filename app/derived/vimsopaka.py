"""Vimsopaka Bala -- classical 20-point divisional-chart strength (BPHS
Ch.6), build_plan.md Phase 5 ("Vimsopaka Bala (needs Phase 1 vargas
engine)").

Four classical schemes, differing only in WHICH vargas are weighted and
by how much -- weight tables are fixed classical data (BPHS Ch.6), cross-
checked here (AD-4, data-only comparison, no code imported) against
PyJHora's `const.py` (`shadvarga_amsa_vimsopaka`, `sapthavarga_amsa_
vimsopaka`, `dhasavarga_amsa_vimsopaka`, `shodhasa_varga_amsa_vimsopaka`)
-- all four schemes' weights sum to exactly 20, confirmed by hand and by
`_ASSERT_SCHEMES_SUM_TO_20()` at import time.

Per-varga scoring (how much of that varga's weight a planet actually
earns) is a straight DRY reuse of already-built, already-Phase-1-verified
machinery -- no new dignity logic:
  - Own sign or exaltation in that varga -> full 20/20 of the varga's weight.
  - Otherwise -> the planet's PANCHADHA (5-fold compound) relationship,
    per app.derived.dignities.graha_maitri_report (already varga-aware by
    design), toward the LORD of the sign it occupies in that varga.
    Points per tier (Adhi Mitra=18, Mitra=15, Sama=10, Shatru=7, Adhi
    Shatru=5) cross-checked against PyJHora's own
    `vimsopaka_bala_scores = [5, 7, 10, 15, 18]` constant.

Rahu/Ketu are excluded, same disclosed data_gap precedent already
established for Ashtakavarga (app.derived.ashtakavarga) -- classical
Parashari Vimsopaka doctrine has no consistent own-sign/exaltation
convention for the lunar nodes across all divisional charts.
"""
from __future__ import annotations

from typing import Any

from app.astro.constants import PLANET_STATES, SIGNS
from app.astro.vargas import compute_varga
from app.derived.dignities import graha_maitri_report

CLASSICAL_7 = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]

VIMSOPAKA_SCHEMES: dict[str, dict[int, float]] = {
    "shadvarga": {1: 6, 2: 2, 3: 4, 9: 5, 12: 2, 30: 1},
    "saptavarga": {1: 5, 2: 2, 3: 3, 7: 1, 9: 2.5, 12: 4.5, 30: 2},
    "dasavarga": {1: 3, 2: 1.5, 3: 1.5, 7: 1.5, 9: 1.5, 10: 1.5, 12: 1.5, 16: 1.5, 30: 1.5, 60: 5},
    "shodasavarga": {
        1: 3.5, 2: 1, 3: 1, 4: 0.5, 7: 0.5, 9: 3, 10: 0.5, 12: 0.5, 16: 2,
        20: 0.5, 24: 0.5, 27: 0.5, 30: 1, 40: 0.5, 45: 0.5, 60: 4,
    },
}

PANCHADHA_VIMSOPAKA_POINTS = {"adhi_mitra": 18, "mitra": 15, "sama": 10, "shatru": 7, "adhi_shatru": 5}


def _assert_schemes_sum_to_20() -> None:
    for name, weights in VIMSOPAKA_SCHEMES.items():
        total = round(sum(weights.values()), 6)
        if total != 20:
            raise AssertionError(f"Vimsopaka scheme {name!r} weights sum to {total}, not 20")


_assert_schemes_sum_to_20()


def _sign_lord(sign: int) -> str:
    return SIGNS[sign - 1]["lord"]


def _is_own_or_exalted(planet: str, sign: int) -> bool:
    states = PLANET_STATES[planet]
    return sign in states["own"] or sign == states["exalt"]


def _dignity_points(planet: str, varga: dict[str, Any], varga_sign: int) -> int:
    """Points (out of 20) this planet earns from its dignity in ONE varga."""
    if _is_own_or_exalted(planet, varga_sign):
        return 20
    lord = _sign_lord(varga_sign)
    if lord == planet:
        return 20  # defensive: a planet can never actually be its own sign's lord and land here, since _is_own_or_exalted already caught it
    planet_houses = {p: varga["planets"][p]["house"] for p in CLASSICAL_7 if p in varga["planets"]}
    relationships = graha_maitri_report(planet_houses)["planets"][planet]["relationships"]
    tier = relationships[lord]["panchadha"]
    return PANCHADHA_VIMSOPAKA_POINTS[tier]


def _varga_contribution(planet: str, d1_chart: dict[str, Any], n: int, weight: float) -> dict[str, Any]:
    varga = compute_varga(d1_chart, n)
    varga_sign = varga["planets"][planet]["sign"]
    points = _dignity_points(planet, varga, varga_sign)
    contribution = weight * points / 20.0
    return {
        "weight": weight, "varga_sign": varga_sign, "varga_sign_en": varga["planets"][planet]["sign_en"],
        "dignity_points_of_20": points, "contribution": round(contribution, 4),
    }


def _verdict(total: float) -> str:
    """Standard 3-tier Uttama/Madhyama/Adhama banding used across most
    classical strength measures. Boundary numbers (15/10 of 20) are a
    widely-cited practical convention, not a specific BPHS verse --
    disclosed as pending_audit rather than claimed as a direct citation,
    per Cardinal Rule 5."""
    if total >= 15:
        return "uttama"
    if total >= 10:
        return "madhyama"
    return "adhama"


def vimsopaka_bala(d1_chart: dict[str, Any], scheme: str = "shadvarga") -> dict[str, Any]:
    if scheme not in VIMSOPAKA_SCHEMES:
        raise ValueError(f"Unknown Vimsopaka scheme {scheme!r}. Choices: {sorted(VIMSOPAKA_SCHEMES)}")
    weights = VIMSOPAKA_SCHEMES[scheme]

    planets: dict[str, Any] = {}
    for planet in CLASSICAL_7:
        breakdown: dict[str, Any] = {}
        total = 0.0
        for n, weight in weights.items():
            contribution = _varga_contribution(planet, d1_chart, n, weight)
            breakdown[f"D{n}"] = contribution
            total += contribution["contribution"]
        planets[planet] = {
            "total": round(total, 4), "max": 20.0,
            "verdict": _verdict(total), "verdict_citation_status": "pending_audit",
            "breakdown": breakdown,
        }

    for node in ("Rahu", "Ketu"):
        planets[node] = {
            "model": "data_gap",
            "reason": "Classical Parashari Vimsopaka Bala has no consistent own-sign/exaltation convention for the lunar nodes across all divisional charts.",
        }

    return {
        "scheme": scheme, "vargas_used": sorted(weights.keys()), "planets": planets,
        "citation": "BPHS Ch.6 Vimsopaka Bala; weight tables cross-checked (AD-4, data-only) against PyJHora const.py's amsa_vimsopaka tables; per-tier points cross-checked against PyJHora's vimsopaka_bala_scores constant",
    }


def all_schemes_vimsopaka_bala(d1_chart: dict[str, Any]) -> dict[str, Any]:
    """All 4 classical schemes at once, for a single-glance comparison --
    the same planet can rank differently depending on which varga set a
    scheme weights (a genuine classical nuance, not a bug)."""
    return {scheme: vimsopaka_bala(d1_chart, scheme) for scheme in VIMSOPAKA_SCHEMES}
