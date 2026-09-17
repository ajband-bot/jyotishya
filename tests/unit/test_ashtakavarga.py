"""Unit tests for the classical Ashtakavarga engine -- app/astro/ashtakavarga.py
and its `app/derived/ashtakavarga.py` chart-wiring layer.

Per build_plan.md Phase 1: "Full Ashtakavarga (Bhinna + Sarva)". The core
correctness guarantee exercised here is the classical chart-invariant: no
matter what a chart's planetary positions are, each Bhinnashtakavarga row
must always sum to the same fixed total (Sun 48, Moon 49, Mars 39,
Mercury 54, Jupiter 56, Venus 52, Saturn 39), and SAV must always total 337.
This is the exact guardrail against silent transcription/engine corruption
that a prior session flagged as the highest-risk part of this feature.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.astro.ashtakavarga import (
    EXPECTED_ROW_TOTAL,
    EXPECTED_SAV_TOTAL,
    SEVEN_PLANETS,
    bhinna_ashtakavarga,
    full_ashtakavarga,
    sarva_ashtakavarga,
)
from app.derived.ashtakavarga import classical_ashtakavarga
from app.derived.factors import build_chart_context
from app.fixtures import list_fixture_ids, load_chart_fixture

ALL_TARGETS = SEVEN_PLANETS + ["Lagna"]


def _chart(fixture_id: str):
    fixture = load_chart_fixture(fixture_id)
    return build_chart_context(fixture)["chart"]


def test_bav_row_totals_are_chart_invariant_across_every_golden_fixture():
    """The single most important safety net: regardless of birth data, each
    planet's Bhinnashtakavarga row must sum to its fixed classical total."""
    for fixture_id in list_fixture_ids():
        chart = _chart(fixture_id)
        bav = bhinna_ashtakavarga(chart)
        for target in ALL_TARGETS:
            total = sum(bav[target].values())
            assert total == EXPECTED_ROW_TOTAL[target], (
                f"{fixture_id}: {target} BAV totals {total}, "
                f"expected invariant {EXPECTED_ROW_TOTAL[target]}"
            )


def test_sav_total_is_337_across_every_golden_fixture():
    for fixture_id in list_fixture_ids():
        chart = _chart(fixture_id)
        bav = bhinna_ashtakavarga(chart)
        sav = sarva_ashtakavarga(bav)
        assert sum(sav.values()) == EXPECTED_SAV_TOTAL == 337


def test_full_ashtakavarga_signs_cover_all_twelve_and_agree_with_sav():
    chart = _chart("ajay_kumar")
    result = full_ashtakavarga(chart)
    assert set(result["signs"].keys()) == set(range(1, 13))
    for sign_no, entry in result["signs"].items():
        assert entry["sav_bindus"] == result["sarva"][sign_no]
        assert entry["verdict"] in {"favorable", "neutral", "challenging"}
        assert set(entry["bav_by_planet"].keys()) == set(SEVEN_PLANETS)


def test_bindus_land_in_correct_sign_for_a_simple_hand_check():
    """Sun contributes a bindu to its own 1st house (i.e. its own sign) --
    verify the landing-sign arithmetic directly for one fixed case."""
    chart = _chart("ajay_kumar")
    sun_sign = chart["Sun"]["sign"]
    bav = bhinna_ashtakavarga(chart)
    # Sun gives itself a bindu in house 1 (own sign) per BINDU_TABLE["Sun"]["Sun"].
    assert bav["Sun"][sun_sign] >= 1


def test_classical_ashtakavarga_wiring_reports_data_gap_for_nodes():
    fixture = load_chart_fixture("ajay_kumar")
    context = build_chart_context(fixture)
    av = context["ashtakavarga"]
    assert av["model"] == "classical_parashari"
    for planet in SEVEN_PLANETS:
        entry = av["current_transits"][planet]
        assert entry["model"] == "classical_parashari"
        assert 0 <= entry["sav_bindus"] <= 337
        assert 0 <= entry["pav_bindus"] <= 8
        assert entry["verdict"] in {"favorable", "challenging", "mixed"}
    for node in ("Rahu", "Ketu"):
        assert av["current_transits"][node]["model"] == "data_gap"


def test_classical_ashtakavarga_matches_direct_engine_call():
    chart = _chart("sandeep_0700")
    fixture = load_chart_fixture("sandeep_0700")
    context = build_chart_context(fixture)
    direct = full_ashtakavarga(chart)
    assert context["ashtakavarga"]["sav_total"] == direct["sav_total"] == 337


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
