"""Unit tests for build_plan.md Phase 2 batch-2 engines: Bhava Bala +
avastha layer, and the generic cross-varga confirmation engine.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.derived.bhava_bala import baladi_avastha, jagradadi_avastha
from app.derived.factors import build_chart_context
from app.derived.varga_confirmation import (
    confirm_dignity,
    confirm_planet_in_house,
    confirm_planet_in_sign,
)
from app.fixtures import list_fixture_ids, load_chart_fixture


def _context(fixture_id: str = "ajay_kumar"):
    return build_chart_context(load_chart_fixture(fixture_id))


# ── Avastha ─────────────────────────────────────────────────────────────
def test_baladi_avastha_odd_sign_reads_forward():
    assert baladi_avastha(2.0, 1)["stage"] == "Bala"       # Aries (odd), 0-6deg
    assert baladi_avastha(29.0, 1)["stage"] == "Mrita"     # Aries, 24-30deg


def test_baladi_avastha_even_sign_reads_reversed():
    assert baladi_avastha(2.0, 2)["stage"] == "Mrita"      # Taurus (even), reversed
    assert baladi_avastha(29.0, 2)["stage"] == "Bala"


def test_jagradadi_avastha_matches_dignity_state():
    assert jagradadi_avastha("Sun", 1)["stage"] == "Jagrat"       # Sun exalted in Aries
    assert jagradadi_avastha("Sun", 7)["stage"] == "Sushupti"     # Sun debilitated in Libra
    assert jagradadi_avastha("Mercury", 1)["stage"] == "Swapna"   # Mercury neutral in Aries


def test_avastha_report_wired_into_context_for_all_9_planets():
    ctx = _context()
    assert set(ctx["avasthas"].keys()) == {
        "Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu",
    }
    for data in ctx["avasthas"].values():
        assert data["baladi"]["stage"] in {"Bala", "Kumara", "Yuva", "Vriddha", "Mrita"}
        assert data["jagradadi"]["stage"] in {"Jagrat", "Swapna", "Sushupti"}


# ── Bhava Bala ──────────────────────────────────────────────────────────
def test_bhava_bala_covers_all_12_houses_with_valid_verdicts():
    ctx = _context()
    bb = ctx["bhava_bala"]
    assert set(bb["houses"].keys()) == set(range(1, 13))
    for house_data in bb["houses"].values():
        assert house_data["verdict"] in {"strong", "moderate", "weak"}
        assert 0 <= house_data["total_score"] <= 100


def test_bhava_bala_present_for_every_fixture():
    for fixture_id in list_fixture_ids():
        ctx = _context(fixture_id)
        assert len(ctx["bhava_bala"]["houses"]) == 12


# ── Cross-varga confirmation ────────────────────────────────────────────
def test_confirm_planet_in_sign_d1_always_confirms_itself():
    chart = _context()["chart"]
    sun_sign = chart["Sun"]["sign"]
    result = confirm_planet_in_sign(chart, "Sun", sun_sign)
    assert result["per_varga"]["D1"] is True
    assert result["confirmation_count"] >= 1


def test_confirm_planet_in_sign_wrong_sign_never_confirms():
    chart = _context()["chart"]
    sun_sign = chart["Sun"]["sign"]
    wrong_sign = (sun_sign % 12) + 1
    result = confirm_planet_in_sign(chart, "Sun", wrong_sign)
    assert result["confirmation_count"] == 0
    assert result["fully_confirmed"] is False


def test_confirm_planet_in_house_matches_chart_directly():
    chart = _context()["chart"]
    house = chart["Moon"]["house"]
    result = confirm_planet_in_house(chart, "Moon", house)
    assert result["per_varga"]["D1"] is True


def test_confirm_dignity_reflects_known_debilitation_or_exaltation():
    """Whatever D1 dignity state a planet actually has must be reflected in D1's own entry."""
    from app.astro.engine import planet_state

    chart = _context()["chart"]
    for planet in ["Sun", "Moon", "Saturn"]:
        d1_state = planet_state(planet, chart[planet]["sign"])
        result = confirm_dignity(chart, planet, {d1_state})
        assert result["per_varga"]["D1"] is True


def test_confirmation_ratio_bounds():
    chart = _context()["chart"]
    result = confirm_planet_in_sign(chart, "Jupiter", chart["Jupiter"]["sign"], vargas=[9, 10])
    assert 0.0 <= result["confirmation_ratio"] <= 1.0
    assert result["confirmation_total"] == 3  # D1 + D9 + D10


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
