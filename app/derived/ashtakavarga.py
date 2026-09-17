"""Ashtakavarga integration layer -- wires the classical BAV/SAV engine
(`app.astro.ashtakavarga`, pure data + math, no chart-narrative concerns)
to a specific natal chart plus its current transit snapshot.

Replaces a prior `practical_bindu_proxy` heuristic (a Shadbala-derived
approximation used before a classical calculator existed). Now that real
Sarvashtakavarga/Bhinnashtakavarga bindus are computable, transit
favorability is judged against the actual classical figures, not a proxy.
"""
from __future__ import annotations

from typing import Any

from app.astro.ashtakavarga import SEVEN_PLANETS, full_ashtakavarga


def classical_ashtakavarga(context: dict[str, Any]) -> dict[str, Any]:
    chart = context["chart"]
    transits = context["transits"]["transits"]

    result = full_ashtakavarga(chart)

    current_transits: dict[str, Any] = {}
    for planet in SEVEN_PLANETS:
        data = transits[planet]
        sign_no = data["sign"]
        sign_entry = result["signs"][sign_no]
        sav_bindus = sign_entry["sav_bindus"]
        pav_bindus = sign_entry["bav_by_planet"][planet]
        if sav_bindus >= 30 and pav_bindus >= 4:
            verdict = "favorable"
        elif sav_bindus < 25 or pav_bindus <= 3:
            verdict = "challenging"
        else:
            verdict = "mixed"
        current_transits[planet] = {
            "model": "classical_parashari",
            "transit_sign": data["sign_en"],
            "transit_house": sign_entry["house"],
            "sav_bindus": sav_bindus,
            "pav_bindus": pav_bindus,
            "verdict": verdict,
        }

    # Rahu/Ketu have no classical Parashari Ashtakavarga row (see
    # app.astro.ashtakavarga module docstring) -- report the gap explicitly
    # rather than borrowing another planet's bindus, per Cardinal Rule 4.
    for node in ("Rahu", "Ketu"):
        current_transits[node] = {
            "model": "data_gap",
            "reason": "Classical Parashari Ashtakavarga has no defined bindu row for lunar nodes.",
        }

    return {
        "model": result["model"],
        "signs": result["signs"],
        "bhinna": result["bhinna"],
        "sarva": result["sarva"],
        "sav_total": result["sav_total"],
        "current_transits": current_transits,
    }
