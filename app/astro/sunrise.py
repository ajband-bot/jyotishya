"""Sunrise/sunset primitive -- previously a documented gap
(app/astro/panchanga.py's own docstring: "needs a sunrise/sunset engine
that doesn't exist yet"). Built now because build_plan.md Phase 5's full
Shadbala requires it for three Kala Bala sub-components (Nathonnata,
Tribhaga, Hora) that are all defined relative to sunrise/sunset, not
clock midnight.

Uses Swiss Ephemeris's own `swe.BIT_HINDU_RISING` flag -- the library's
purpose-built classical-Hindu-rising convention (top-of-disc, refraction
included per traditional Panchanga practice), not generic astronomical
sunrise, so this stays consistent with every other classical calculation
in this codebase rather than importing a Western-convention definition.
"""
from __future__ import annotations

from datetime import date, timedelta
from typing import Any

import swisseph as swe

from app.astro.engine import julian_day

_FLAGS = swe.FLG_SWIEPH | swe.BIT_HINDU_RISING


def _rise_or_set(jd_ut_search_start: float, lat: float, lon: float, event: int) -> float:
    res, tret = swe.rise_trans(jd_ut_search_start, swe.SUN, event, (lon, lat, 0.0), flags=_FLAGS)
    if res != 0:
        raise ValueError(f"Sunrise/sunset event not found (circumpolar?) for lat={lat}, lon={lon}")
    return tret[0]


def sunrise_sunset_jd(on_date: date, lat: float, lon: float, utc_offset: float = 5.5) -> dict[str, float]:
    """Julian Day (UT) of sunrise and sunset for the LOCAL civil date
    `on_date` at the given place. Searches from local midnight (converted
    to UT) so the returned sunrise/sunset genuinely fall within that civil
    day, not an adjacent one."""
    local_midnight_jd_ut = julian_day(on_date.year, on_date.month, on_date.day, 0.0, utc_offset)
    sunrise_jd = _rise_or_set(local_midnight_jd_ut, lat, lon, swe.CALC_RISE)
    sunset_jd = _rise_or_set(sunrise_jd, lat, lon, swe.CALC_SET)
    return {"sunrise_jd_ut": sunrise_jd, "sunset_jd_ut": sunset_jd}


def previous_sunrise_jd(birth_jd_ut: float, lat: float, lon: float) -> float:
    """The most recent sunrise AT OR BEFORE the given instant -- the
    classical "sunrise to sunrise" day boundary used throughout Kala Bala
    (Nathonnata/Tribhaga/Hora are all measured from this, not clock
    midnight)."""
    candidate = _rise_or_set(birth_jd_ut - 1.5, lat, lon, swe.CALC_RISE)
    while True:
        nxt = _rise_or_set(candidate + 0.1, lat, lon, swe.CALC_RISE)
        if nxt > birth_jd_ut:
            return candidate
        candidate = nxt


def day_night_context(birth_jd_ut: float, lat: float, lon: float) -> dict[str, Any]:
    """Everything Kala Bala's sunrise-relative sub-components need for one
    birth instant: the bracketing sunrise/sunset/next-sunrise, whether
    birth fell in day or night, and how far through that day/night segment
    birth occurred (0.0 = right at the boundary start, 1.0 = right at the
    next boundary)."""
    sunrise = previous_sunrise_jd(birth_jd_ut, lat, lon)
    sunset = _rise_or_set(sunrise + 0.1, lat, lon, swe.CALC_SET)
    next_sunrise = _rise_or_set(sunset + 0.1, lat, lon, swe.CALC_RISE)

    is_day = sunrise <= birth_jd_ut < sunset
    if is_day:
        segment_start, segment_end = sunrise, sunset
    else:
        segment_start, segment_end = sunset, next_sunrise
    fraction = (birth_jd_ut - segment_start) / (segment_end - segment_start)

    return {
        "sunrise_jd_ut": sunrise, "sunset_jd_ut": sunset, "next_sunrise_jd_ut": next_sunrise,
        "is_day_birth": is_day,
        "segment_fraction_elapsed": fraction,
        "segment_duration_days": segment_end - segment_start,
    }
