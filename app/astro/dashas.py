"""Vimshottari Dasha Engine — BPHS Ch.46.
Moon's nakshatra at birth determines starting dasha.
"""
from __future__ import annotations
import math
from datetime import date, timedelta
from typing import List, Dict
from app.astro.constants import DASHA_YEARS, DASHA_ORDER, NAKSHATRAS, TOTAL_DASHA_YEARS

DAYS_PER_YEAR = 365.25


def _nakshatra_lord(moon_sid: float) -> str:
    """Return dasha lord from Moon's sidereal longitude."""
    idx = int(moon_sid / (360 / 27)) % 27
    return NAKSHATRAS[idx]["lord"]


def _elapsed_fraction(moon_sid: float) -> float:
    """Fraction of current nakshatra already elapsed (0.0 – 1.0)."""
    nak_size = 360.0 / 27.0
    pos_in_nak = moon_sid % nak_size
    return pos_in_nak / nak_size


def compute_dashas(birth_date: date, moon_sid: float, years: int = 120) -> List[Dict]:
    """Return list of major dasha periods from birth for `years` years.

    Boundary dates are derived from a single CUMULATIVE elapsed-days
    counter, rounded exactly once per boundary -- not by repeatedly
    truncating (`int()`) each period's own day-count and stacking the
    truncated pieces. The old stacked-truncation approach silently lost
    up to ~1 day per period, and those losses compounded across every
    level (Mahadasha -> Antardasha -> Pratyantardasha), producing a
    multi-day drift in "what dasha is active on date X" answers for
    charts many decades past birth. Found 2026-09-16 when a user reported
    their live current pratyantardasha didn't match this engine's output;
    this fix makes every period's end boundary land exactly on its
    parent's boundary at the end of a full cycle (previously it fell
    short by several days) -- see docs/dasha-precision-fix.md.
    """
    starting_lord = _nakshatra_lord(moon_sid)
    elapsed_frac = _elapsed_fraction(moon_sid)

    start_idx = DASHA_ORDER.index(starting_lord)
    first_dasha_years = DASHA_YEARS[starting_lord]
    remaining_years = first_dasha_years * (1.0 - elapsed_frac)

    dashas: List[Dict] = []
    elapsed_days = 0.0
    total_covered = 0.0

    for i in range(10):  # up to 10 cycles covers 1200 years
        idx = (start_idx + i) % 9
        planet = DASHA_ORDER[idx]
        yrs = remaining_years if i == 0 else DASHA_YEARS[planet]

        start_date = birth_date + timedelta(days=round(elapsed_days))
        elapsed_days += yrs * DAYS_PER_YEAR
        end_date = birth_date + timedelta(days=round(elapsed_days))
        dashas.append({
            "planet": planet,
            "years": round(yrs, 2),
            "start": start_date.isoformat(),
            "end": end_date.isoformat(),
        })
        total_covered += yrs
        if total_covered >= years:
            break

    return dashas


def compute_antardashas(mahadasha: Dict) -> List[Dict]:
    """Compute antardashas (sub-periods) for a given mahadasha. See
    compute_dashas()'s docstring for why this uses a single cumulative
    elapsed-days counter instead of stacked per-period truncation."""
    maha_planet = mahadasha["planet"]
    maha_years = DASHA_YEARS[maha_planet]  # full dasha years
    start_d = date.fromisoformat(mahadasha["start"])

    idx = DASHA_ORDER.index(maha_planet)
    antars = []
    elapsed_days = 0.0
    for i in range(9):
        sub_planet = DASHA_ORDER[(idx + i) % 9]
        sub_yrs = (DASHA_YEARS[sub_planet] / TOTAL_DASHA_YEARS) * maha_years
        start_d_i = start_d + timedelta(days=round(elapsed_days))
        elapsed_days += sub_yrs * DAYS_PER_YEAR
        end_d = start_d + timedelta(days=round(elapsed_days))
        antars.append({
            "planet": sub_planet,
            "years": round(sub_yrs, 3),
            "start": start_d_i.isoformat(),
            "end": end_d.isoformat(),
        })
    return antars


def compute_pratyantaradashas(mahadasha: Dict, antardasha: Dict) -> List[Dict]:
    """Compute pratyantardashas (sub-sub periods) for a given antardasha.

    Formula:
      PD_duration = (PD_lord_years / 120) * AD_duration_years
    Sequence starts from the AD lord itself. Same cumulative-elapsed-days
    fix as compute_dashas()/compute_antardashas() -- see their docstrings.
    """
    ad_planet = antardasha["planet"]
    ad_years = antardasha["years"]
    start_d = date.fromisoformat(antardasha["start"])

    idx = DASHA_ORDER.index(ad_planet)
    pratyas = []
    elapsed_days = 0.0
    for i in range(9):
        sub_planet = DASHA_ORDER[(idx + i) % 9]
        sub_yrs = (DASHA_YEARS[sub_planet] / TOTAL_DASHA_YEARS) * ad_years
        start_d_i = start_d + timedelta(days=round(elapsed_days))
        elapsed_days += sub_yrs * DAYS_PER_YEAR
        end_d = start_d + timedelta(days=round(elapsed_days))
        pratyas.append({
            "planet": sub_planet,
            "years": round(sub_yrs, 4),
            "start": start_d_i.isoformat(),
            "end": end_d.isoformat(),
        })
    return pratyas


def current_dasha_antar(dashas: List[Dict], today: date = None) -> Dict:
    """Find which mahadasha and antardasha is currently running."""
    if today is None:
        today = date.today()
    today_str = today.isoformat()

    active_maha = None
    for d in dashas:
        if d["start"] <= today_str <= d["end"]:
            active_maha = d
            break
    if not active_maha:
        return {}

    antars = compute_antardashas(active_maha)
    active_antar = None
    for a in antars:
        if a["start"] <= today_str <= a["end"]:
            active_antar = a
            break

    pratyas = compute_pratyantaradashas(active_maha, active_antar) if active_antar else []
    active_pratya = None
    for p in pratyas:
        if p["start"] <= today_str <= p["end"]:
            active_pratya = p
            break

    return {
        "mahadasha": active_maha,
        "antardasha": active_antar,
        "pratyantardasha": active_pratya,
        "all_antars": antars,
        "all_pratyantaras": pratyas,
    }
