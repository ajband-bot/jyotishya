"""Unit tests for app.derived.shadbala -- full classical Shadbala
(BPHS Ch.27), build_plan.md Phase 5. See module docstring for the
disclosed data_gap components (Varsha/Masa Bala, Chesta Bala for the 5
non-luminary planets, Drik Bala).
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.derived.factors import build_chart_context
from app.derived.shadbala import CLASSICAL_7, ayana_bala, dig_bala, full_shadbala, kendradi_bala
from app.derived.shadbala import NAISARGIKA_BALA_RUPAS, paksha_bala, uchcha_bala
from app.fixtures import load_chart_fixture


def _ctx(chart_id: str):
    return build_chart_context(load_chart_fixture(chart_id))


def test_uchcha_bala_max_60_at_exact_exaltation():
    """Sun exalted at 10 deg Aries -> longitude 10.0 exactly -> full 60 Virupas."""
    assert uchcha_bala("Sun", 10.0) == 60.0


def test_uchcha_bala_zero_at_exact_debilitation():
    """Sun debilitated at 10 deg Libra -> longitude 190.0 exactly -> 0 Virupas."""
    assert uchcha_bala("Sun", 190.0) == 0.0


def test_kendradi_bala_three_tiers():
    assert kendradi_bala(1) == 60.0
    assert kendradi_bala(2) == 30.0
    assert kendradi_bala(3) == 15.0


def test_dig_bala_full_60_at_ideal_cusp():
    """Saturn's ideal cusp is the 7th house -- construct a trivial 1-planet
    chart dict where Saturn sits exactly at the 7th house's sign start."""
    lagna_sign = 1  # Aries
    chart = {"Saturn": {"longitude": 180.0}}  # 7th from Aries = Libra = 180 deg start
    assert dig_bala("Saturn", chart, lagna_sign) == 60.0


def test_dig_bala_zero_at_own_ascendant_cusp():
    lagna_sign = 1
    chart = {"Saturn": {"longitude": 0.0}}  # Ascendant cusp itself = Saturn's zero point
    assert dig_bala("Saturn", chart, lagna_sign) == 0.0


def test_paksha_bala_full_moon_gives_benefics_max():
    """Moon exactly opposite Sun (full moon, 180 deg) -> benefics get max 60."""
    result = paksha_bala(sun_longitude=0.0, moon_longitude=180.0)
    assert result["Moon"] == 60.0
    assert result["Sun"] == 0.0


def test_naisargika_bala_rupas_matches_bphs_ch27_v14_table():
    assert NAISARGIKA_BALA_RUPAS == {
        "Sun": 1.000, "Moon": 0.857, "Mars": 0.286, "Mercury": 0.429,
        "Jupiter": 0.571, "Venus": 0.714, "Saturn": 0.143,
    }


def test_ayana_bala_bounded_0_to_60():
    for kranti in (-23.45, -10.0, 0.0, 10.0, 23.45):
        for planet in CLASSICAL_7:
            v = ayana_bala(planet, kranti)
            assert 0.0 <= v <= 60.0


def test_full_shadbala_covers_all_7_planets_with_disclosed_gaps():
    ctx = _ctx("ajay_kumar")
    result = full_shadbala(ctx)
    assert set(result["planets"].keys()) == set(CLASSICAL_7)
    for planet in CLASSICAL_7:
        entry = result["planets"][planet]
        assert entry["drik_bala"] is None  # disclosed data_gap
        assert entry["sthana_bala"]["total_virupas"] >= 0
        assert 0.0 <= entry["dig_bala"] <= 60.0
        assert entry["computed_total_rupas"] > 0
        if planet not in ("Sun", "Moon"):
            assert entry["chesta_bala"] is None  # disclosed data_gap
        else:
            assert entry["chesta_bala"] is not None


def test_full_shadbala_dina_and_hora_lord_are_classical_planets():
    ctx = _ctx("ajay_kumar")
    result = full_shadbala(ctx)
    assert result["dina_lord"] in CLASSICAL_7
    assert result["hora_lord"] in CLASSICAL_7


def test_full_shadbala_runs_for_second_fixture_different_location():
    """Sandeep's fixture has a different lat/lon/time -- sanity guard that
    the sunrise-anchored components don't silently break for any chart."""
    ctx = _ctx("sandeep_0700")
    result = full_shadbala(ctx)
    assert len(result["planets"]) == 7


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
