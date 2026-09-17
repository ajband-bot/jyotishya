"""Chart Lab v2 -- time-aware layer on top of the birth-data-free sandbox
(app/derived/sandbox.py): Vimsottari Dasha (Sprint 2) and Transit overlay
(Sprint 3).

Design constraint (AGENTS.md Cardinal Rule 2 -- never fabricate): a sandbox
chart has no real birth timestamp, so there is no "real" dasha to compute.
What we CAN honestly compute is a genuine what-if simulation: "if the Moon
sat at this sign+degree and the native were born on this date, here is the
real Vimsottari chain that BPHS Ch.46 produces" -- same engine, same math,
as any real chart, just fed a hypothetical Moon position and birth date the
user explicitly chose. If no birth date is supplied at all, we refuse to
invent one and tell the frontend to fall back to manual MD/AD/PD selection
instead (spec section 17-18).

Transits need no birth data at all -- they are real Swiss Ephemeris
positions for a real calendar date, valid for any hypothetical Lagna.
"""
from __future__ import annotations

from datetime import date
from typing import Any

from pydantic import BaseModel, Field

from app.astro.dashas import compute_dashas, current_dasha_antar
from app.astro.engine import planet_state
from app.astro.transits import transit_chart
from app.derived.factors import planet_aspects


class SandboxDashaRequest(BaseModel):
    moon_sign: int = Field(ge=1, le=12)
    moon_degree: float = Field(default=15.0, ge=0.0, lt=30.0)
    birth_date: date | None = None
    as_of_date: date | None = None


class NatalPointer(BaseModel):
    sign: int = Field(ge=1, le=12)
    degree: float = Field(default=15.0, ge=0.0, lt=30.0)


class SandboxTransitRequest(BaseModel):
    on_date: date
    lagna_sign: int = Field(ge=1, le=12)
    moon_sign: int = Field(ge=1, le=12)
    natal_planets: dict[str, NatalPointer] = Field(default_factory=dict)


CONJUNCTION_ORB_DEG = 10.0


def _sign_lon(sign: int, degree: float) -> float:
    return (sign - 1) * 30.0 + degree


def sandbox_dasha(req: SandboxDashaRequest) -> dict[str, Any]:
    """Vimsottari Mahadasha chain + current MD/AD/PD for a hypothetical
    Moon position, ONLY if a birth date was supplied. Returns
    mode='manual_required' (no dates, no fabricated chain) otherwise."""
    if req.birth_date is None:
        return {
            "mode": "manual_required",
            "reason": "No birth date supplied -- pick MD/AD/PD manually instead of a fabricated calendar.",
        }

    moon_sid = _sign_lon(req.moon_sign, req.moon_degree)
    mahadashas = compute_dashas(req.birth_date, moon_sid)
    as_of = req.as_of_date or date.today()
    current = current_dasha_antar(mahadashas, as_of)

    return {
        "mode": "computed",
        "birth_date": req.birth_date.isoformat(),
        "as_of_date": as_of.isoformat(),
        "mahadashas": mahadashas,
        "current": current,
        "data_gap": "Moon position is your hypothetical sign+degree input, not a real birth measurement -- "
        "this is a valid what-if simulation of the real BPHS Ch.46 formula, not a real person's dasha.",
    }


def sandbox_transits(req: SandboxTransitRequest) -> dict[str, Any]:
    """Real sidereal transit positions for any calendar date -- needs no
    birth data, valid against any hypothetical Lagna/Moon the user has
    built. House-from-Lagna, house-from-Moon, dignity, and aspects are all
    computed here (never in the frontend) with the SAME functions natal
    charts use (app.astro.engine.planet_state, app.derived.factors.
    planet_aspects) -- so a transit and a natal placement can never drift
    out of sync in their house-counting convention.

    Sprint 4 (spec sections 8-9): if natal_planets is supplied, each
    transit planet also gets a natal_contacts list -- exact-degree
    conjunctions (same sign, within CONJUNCTION_ORB_DEG) and sign-based
    aspects onto natal planets, so the frontend can highlight both
    endpoints of a real transit->natal hit instead of guessing."""
    positions = transit_chart(req.on_date)
    natal_houses = {
        name: {
            "sign": ptr.sign,
            "degree": ptr.degree,
            "house": ((ptr.sign - req.lagna_sign) % 12) + 1,
        }
        for name, ptr in req.natal_planets.items()
    }

    planets: dict[str, Any] = {}
    for name, pos in positions.items():
        sign = pos["sign"]
        house_from_lagna = ((sign - req.lagna_sign) % 12) + 1
        house_from_moon = ((sign - req.moon_sign) % 12) + 1
        aspects_houses = planet_aspects(name, house_from_lagna)

        natal_contacts: list[dict[str, Any]] = []
        for natal_name, natal_pos in natal_houses.items():
            if natal_pos["sign"] == sign:
                orb = round(abs(pos["deg_in_sign"] - natal_pos["degree"]), 2)
                if orb <= CONJUNCTION_ORB_DEG:
                    natal_contacts.append(
                        {"natal_planet": natal_name, "kind": "conjunction", "house": natal_pos["house"], "orb_deg": orb}
                    )
            elif natal_pos["house"] in aspects_houses:
                natal_contacts.append(
                    {"natal_planet": natal_name, "kind": "aspect", "house": natal_pos["house"], "orb_deg": None}
                )

        entry = {
            **pos,
            "house_from_lagna": house_from_lagna,
            "house_from_moon": house_from_moon,
            "aspects_houses": aspects_houses,
            "natal_contacts": natal_contacts,
        }
        if name not in ("Rahu", "Ketu"):
            entry["dignity"] = planet_state(name, sign)
        planets[name] = entry
    return {"date": req.on_date.isoformat(), "planets": planets}
