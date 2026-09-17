"""Unit tests for build_plan.md Phase 2 item 10: Lagna-balanced regression
dataset audit (the honest, non-fabricating half of this item -- see
docs/historical-event-validation-protocol.md for why the historical-event
half is not code, and app.derived.lagna_coverage's module docstring for
why gaps are reported rather than filled with invented charts).
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.derived.factors import build_chart_context
from app.derived.lagna_coverage import (
    functional_nature_classification_coverage,
    lagna_coverage_report,
)
from app.fixtures import list_fixture_ids, load_chart_fixture


def _builder(fixture_id: str):
    return build_chart_context(load_chart_fixture(fixture_id))


def test_lagna_coverage_report_accounts_for_every_fixture_exactly_once():
    fixture_ids = list_fixture_ids()
    report = lagna_coverage_report(fixture_ids, _builder)
    assert report["total_fixtures"] == len(fixture_ids)
    total_in_by_sign = sum(len(fixtures) for fixtures in report["by_sign"].values())
    assert total_in_by_sign == len(fixture_ids)


def test_lagna_coverage_report_flags_the_known_current_gap_honestly():
    """As of this writing the 7 fixtures cover only 5/12 Lagna signs --
    this test locks that in as a VISIBLE gap (not silently passing), so
    adding a fixture that closes a gap shows up as an intentional test
    update, never an accidental regression."""
    fixture_ids = list_fixture_ids()
    report = lagna_coverage_report(fixture_ids, _builder)
    assert report["is_fully_balanced"] is False
    assert "Aries" in report["missing_signs"]
    assert report["distinct_lagna_signs_covered"] < 12


def test_functional_nature_classification_coverage_runs_without_error():
    fixture_ids = list_fixture_ids()
    report = functional_nature_classification_coverage(fixture_ids, _builder)
    assert "exercised" in report and "missing_classifications" in report
    assert isinstance(report["is_fully_exercised"], bool)


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
