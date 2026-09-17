"""Vedic Astronomical Engine — powered by Swiss Ephemeris (pyswisseph).

Accuracy: arc-second precision for all planets and Lagna.
Lahiri (Chitrapaksha) ayanamsa via SIDM_LAHIRI — same as JHora / Jagannatha Hora.
"""
from __future__ import annotations
import math
from typing import Dict

import swisseph as swe

# Lahiri ayanamsa — set once at module load
swe.set_sid_mode(swe.SIDM_LAHIRI)

# Swiss Ephemeris planet IDs → our names (7 classical grahas -- node handled
# separately below since it's the one graha whose *identity* is a config
# choice, not a fixed body).
_SWE_PLANETS = [
    (swe.SUN,       "Sun"),
    (swe.MOON,      "Moon"),
    (swe.MARS,      "Mars"),
    (swe.MERCURY,   "Mercury"),
    (swe.JUPITER,   "Jupiter"),
    (swe.VENUS,     "Venus"),
    (swe.SATURN,    "Saturn"),
]

# node_type config knob (build_plan.md Phase 1 item; docs/public-repo-review/
# 03-validation-cross-checks.md Check 1 originally flagged this as a real gap
# -- PyJHora's true-node default vs. our then-hardcoded mean-node explained a
# genuine ~21' Rahu/Ketu discrepancy against Ajay Kumar's chart). Explicit
# parameter, no global side effect -- per AD-"never silently default" style
# convention already used for ayanamsha/house_system in data/charts/*.yaml.
_NODE_SWE_IDS = {"mean": swe.MEAN_NODE, "true": swe.TRUE_NODE}


def _resolve_node_id(node_type: str) -> int:
    try:
        return _NODE_SWE_IDS[node_type]
    except KeyError:
        raise ValueError(
            f"Unsupported node_type: {node_type!r}. Supported: {sorted(_NODE_SWE_IDS)}"
        )

_FLAGS_SID_SPD = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED


# ── Julian Day (UT) ────────────────────────────────────────────────────────
def julian_day(year: int, month: int, day: int,
               hour: float = 0.0, utc_offset: float = 5.5) -> float:
    """Return Julian Day Number in Universal Time.
    hour is local time (decimal).  utc_offset in hours (e.g. 5.5 for IST).
    """
    ut = hour - utc_offset
    # roll back one calendar day if UT goes negative (e.g. 04:15 IST → 22:45 prev day UT)
    if ut < 0:
        day -= 1
        ut += 24.0
    return swe.julday(year, month, day, ut)


# ── Lahiri Ayanamsa ────────────────────────────────────────────────────────
def lahiri_ayanamsa(jd: float) -> float:
    """Lahiri ayanamsa in decimal degrees for a given Julian Day (UT)."""
    return swe.get_ayanamsa(jd)


# ── Helpers ────────────────────────────────────────────────────────────────
def _norm(deg: float) -> float:
    return deg % 360.0


# ── All Planets + Lagna in Sidereal (Vedic) ───────────────────────────────
def all_planets_sidereal(jd: float, lat: float, lon: float, node_type: str = "mean") -> Dict[str, Dict]:
    """Compute all grahas + Lagna in sidereal longitude.

    Args:
      node_type: "mean" (default, matches every existing chart fixture and
        this engine's historical behavior) or "true". Threaded explicitly
        per call -- never a module-level global -- so mixing mean-node and
        true-node charts in the same process is always safe and intentional,
        never accidental.

    Returns a dict keyed by planet name, each value containing:
      longitude     – sidereal longitude 0-360°
      sign          – rashi number 1-12
      deg_in_sign   – degrees within the sign (0-30°)
      house         – whole-sign house from Lagna (1-12)
      retrograde    – True if planet is retrograde
      speed         – daily motion in degrees (negative = retrograde)
    """
    node_id = _resolve_node_id(node_type)
    ayan = swe.get_ayanamsa(jd)

    # Lagna (Ascendant) — sidereal via houses_ex with FLG_SIDEREAL
    _, ascmc = swe.houses_ex(jd, lat, lon, b'P', swe.FLG_SIDEREAL)
    asc_sid   = _norm(ascmc[0])
    lagna_sign = int(asc_sid / 30) + 1

    result: Dict[str, Dict] = {}

    # All planets (7 classical + the configured node, computed identically)
    for pid, name in _SWE_PLANETS + [(node_id, "Rahu")]:
        pos, _ = swe.calc_ut(jd, pid, _FLAGS_SID_SPD)
        sid_lon = _norm(pos[0])
        speed   = pos[3]          # deg/day; negative = retrograde
        sign    = int(sid_lon / 30) + 1
        deg_in  = sid_lon % 30
        house   = ((sign - lagna_sign) % 12) + 1
        result[name] = {
            "longitude":   round(sid_lon, 4),
            "sign":        sign,
            "deg_in_sign": round(deg_in, 4),
            "house":       house,
            "retrograde":  speed < 0,
            "speed":       round(speed, 6),
        }

    # Ketu = Rahu + 180° (always retrograde)
    rahu_lon  = result["Rahu"]["longitude"]
    ketu_lon  = _norm(rahu_lon + 180.0)
    ketu_sign = int(ketu_lon / 30) + 1
    result["Ketu"] = {
        "longitude":   round(ketu_lon, 4),
        "sign":        ketu_sign,
        "deg_in_sign": round(ketu_lon % 30, 4),
        "house":       ((ketu_sign - lagna_sign) % 12) + 1,
        "retrograde":  True,
        "speed":       result["Rahu"]["speed"],
    }

    # Lagna entry
    result["Lagna"] = {
        "longitude":   round(asc_sid, 4),
        "sign":        lagna_sign,
        "deg_in_sign": round(asc_sid % 30, 4),
        "house":       1,
        "retrograde":  False,
        "speed":       0.0,
    }

    result["_ayanamsa"] = round(ayan, 6)
    return result


# ── Nakshatra from sidereal longitude ─────────────────────────────────────
def get_nakshatra(sid_lon: float) -> Dict:
    """Return nakshatra name, pada (1-4), and lord for a sidereal longitude."""
    from app.astro.constants import NAKSHATRAS
    idx  = int(sid_lon / (360 / 27)) % 27
    nak  = NAKSHATRAS[idx]
    pada = int((sid_lon % (360 / 27)) / (360 / 108)) + 1
    return {"nakshatra": nak, "pada": pada}


# ── Planet state: exalted / debilitated / own / neutral ───────────────────
def planet_state(planet: str, sign: int) -> str:
    from app.astro.constants import PLANET_STATES
    if planet not in PLANET_STATES:
        return "neutral"
    ps = PLANET_STATES[planet]
    if sign == ps["exalt"]:  return "exalted"
    if sign == ps["debil"]:  return "debilitated"
    if sign in ps["own"]:    return "own-sign"
    return "neutral"


# ── Navamsha (D9) ────────────────────────────────────────────────────────────
# Universal formula (BPHS Ch.6):
#   Each of the 12 signs has 9 navamsha padas of exactly 3°20' (= 10/3 degrees).
#   D9 sign (1-based) = floor(sidereal_lon ÷ (10/3)) % 12 + 1
#
# Cross-check via element-based starting signs (both must agree):
#   Fire signs  (1,5,9)   → D9 sequence starts from Aries   (sign 1)
#   Earth signs (2,6,10)  → D9 sequence starts from Capricorn (sign 10)
#   Air signs   (3,7,11)  → D9 sequence starts from Libra   (sign 7)
#   Water signs (4,8,12)  → D9 sequence starts from Cancer  (sign 4)

_D9_ELEMENT_START = {
    "Fire":  1,   # Aries
    "Earth": 10,  # Capricorn
    "Air":   7,   # Libra
    "Water": 4,   # Cancer
}


def navamsha_sign(sid_lon: float) -> int:
    """Return D9 rashi number (1-12) for a sidereal longitude.

    Primary formula  : floor(lon / 3.3333...) % 12  → 0-indexed → +1
    Equivalent check : element-based pada start (both must yield same result).
    """
    idx = int(sid_lon / (10.0 / 3.0)) % 12   # 0-indexed (0 = Aries)
    return idx + 1                             # 1-based rashi


_JAIMINI_PLANETS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]


def darakaraka(d1_chart: Dict) -> str:
    """Return the Darakaraka (DK) — Jaimini's spouse indicator.

    Rule: among the 7 classical planets (Sun–Saturn, nodes excluded),
    the planet with the LOWEST degree within its sign is the DK.
    """
    lowest_deg, dk = 30.0, ""
    for name in _JAIMINI_PLANETS:
        deg = d1_chart.get(name, {}).get("deg_in_sign", 30.0)
        if deg < lowest_deg:
            lowest_deg, dk = deg, name
    return dk


def navamsha_d9(d1_chart: Dict) -> Dict:
    """Compute the full Navamsha (D9) chart from a D1 sidereal chart dict.

    Returns:
      lagna_sign     – D9 Lagna rashi number (1-12)
      lagna_sign_en  – English name of D9 Lagna sign
      lagna_sign_tel – Telugu name of D9 Lagna sign
      planets        – {planet → {sign, deg_in_sign, house, state,
                                   sign_en, sign_tel, sign_lord, retrograde}}
      darakaraka     – name of DK planet
      dk_d9_sign     – D9 sign number of DK
      dk_d9_sign_en  – English name of DK's D9 sign
      dk_d9_state    – dignity of DK in its D9 sign (exalted/own-sign/…)
      dk_d9_house    – D9 house of DK (from D9 Lagna)
    """
    from app.astro.constants import SIGNS, PLANET_STATES

    def _d9_state(planet: str, sign: int) -> str:
        ps = PLANET_STATES.get(planet, {})
        if sign == ps.get("exalt"):       return "exalted"
        if sign == ps.get("debil"):       return "debilitated"
        if sign in ps.get("own", []):     return "own-sign"
        return "neutral"

    # D9 Lagna
    d9_lagna_sign = navamsha_sign(d1_chart["Lagna"]["longitude"])
    d9_lagna_info = SIGNS[d9_lagna_sign - 1]

    _all_names = ["Sun", "Moon", "Mars", "Mercury",
                  "Jupiter", "Venus", "Saturn", "Rahu", "Ketu", "Lagna"]
    planets_d9: Dict[str, Dict] = {}
    for name in _all_names:
        p = d1_chart.get(name)
        if not p:
            continue
        lon       = p["longitude"]
        d9_sign   = navamsha_sign(lon)
        # Degree within the D9 sign: position inside the 3°20' pada, scaled to 0-30°
        lon_in_pada    = lon % (10.0 / 3.0)
        d9_deg_in_sign = round(lon_in_pada * 9.0, 4)   # 9 navamshas per sign
        d9_house       = ((d9_sign - d9_lagna_sign) % 12) + 1
        si             = SIGNS[d9_sign - 1]
        planets_d9[name] = {
            "sign":        d9_sign,
            "deg_in_sign": d9_deg_in_sign,
            "house":       d9_house,
            "state":       _d9_state(name, d9_sign),
            "sign_en":     si["en"],
            "sign_tel":    si["name"],
            "sign_lord":   si["lord"],
            "retrograde":  p.get("retrograde", False),
        }

    dk          = darakaraka(d1_chart)
    dk_d9       = planets_d9.get(dk, {})

    return {
        "lagna_sign":     d9_lagna_sign,
        "lagna_sign_en":  d9_lagna_info["en"],
        "lagna_sign_tel": d9_lagna_info["name"],
        "planets":        planets_d9,
        "darakaraka":     dk,
        "dk_d9_sign":     dk_d9.get("sign"),
        "dk_d9_sign_en":  dk_d9.get("sign_en"),
        "dk_d9_state":    dk_d9.get("state"),
        "dk_d9_house":    dk_d9.get("house"),
    }


# ── Combustion check ─────────────────────────────────────────────────────────
COMBUST_ORBS = {
    "Moon": 12.0, "Mars": 17.0, "Mercury": 14.0,
    "Jupiter": 11.0, "Venus": 10.0, "Saturn": 15.0,
}

def is_combust(planet: str, planet_lon: float, sun_lon: float) -> bool:
    """True if planet is within combustion orb of Sun (sidereal longitudes)."""
    orb = COMBUST_ORBS.get(planet)
    if orb is None:
        return False
    diff = abs(planet_lon - sun_lon) % 360
    if diff > 180:
        diff = 360 - diff
    return diff <= orb
