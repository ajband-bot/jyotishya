"""Chart Lab sandbox -- a hypothetical (non-birth-data) D1 chart built
purely from user-placed Lagna + planet sign/degree/retrograde inputs, for
the drag-and-drop "Chart Lab" teaching tool.

Design constraint (see AGENTS.md Cardinal Rule 2 -- never fabricate): this
module is explicit that it is NOT a real birth chart. Dashas, transits, and
Ashtakavarga/Argala (which need a real "today" or a real Moon-nakshatra
birth timestamp) are deliberately NOT computed here -- they would require
fabricating data the sandbox doesn't have. Everything this module DOES
compute (combustion, D9, dignity, doshas, yogas, aspects, Shadbala) is
computed from the exact same engine functions real charts use, fed
synthetic-but-internally-consistent longitudes derived from the user's
sign+degree placement. Ketu is never user-placed -- it is always exactly
180 degrees from Rahu, enforced here rather than trusted from input.
"""
from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

from app.astro.constants import SIGNS
from app.astro.engine import is_combust, navamsha_d9, planet_state
from app.derived.doshas import compute_all_doshas
from app.derived.factors import (
    house_lord,
    is_yoga_karaka,
    maraka_lords,
    planet_aspects,
)
from app.derived.reference_tables import (
    ALL_PLANETS,
    NATURAL_RELATIONSHIPS,
    _classify_cell,
    get_house_themes,
    house_connection_text,
)
from app.derived.strengths import simplified_ishta_kashta, simplified_shadbala_core, simplified_varga_quality
from app.knowledge.interpreter import detect_yogas

CLASSICAL_7 = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
PLACEABLE = CLASSICAL_7 + ["Rahu"]
ALL_9 = CLASSICAL_7 + ["Rahu", "Ketu"]


class PlanetPlacement(BaseModel):
    sign: int = Field(ge=1, le=12)
    degree: float = Field(default=15.0, ge=0.0, lt=30.0)
    retrograde: bool = False


class SandboxRequest(BaseModel):
    lagna_sign: int = Field(ge=1, le=12)
    lagna_degree: float = Field(default=15.0, ge=0.0, lt=30.0)
    planets: dict[str, PlanetPlacement]
    day_or_night: Literal["day", "night"] = "day"


def _sign_lon(sign: int, degree: float) -> float:
    return (sign - 1) * 30.0 + degree


def build_sandbox_chart(req: SandboxRequest) -> dict[str, Any]:
    """Synthesize a chart dict shaped exactly like all_planets_sidereal()'s
    output, from user sign/degree/retrograde placements. Ketu is forced to
    Rahu + 180 degrees regardless of what (if anything) was sent for it."""
    chart: dict[str, Any] = {}
    lagna_sign = req.lagna_sign

    for planet in PLACEABLE:
        placement = req.planets.get(planet)
        if placement is None:
            raise ValueError(f"Missing placement for {planet}")
        lon = _sign_lon(placement.sign, placement.degree)
        house = ((placement.sign - lagna_sign) % 12) + 1
        chart[planet] = {
            "longitude": round(lon, 4),
            "sign": placement.sign,
            "deg_in_sign": round(placement.degree, 4),
            "house": house,
            "retrograde": placement.retrograde,
            "speed": -0.5 if placement.retrograde else 0.5,
        }

    rahu = chart["Rahu"]
    ketu_sign = ((rahu["sign"] - 1 + 6) % 12) + 1
    ketu_lon = _sign_lon(ketu_sign, rahu["deg_in_sign"])
    chart["Ketu"] = {
        "longitude": round(ketu_lon, 4),
        "sign": ketu_sign,
        "deg_in_sign": rahu["deg_in_sign"],
        "house": ((ketu_sign - lagna_sign) % 12) + 1,
        "retrograde": True,
        "speed": -0.5,
    }

    chart["Lagna"] = {
        "longitude": round(_sign_lon(lagna_sign, req.lagna_degree), 4),
        "sign": lagna_sign,
        "deg_in_sign": req.lagna_degree,
        "house": 1,
        "retrograde": False,
        "speed": 0.0,
    }
    return chart


def _sign_relationship(planet: str, sign: int) -> str:
    sign_lord = SIGNS[sign - 1]["lord"]
    if sign_lord == planet:
        return "own_sign"
    rel = NATURAL_RELATIONSHIPS.get(planet, {})
    if sign_lord in rel.get("friends", []):
        return "friendly_territory"
    if sign_lord in rel.get("enemies", []):
        return "enemy_territory"
    return "neutral_territory"


def analyze_sandbox(req: SandboxRequest) -> dict[str, Any]:
    """The Chart Lab 'Key Observations' engine -- house lordships,
    functional nature, dignity, natural-relationship territory, doshas,
    yogas, aspects, and simplified-but-authentic Shadbala (real combustion
    and D9 via real synthesized longitudes, kala/chesta bala proxied via
    the day/night toggle and retrograde flag since there is no real birth
    time or motion data in a sandbox)."""
    chart = build_sandbox_chart(req)
    lagna_sign = req.lagna_sign

    d9_raw = navamsha_d9(chart)
    d9_planets = d9_raw["planets"]

    combustion = {}
    sun_lon = chart["Sun"]["longitude"]
    for planet in ["Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
        diff = min(abs(chart[planet]["longitude"] - sun_lon) % 360, 360 - (abs(chart[planet]["longitude"] - sun_lon) % 360))
        combustion[planet] = {"combust": is_combust(planet, chart[planet]["longitude"], sun_lon), "diff": round(diff, 4)}

    aspect_map = {planet: planet_aspects(planet, chart[planet]["house"]) for planet in ALL_9}
    hour_local = 12 if req.day_or_night == "day" else 0
    shadbala = simplified_shadbala_core(chart, d9_planets, combustion, aspect_map, hour_local)
    varga_quality = simplified_varga_quality({"chart": chart, "d9": d9_raw})
    ishta_kashta = simplified_ishta_kashta({"chart": chart, "d9": d9_raw, "combustion": combustion}, shadbala=shadbala)
    yoga_karakas = [p for p in CLASSICAL_7 if is_yoga_karaka(lagna_sign, p)]

    house_themes = get_house_themes()
    houses: dict[int, Any] = {}
    house_connections: dict[int, Any] = {}
    for house_no in range(1, 13):
        occupants = [p for p in ALL_9 if chart[p]["house"] == house_no]
        houses[house_no] = {
            "lord": house_lord(lagna_sign, house_no),
            "theme": house_themes[house_no],
            "occupants": occupants,
            "aspected_by": [p for p in ALL_9 if house_no in aspect_map[p]],
        }
        lord = house_lord(lagna_sign, house_no)
        lord_house = chart[lord]["house"]
        text = house_connection_text(house_no, lord_house, house_themes)
        house_connections[house_no] = {
            "lord": lord,
            "lord_house": lord_house,
            "connection": text["connection"],
            "dest_nature": text["dest_nature"],
            "is_self_placed": house_no == lord_house,
        }

    planets_out: dict[str, Any] = {}
    for planet in ALL_9:
        pos = chart[planet]
        entry: dict[str, Any] = {
            "sign": pos["sign"],
            "sign_en": SIGNS[pos["sign"] - 1]["en"],
            "degree": pos["deg_in_sign"],
            "house": pos["house"],
            "retrograde": pos["retrograde"],
            "dignity": planet_state(planet, pos["sign"]) if planet in CLASSICAL_7 else "n/a",
            "territory": _sign_relationship(planet, pos["sign"]) if planet in CLASSICAL_7 else "n/a",
            "d9_sign_en": SIGNS[d9_planets[planet]["sign"] - 1]["en"],
            "d9_state": d9_planets[planet]["state"],
            "vargottama": pos["sign"] == d9_planets[planet]["sign"],
            "aspects_houses": aspect_map[planet],
        }
        if planet in CLASSICAL_7:
            entry["functional"] = _classify_cell(lagna_sign, planet)
            entry["combust"] = combustion.get(planet, {}).get("combust", False)
            entry["shadbala"] = shadbala[planet]
            entry["varga_quality"] = varga_quality[planet]
            entry["ishta_kashta"] = ishta_kashta[planet]
        planets_out[planet] = entry

    doshas = compute_all_doshas({"chart": chart, "lagna_sign": lagna_sign, "aspect_map": aspect_map})
    yogas = detect_yogas(chart)

    return {
        "lagna_sign": lagna_sign,
        "lagna_sign_en": SIGNS[lagna_sign - 1]["en"],
        "houses": houses,
        "house_connections": house_connections,
        "planets": planets_out,
        "maraka_lords": maraka_lords(lagna_sign),
        "yoga_karakas": yoga_karakas,
        "doshas": doshas,
        "yogas": yogas,
        "data_gaps": [
            "Dashas: require a real birth Moon-nakshatra timestamp, not available in a hypothetical chart.",
            "Transit-based Ashtakavarga/Argala: require a real 'today', not applicable to a hypothetical chart.",
            "D9 Lagna sign is approximate (assumes Lagna at mid-sign unless you set the Lagna degree slider).",
            "Kala Bala uses your Day/Night toggle as a proxy for real birth-time strength; Chesta Bala uses the retrograde toggle as a proxy for real planetary speed.",
        ],
    }
