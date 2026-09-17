"""Classical Panchanga engine -- the five limbs (Pancha-Anga): Vara, Tithi,
Nakshatra, Yoga, Karana.

Formulas are standard Siddhantic degree-based math (Sun/Moon longitude
differences and sums divided into fixed classical arc-spans) -- unlike
Ashtakavarga's fixed bindu table, these are not large hand-transcribed data
tables, so the correctness risk here is in getting the boundary arithmetic
right, not in copying a big table. Per build_plan.md Phase 1 ("cross-check
against panchanga/drik.py"), the five limb definitions, name lists, and
index ranges below were verified against
`public-git-repos/PyJHora-main/src/jhora/panchanga/drik.py` (functions
`tithi`, `nakshatra`, `yogam`/`yogam_old`, `karana`, `vaara`) and its
`lang/list_values_en.txt` name tables (data only, per AD-4 -- no code
copied). Sanskrit tithi/yoga/karana names below use standard classical
spelling (matching BPHS/Sanskrit sources per AD-5) rather than that
library's Tamil-transliterated tithi variant, but the index ranges,
ordering, and arc-span formulas agree exactly.

Deliberately out of scope (flagged as `data_gap`, not silently assumed):
sunrise-to-sunrise "Vedic day" boundary for Vara/Tithi/Nakshatra/Yoga/
Karana transitions (needs a sunrise/sunset engine that doesn't exist yet).
This module reports civil-midnight-to-midnight Vara and instant-in-time
(at the queried moment, matching how the rest of this engine reports
planetary positions) values for the other four limbs -- both explicitly
labeled, never presented as sunrise-anchored classical Panchanga.
"""
from __future__ import annotations

from datetime import date
from typing import Any

from app.astro.constants import NAKSHATRAS
from app.astro.engine import get_nakshatra

ARC_PER_TITHI = 12.0
ARC_PER_YOGA = 360.0 / 27.0
ARC_PER_KARANA = 6.0

TITHI_NAMES = [
    "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami", "Shashthi",
    "Saptami", "Ashtami", "Navami", "Dashami", "Ekadashi", "Dwadashi",
    "Trayodashi", "Chaturdashi",
]

YOGA_NAMES = [
    "Vishkumbha", "Priti", "Ayushman", "Saubhagya", "Shobhana", "Atiganda",
    "Sukarma", "Dhriti", "Shoola", "Ganda", "Vriddhi", "Dhruva", "Vyaghata",
    "Harshana", "Vajra", "Siddhi", "Vyatipata", "Variyana", "Parigha",
    "Shiva", "Siddha", "Sadhya", "Shubha", "Shukla", "Brahma", "Indra",
    "Vaidhriti",
]
assert len(YOGA_NAMES) == 27

# The 7 "chara" (movable) karanas, repeating cyclically for karana indices
# 2-57 (8 full cycles of 7 = 56 slots); Kimstughna (index 1) and
# Shakuni/Chatushpada/Naga (indices 58-60) are "sthira" (fixed), occurring
# exactly once each per lunar month.
CHARA_KARANAS = ["Bava", "Balava", "Kaulava", "Taitila", "Gara", "Vanija", "Vishti"]
FIXED_KARANA_HEAD = "Kimstughna"
FIXED_KARANA_TAIL = ["Shakuni", "Chatushpada", "Naga"]

VARA_NAMES = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
VARA_LORDS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]


def _angular_diff(a: float, b: float) -> float:
    return (a - b) % 360.0


def compute_tithi(sun_lon: float, moon_lon: float) -> dict[str, Any]:
    """Tithi = 1/30th of the Moon-Sun angular separation. 1-15 waxing
    (Shukla Paksha), 16-30 waning (Krishna Paksha); 15th of each paksha is
    Purnima (full moon) / Amavasya (new moon) respectively, not a numbered
    name."""
    diff = _angular_diff(moon_lon, sun_lon)
    number = int(diff / ARC_PER_TITHI) + 1  # 1-30
    percentage_complete = round((diff % ARC_PER_TITHI) / ARC_PER_TITHI * 100, 2)
    if number <= 15:
        paksha = "Shukla"
        ordinal = number
    else:
        paksha = "Krishna"
        ordinal = number - 15
    if ordinal == 15:
        name = "Purnima" if paksha == "Shukla" else "Amavasya"
    else:
        name = TITHI_NAMES[ordinal - 1]
    return {
        "number": number,
        "paksha": paksha,
        "name": name,
        "percentage_complete": percentage_complete,
    }


def compute_nakshatra_limb(moon_lon: float) -> dict[str, Any]:
    """Wraps the already-verified `app.astro.engine.get_nakshatra` (used
    elsewhere for D9/karaka logic) so Panchanga exposes the same nakshatra
    computation everywhere in the engine, never a second implementation."""
    info = get_nakshatra(moon_lon)
    nak = info["nakshatra"]
    span = 360.0 / 27.0
    idx = NAKSHATRAS.index(nak)
    percentage_complete = round((moon_lon % span) / span * 100, 2)
    return {
        "number": idx + 1,
        "name": nak["en"],
        "lord": nak["lord"],
        "pada": info["pada"],
        "percentage_complete": percentage_complete,
    }


def compute_yoga(sun_lon: float, moon_lon: float) -> dict[str, Any]:
    """Nitya Yoga = 1/27th of (Sun longitude + Moon longitude)."""
    total = (sun_lon + moon_lon) % 360.0
    number = int(total / ARC_PER_YOGA) + 1  # 1-27
    percentage_complete = round((total % ARC_PER_YOGA) / ARC_PER_YOGA * 100, 2)
    return {
        "number": number,
        "name": YOGA_NAMES[number - 1],
        "percentage_complete": percentage_complete,
    }


def _karana_name(karana_index: int) -> str:
    if karana_index == 1:
        return FIXED_KARANA_HEAD
    if karana_index >= 58:
        return FIXED_KARANA_TAIL[karana_index - 58]
    return CHARA_KARANAS[(karana_index - 2) % 7]


def compute_karana(sun_lon: float, moon_lon: float) -> dict[str, Any]:
    """Karana = half-tithi, 1-60 across a lunar month; 11 distinct names
    (7 cyclic + Kimstughna + Shakuni/Chatushpada/Naga -- see module docstring)."""
    diff = _angular_diff(moon_lon, sun_lon)
    number = int(diff / ARC_PER_KARANA) + 1  # 1-60
    percentage_complete = round((diff % ARC_PER_KARANA) / ARC_PER_KARANA * 100, 2)
    return {
        "number": number,
        "name": _karana_name(number),
        "percentage_complete": percentage_complete,
    }


def compute_vara(local_date: date) -> dict[str, Any]:
    """Civil weekday (local midnight-to-midnight), NOT sunrise-anchored
    Vedic day -- see module docstring for why."""
    # date.weekday(): Monday=0 .. Sunday=6. Panchanga convention: Sunday=0.
    vara_index = (local_date.weekday() + 1) % 7
    return {
        "number": vara_index,
        "name": VARA_NAMES[vara_index],
        "lord": VARA_LORDS[vara_index],
        "day_boundary": "civil_midnight",
    }


def compute_panchanga(sun_lon: float, moon_lon: float, local_date: date) -> dict[str, Any]:
    """Full five-limbed Panchanga for a given Sun/Moon longitude pair and
    local calendar date. Each limb reports its own `day_boundary`/instant
    convention explicitly (see module docstring) rather than presenting a
    unified sunrise-anchored Panchanga this engine cannot yet compute."""
    return {
        "model": "computed_instant_not_sunrise_anchored",
        "vara": compute_vara(local_date),
        "tithi": compute_tithi(sun_lon, moon_lon),
        "nakshatra": compute_nakshatra_limb(moon_lon),
        "yoga": compute_yoga(sun_lon, moon_lon),
        "karana": compute_karana(sun_lon, moon_lon),
    }
