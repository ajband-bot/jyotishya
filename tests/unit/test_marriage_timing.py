"""Unit tests for app.derived.marriage_timing -- the Dasha/Transit/D9
Triple Agreement marriage-timing engine (build_plan.md Phase 4a item 3).
"""
from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.derived.factors import build_chart_context
from app.derived.marriage_timing import (
    dasha_agreement_windows,
    identify_significators,
    marriage_timing_report,
    transit_agreement_dates,
)
from app.fixtures import load_chart_fixture


def _ctx(chart_id: str):
    return build_chart_context(load_chart_fixture(chart_id))


def test_identify_significators_male_uses_venus_as_karaka():
    ctx = _ctx("ajay_kumar")
    result = identify_significators(ctx, gender="male")
    assert result["marriage_karaka"] == "Venus"
    assert result["h7_lord"] == "Venus"  # Ajay's own H7 lord happens to also be Venus
    assert result["darakaraka"] == "Mars"
    ranks = {item["rank"] for item in result["ranked_significators"]}
    assert ranks.issubset({1, 2, 3, 4, 5, 6, 7})


def test_identify_significators_female_uses_jupiter_as_karaka():
    ctx = _ctx("sravani")
    result = identify_significators(ctx, gender="female")
    assert result["marriage_karaka"] == "Jupiter"


def test_identify_significators_rejects_invalid_gender():
    ctx = _ctx("ajay_kumar")
    try:
        identify_significators(ctx, gender="other")
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_dasha_agreement_windows_finds_rahu_venus_period():
    """Cross-check: both Marriage_Guide_Part3.md and
    Ajay_Sravani_Compatibility.md flag Ajay's Rahu/Venus antardasha
    (Venus = his H7 lord) as a prime marriage-activation window."""
    ctx = _ctx("ajay_kumar")
    significators = identify_significators(ctx, gender="male")
    windows = dasha_agreement_windows(ctx, significators)
    assert any(w["mahadasha"] == "Rahu" and w["antardasha"] == "Venus" for w in windows)
    rahu_venus = next(w for w in windows if w["mahadasha"] == "Rahu" and w["antardasha"] == "Venus")
    assert rahu_venus["best_rank"] == 1  # Venus is H7 lord (rank 1) for Ajay


def test_dasha_windows_sorted_by_rank_then_date():
    ctx = _ctx("ajay_kumar")
    significators = identify_significators(ctx, gender="male")
    windows = dasha_agreement_windows(ctx, significators)
    ranks = [w["best_rank"] for w in windows]
    assert ranks == sorted(ranks[:len(ranks)]) or True  # monotonic non-decreasing within any same-rank date ties
    for earlier, later in zip(windows, windows[1:]):
        assert (earlier["best_rank"], earlier["start"]) <= (later["best_rank"], later["start"])


def test_transit_agreement_dates_returns_only_favorable_scores():
    ctx = _ctx("ajay_kumar")
    dates = transit_agreement_dates(ctx["chart"], date(2027, 1, 1), date(2027, 12, 31), step_days=60)
    for entry in dates:
        assert entry["score"] >= 2


def test_marriage_timing_report_end_to_end_structure():
    """Small years/step window purely for test speed -- not a scope
    reflection of the real API default."""
    ctx = _ctx("ajay_kumar")
    report = marriage_timing_report(ctx, gender="male", years=5, step_days=60)
    assert "significators" in report
    assert "dasha_windows" in report
    assert "transit_favorable_dates" in report
    assert "combined_windows" in report
    for window in report["combined_windows"]:
        assert window["verdict"] in {"possible", "confirmed", "certain"}
        assert 1 <= window["agreement_count"] <= 3


def test_combined_windows_carry_probability_percent_and_reason():
    ctx = _ctx("ajay_kumar")
    report = marriage_timing_report(ctx, gender="male", years=10, step_days=60)
    assert report["probability_model"] == "heuristic_proxy"
    assert "probability_caveat" in report and "NOT a statistically validated probability" in report["probability_caveat"]
    for window in report["combined_windows"]:
        assert window["probability_percent"] == {"certain": 85, "confirmed": 60, "possible": 35}[window["verdict"]]
        assert isinstance(window["reason"], str) and len(window["reason"]) > 0
        assert window["mahadasha"] in window["reason"] or window["antardasha"] in window["reason"]


def test_upcoming_windows_are_filtered_to_today_or_future_and_capped():
    ctx = _ctx("ajay_kumar")
    report = marriage_timing_report(ctx, gender="male", years=15, step_days=60)
    today_str = date.today().isoformat()
    assert len(report["upcoming_windows"]) <= 5
    for window in report["upcoming_windows"]:
        assert window["end"] >= today_str


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
