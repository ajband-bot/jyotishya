"""Unit tests for the chart-independent "today" API (Phase 8 follow-up):
GET /api/v2/today/transits and GET /api/v2/today/panchanga. Both take an
explicit on_date so these tests are deterministic, not date.today()
dependent.
"""
from __future__ import annotations

import asyncio
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.api.v2.today import api_today_panchanga, api_today_transits  # noqa: E402

FIXED_DATE = date(2026, 9, 17)


def _run(coro):
    return asyncio.run(coro)


def test_today_transits_returns_all_nine_grahas_with_nakshatra():
    result = _run(api_today_transits(on_date=FIXED_DATE))
    assert result["date"] == "2026-09-17"
    planets = result["planets"]
    for name in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]:
        assert name in planets
        assert "sign_en" in planets[name]
        assert "nakshatra" in planets[name]
        assert 1 <= planets[name]["pada"] <= 4


def test_today_transits_is_chart_independent_and_deterministic():
    """Same date -> same result, regardless of call order/context -- no
    hidden dependency on any birth chart or global state."""
    first = _run(api_today_transits(on_date=FIXED_DATE))
    second = _run(api_today_transits(on_date=FIXED_DATE))
    assert first == second


def test_today_panchanga_returns_all_five_limbs():
    result = _run(api_today_panchanga(on_date=FIXED_DATE))
    for limb in ["vara", "tithi", "nakshatra", "yoga", "karana"]:
        assert limb in result
    assert result["vara"]["name"] == "Thursday"


def test_today_panchanga_moon_nakshatra_matches_transits_moon_nakshatra():
    """Both endpoints must derive the Moon's nakshatra from the identical
    transit_chart() longitude -- they must never silently disagree."""
    transits = _run(api_today_transits(on_date=FIXED_DATE))
    panchanga = _run(api_today_panchanga(on_date=FIXED_DATE))
    assert transits["planets"]["Moon"]["nakshatra"] == panchanga["nakshatra"]["name"]
    assert transits["planets"]["Moon"]["pada"] == panchanga["nakshatra"]["pada"]


if __name__ == "__main__":
    import traceback

    tests = [obj for name, obj in list(globals().items()) if name.startswith("test_")]
    failed = 0
    for t in tests:
        try:
            t()
            print(f"[PASS] {t.__name__}")
        except Exception:
            failed += 1
            print(f"[FAIL] {t.__name__}")
            traceback.print_exc()
    print(f"\n{len(tests) - failed}/{len(tests)} passed")
    raise SystemExit(1 if failed else 0)
