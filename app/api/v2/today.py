"""Chart-independent "today" reference API (Phase 8 follow-up): a generic
Panchanga and planetary Transits view that needs no birth chart at all --
distinct from the natal-chart-specific Panchanga/Transits tabs inside the
Chart Workbench, which show these same limbs/positions AT THE BIRTH MOMENT
or IN NATAL CONTEXT (house-from-Lagna, Sade Sati, etc.) for one person.

Both endpoints reuse `app.astro.transits.transit_chart()` (already
location-independent -- ecliptic longitude does not depend on the
observer, per that module's own docstring) and
`app.astro.panchanga.compute_panchanga()` verbatim -- zero new astrology
math, just a chart-free entry point into engines that already existed.
"""
from __future__ import annotations

from datetime import date
from typing import Any

from fastapi import APIRouter, Query

from app.astro.engine import get_nakshatra
from app.astro.panchanga import compute_panchanga
from app.astro.transits import transit_chart

router = APIRouter(prefix="/api/v2/today", tags=["today"])

PLANET_ORDER = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]


@router.get("/transits")
async def api_today_transits(
    on_date: date = Query(default_factory=date.today),
    utc_offset: float = 5.5,
    node_type: str = "mean",
) -> dict[str, Any]:
    """Real sidereal positions for every graha on a given calendar date
    (default: today), with no natal chart involved -- sign/degree/
    nakshatra/retrograde/speed only. House-from-Lagna and Sade Sati are
    inherently chart-specific and stay on the Chart Workbench's own
    Transits tab, not here."""
    positions = transit_chart(on_date, utc_offset=utc_offset, node_type=node_type)
    planets: dict[str, Any] = {}
    for name in PLANET_ORDER:
        pos = positions[name]
        nak = get_nakshatra(pos["longitude"])
        planets[name] = {**pos, "nakshatra": nak["nakshatra"]["en"], "pada": nak["pada"]}
    return {"date": on_date.isoformat(), "utc_offset": utc_offset, "node_type": node_type, "planets": planets}


@router.get("/panchanga")
async def api_today_panchanga(on_date: date = Query(default_factory=date.today), utc_offset: float = 5.5) -> dict[str, Any]:
    """The 5 classical limbs (Vara/Tithi/Nakshatra/Yoga/Karana) for a given
    calendar date (default: today), computed at local noon -- no birth
    chart needed. Same `compute_panchanga()` the Chart Workbench's
    per-chart Panchanga tab uses, just fed today's Sun/Moon longitude
    instead of a birth-moment one."""
    positions = transit_chart(on_date, utc_offset=utc_offset)
    panchanga = compute_panchanga(positions["Sun"]["longitude"], positions["Moon"]["longitude"], on_date)
    return {"date": on_date.isoformat(), "utc_offset": utc_offset, **panchanga}
