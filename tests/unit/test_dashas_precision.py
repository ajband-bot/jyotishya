"""Unit tests for app.astro.dashas -- precision fix found 2026-09-16 while
investigating a user-reported live pratyantardasha mismatch (see
docs/dasha-precision-fix.md).

The bug: compute_antardashas()/compute_pratyantaradashas() used to
truncate (`int()`) each sub-period's own day-count and stack the
truncated pieces, silently losing up to ~1 day per sub-period. Over 9
Antardashas within a Mahadasha (or 9 Pratyantardashas within an
Antardasha), those losses compounded, so the LAST sub-period's computed
end date fell several days short of its parent period's own end date --
a violation of the basic invariant that sub-periods must exactly tile
their parent period with no gap or overlap. Fixed by tracking a single
cumulative elapsed-days float and rounding exactly once per boundary.
"""
from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.astro.dashas import compute_antardashas, compute_dashas, compute_pratyantaradashas
from app.derived.factors import build_chart_context
from app.fixtures import load_chart_fixture


def _day_gap(iso_a: str, iso_b: str) -> int:
    return abs((date.fromisoformat(iso_a) - date.fromisoformat(iso_b)).days)


def _ctx(chart_id: str, today: date):
    return build_chart_context(load_chart_fixture(chart_id), today=today)


def test_last_antardasha_ends_within_a_day_of_mahadasha_end():
    """Regression guard for the compounding-truncation bug: the 9th
    (last) antardasha's end date must land within 1 day of the
    mahadasha's own end date -- a single independent-rounding residual is
    expected and fine (each level rounds its own boundary once from its
    own parent's already-rounded start); what the old code did wrong was
    accumulate up to ~9 STACKED truncations, producing multi-day gaps.
    Before this fix that gap was 5 days for this exact chart/mahadasha;
    after the fix it is <=1 day."""
    fixture = load_chart_fixture("ajay_kumar")
    chart_ctx = build_chart_context(fixture)
    mahadasha = next(d for d in chart_ctx["dashas"] if d["planet"] == "Rahu")
    antars = compute_antardashas(mahadasha)
    assert _day_gap(antars[-1]["end"], mahadasha["end"]) <= 1


def test_last_pratyantardasha_ends_within_a_day_of_antardasha_end():
    fixture = load_chart_fixture("ajay_kumar")
    chart_ctx = build_chart_context(fixture)
    mahadasha = next(d for d in chart_ctx["dashas"] if d["planet"] == "Rahu")
    antars = compute_antardashas(mahadasha)
    moon_antardasha = next(a for a in antars if a["planet"] == "Moon")
    pratyas = compute_pratyantaradashas(mahadasha, moon_antardasha)
    assert _day_gap(pratyas[-1]["end"], moon_antardasha["end"]) <= 1


def test_critical_date_baseline_unaffected_by_precision_fix():
    """tests/run_suite.py's frozen regression anchor (2026-04-11) must
    still resolve to the exact same dasha chain after this fix -- the fix
    only removes drift accumulated over LONG spans, it must not silently
    change already-verified historical checkpoints."""
    ajay = _ctx("ajay_kumar", date(2026, 4, 11))
    cd = ajay["current_dasha"]
    assert (cd["mahadasha"]["planet"], cd["antardasha"]["planet"], cd["pratyantardasha"]["planet"]) == ("Rahu", "Moon", "Rahu")

    sandeep = _ctx("sandeep_0700", date(2026, 4, 11))
    cd2 = sandeep["current_dasha"]
    assert (cd2["mahadasha"]["planet"], cd2["antardasha"]["planet"], cd2["pratyantardasha"]["planet"]) == ("Mercury", "Jupiter", "Venus")


def test_pratyantardasha_boundary_near_2026_09_16_is_saturn_not_mercury():
    """Locks in the corrected answer for the specific date this bug was
    reported against (2026-09-16): Saturn pratyantardasha runs
    2026-06-30 -> 2026-09-25 within Ajay's Rahu/Moon antardasha; Mercury
    only begins 2026-09-26. If a chart's own real-world 'today' is on or
    after 2026-09-26, Mercury is correctly current -- that is a
    real-calendar-date question, not a bug in this engine."""
    ajay = _ctx("ajay_kumar", date(2026, 9, 16))
    pd = ajay["current_dasha"]["pratyantardasha"]
    assert pd["planet"] == "Saturn"
    assert pd["start"] == "2026-06-30"
    assert pd["end"] == "2026-09-25"


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
