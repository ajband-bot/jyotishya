"""Unit tests for app.astro.sunrise -- the sunrise/sunset primitive built
to unblock Shadbala's sunrise-anchored Kala Bala sub-components (build_plan.md
Phase 5). Previously a documented gap in app/astro/panchanga.py.
"""
from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.astro.engine import julian_day
from app.astro.sunrise import day_night_context, sunrise_sunset_jd


def test_sunrise_before_sunset_same_day():
    result = sunrise_sunset_jd(date(1987, 12, 31), 14.54519, 77.10552, utc_offset=5.5)
    assert result["sunrise_jd_ut"] < result["sunset_jd_ut"]


def test_day_night_context_before_sunrise_is_night():
    """Ajay Kumar born 04:15 IST -- well before sunrise (~06:45 local at
    that latitude/longitude in late December) -- must resolve to the
    PREVIOUS day's night segment, not flip to 'day'."""
    jd_birth = julian_day(1987, 12, 31, 4.25, 5.5)
    ctx = day_night_context(jd_birth, 14.54519, 77.10552)
    assert ctx["is_day_birth"] is False
    assert ctx["sunset_jd_ut"] < jd_birth < ctx["next_sunrise_jd_ut"]
    assert 0.0 <= ctx["segment_fraction_elapsed"] <= 1.0


def test_day_night_context_midday_is_day():
    jd_noon = julian_day(1987, 12, 31, 12.5, 5.5)
    ctx = day_night_context(jd_noon, 14.54519, 77.10552)
    assert ctx["is_day_birth"] is True


def test_segment_fraction_is_bounded():
    for hour in (0.5, 6.75, 12.0, 18.5, 23.5):
        jd = julian_day(1987, 12, 31, hour, 5.5)
        ctx = day_night_context(jd, 14.54519, 77.10552)
        assert 0.0 <= ctx["segment_fraction_elapsed"] <= 1.0


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
