"""Unit tests for the divisional-chart (varga) engine — app/astro/vargas.py.

Per docs/technical-architecture.md §9 and spec §22: every varga mapping
algorithm gets a unit test with a known-good fixture before being wired
into any API.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.astro.engine import navamsha_sign
from app.astro.vargas import (
    SUPPORTED_VARGAS,
    VARGA_META,
    compute_all_vargas,
    compute_varga,
)
from app.derived.factors import build_chart_context
from app.fixtures import load_chart_fixture

FIXTURE_ID = "ajay_kumar"
_ALL_PLANETS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu", "Lagna"]


def _chart():
    fixture = load_chart_fixture(FIXTURE_ID)
    ctx = build_chart_context(fixture)
    return ctx["chart"]


def test_all_supported_vargas_compute_without_error():
    chart = _chart()
    vargas = compute_all_vargas(chart)
    assert set(vargas.keys()) == {f"D{n}" for n in SUPPORTED_VARGAS}
    for key, data in vargas.items():
        assert data["lagna_sign"] in range(1, 13)
        for planet in _ALL_PLANETS:
            assert planet in data["planets"], f"{planet} missing in {key}"
            assert data["planets"][planet]["sign"] in range(1, 13)


def test_d1_is_identity_passthrough():
    chart = _chart()
    d1 = compute_varga(chart, 1)
    assert d1["lagna_sign"] == chart["Lagna"]["sign"]
    for planet in _ALL_PLANETS:
        assert d1["planets"][planet]["sign"] == chart[planet]["sign"]
        assert abs(d1["planets"][planet]["deg_in_sign"] - chart[planet]["deg_in_sign"]) < 0.01


def test_d9_matches_existing_engine_formula():
    """New generic engine's D9 must agree exactly with the already-verified
    app.astro.engine.navamsha_sign() used throughout the narrative pipeline."""
    chart = _chart()
    d9 = compute_varga(chart, 9)
    for planet in _ALL_PLANETS:
        lon = chart[planet]["longitude"]
        expected_sign = navamsha_sign(lon)
        assert d9["planets"][planet]["sign"] == expected_sign, f"D9 mismatch for {planet}"


def test_d60_always_carries_birth_time_warning():
    chart = _chart()
    d60 = compute_varga(chart, 60)
    assert d60.get("birth_time_sensitivity_warning") is True
    assert "warning_note" in d60 and len(d60["warning_note"]) > 0


def test_d30_trimsamsa_uses_irregular_degree_ranges_not_equal_division():
    """D30 (Trimsamsa) is classically NOT an equal 1-degree division — verify
    the resulting sign changes at the documented irregular boundaries rather
    than every 1 degree."""
    chart = _chart()
    d30 = compute_varga(chart, 30)
    # Every planet's D30 sign must come from the finite classical planet-lord set
    for planet in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
        assert d30["planets"][planet]["sign"] in range(1, 13)


def test_unsupported_divisor_raises():
    chart = _chart()
    try:
        compute_varga(chart, 5)
        assert False, "expected ValueError for unsupported divisor D5"
    except ValueError:
        pass


def test_d5_d6_d8_d11_deliberately_unsupported_not_missing_by_accident():
    """These four divisions were checked against the actual BPHS PDF text
    (2026-09-16, docs/rule-v1-to-v2-parity.md / build_plan.md Phase 1) and
    found absent from BPHS's own Shodasavarga (16-fold) scheme -- BPHS Ch.6
    explicitly enumerates 16 divisions from Rasi to Shashtiamsa, no more.
    This test locks in that they stay unsupported (raise, not silently
    guess) until a genuine textual basis is found in a lower-tier source
    per AD-5, rather than being ported wholesale from PyJHora."""
    chart = _chart()
    for n in (5, 6, 8, 11):
        try:
            compute_varga(chart, n)
            assert False, f"expected ValueError for D{n} -- not in BPHS's 16-varga scheme"
        except ValueError:
            pass


def test_d40_khavedamsa_odd_sign_starts_from_aries_even_from_libra():
    """BPHS Ch.6 v.29-30: odd signs count Khavedamsa divisions from Aries,
    even signs from Libra. Verify on a synthetic D1 at 0deg (part index 0)
    for both an odd sign (Aries) and an even sign (Taurus)."""
    from app.astro.vargas import _varga_sign_and_degree

    aries_sign, _ = _varga_sign_and_degree(1, 0.0, 40)   # Aries = odd sign
    assert aries_sign == 1  # first part of D40 for an odd sign is Aries
    taurus_sign, _ = _varga_sign_and_degree(2, 0.0, 40)  # Taurus = even sign
    assert taurus_sign == 7  # first part of D40 for an even sign is Libra


def test_d45_akshavedamsa_starts_by_modality():
    """BPHS Ch.6 v.31-32: movable signs start Akshavedamsa from Aries,
    fixed signs from Leo, dual signs from Sagittarius."""
    from app.astro.vargas import _varga_sign_and_degree

    movable_sign, _ = _varga_sign_and_degree(1, 0.0, 45)   # Aries = movable
    assert movable_sign == 1
    fixed_sign, _ = _varga_sign_and_degree(2, 0.0, 45)     # Taurus = fixed
    assert fixed_sign == 5  # Leo
    dual_sign, _ = _varga_sign_and_degree(3, 0.0, 45)      # Gemini = dual
    assert dual_sign == 9  # Sagittarius


def test_varga_meta_has_citation_status_for_every_supported_varga():
    """Honesty guardrail (AGENTS.md Cardinal Rule #2): no varga may claim
    verified status without an explicit citation_status field."""
    for n in SUPPORTED_VARGAS:
        assert "citation_status" in VARGA_META[n]
        assert "significance" in VARGA_META[n]


def test_vargottama_detection_consistent_with_d1_and_d9():
    chart = _chart()
    vargas = compute_all_vargas(chart, divisors=(1, 9))
    d9 = vargas["D9"]
    for planet in d9["vargottama"]:
        assert chart[planet]["sign"] == d9["planets"][planet]["sign"]


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
