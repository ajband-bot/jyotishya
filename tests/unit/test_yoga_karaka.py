"""Unit tests for app.derived.factors.is_yoga_karaka -- the classical
kendra+trikona dual-ownership test, fixed to exclude the trivial H1
self-membership bug (see inline docstring in factors.py for full history:
this bug was previously found independently in Pisces/Nikita and
Gemini/Shivani narrative readings before being fixed at the engine level).
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.derived.factors import is_yoga_karaka

# Standard classical yoga-karaka table (BPHS Ch.34) keyed by Lagna sign number.
# Sign numbers: 1=Aries .. 12=Pisces.
EXPECTED_YOGA_KARAKA = {
    1: None,          # Aries -- Mars owns H1+H8, both trivial/dusthana, no yoga-karaka
    2: "Saturn",       # Taurus -- Saturn owns H9 (Capricorn) + H10 (Aquarius)
    3: None,           # Gemini -- Mercury owns H1+H4, no dual kendra+trikona
    4: "Mars",         # Cancer -- Mars owns H5 (Aries) + H10 (Scorpio)
    5: "Mars",         # Leo -- Mars owns H4 (Scorpio) + H9 (Aries)
    6: None,           # Virgo -- Mercury owns H1+H10, trivial
    7: "Saturn",       # Libra -- Saturn owns H4 (Capricorn) + H5 (Aquarius)
    8: None,           # Scorpio -- Mars owns H1+H6, trivial
    9: None,           # Sagittarius -- Jupiter owns H1+H4, trivial
    10: "Venus",       # Capricorn -- Venus owns H5 (Taurus) + H10 (Libra)
    11: "Venus",       # Aquarius -- Venus owns H4 (Libra) + H9 (Taurus)
    12: None,          # Pisces -- Jupiter owns H1+H10, trivial (the exact bug case from AGENTS.md)
}

_ALL_PLANETS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]


def test_yoga_karaka_matches_classical_table_for_all_12_lagnas():
    for lagna_sign, expected_planet in EXPECTED_YOGA_KARAKA.items():
        found = [p for p in _ALL_PLANETS if is_yoga_karaka(lagna_sign, p)]
        if expected_planet is None:
            assert found == [], f"Lagna {lagna_sign}: expected no yoga-karaka, got {found}"
        else:
            assert found == [expected_planet], (
                f"Lagna {lagna_sign}: expected [{expected_planet}], got {found}"
            )


def test_pisces_jupiter_lagna_lord_is_never_yoga_karaka():
    """Regression guard for the exact bug documented in AGENTS.md /
    kennel memory: Jupiter as Pisces Lagna lord must NOT be flagged."""
    assert is_yoga_karaka(12, "Jupiter") is False


def test_gemini_mercury_lagna_lord_is_never_yoga_karaka():
    """Regression guard for the Gemini/Shivani instance of the same bug."""
    assert is_yoga_karaka(3, "Mercury") is False


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
