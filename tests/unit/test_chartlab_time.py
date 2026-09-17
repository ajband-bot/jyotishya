"""Unit tests for Chart Lab v2 Sprint 2/3 -- app/derived/chartlab_time.py:
Vimsottari Dasha simulation and Transit overlay for the sandbox."""
from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.derived.chartlab_time import (
    NatalPointer,
    SandboxDashaRequest,
    SandboxTransitRequest,
    sandbox_dasha,
    sandbox_transits,
)


def test_dasha_without_birth_date_refuses_to_fabricate():
    req = SandboxDashaRequest(moon_sign=4, moon_degree=15.0)
    result = sandbox_dasha(req)
    assert result["mode"] == "manual_required"
    assert "mahadashas" not in result


def test_dasha_with_birth_date_computes_real_chain():
    req = SandboxDashaRequest(
        moon_sign=4, moon_degree=15.0, birth_date=date(2000, 5, 15), as_of_date=date(2026, 8, 25)
    )
    result = sandbox_dasha(req)
    assert result["mode"] == "computed"
    assert len(result["mahadashas"]) >= 9
    # Chain must cover the as_of date somewhere -- Vimsottari total is 120yrs
    assert result["current"].get("mahadasha") is not None


def test_dasha_current_matches_asof_window():
    req = SandboxDashaRequest(
        moon_sign=1, moon_degree=0.0, birth_date=date(1990, 1, 1), as_of_date=date(2000, 1, 1)
    )
    result = sandbox_dasha(req)
    md = result["current"]["mahadasha"]
    assert md["start"] <= "2000-01-01" <= md["end"]


def test_dasha_sequence_always_9_planet_cycle():
    req = SandboxDashaRequest(moon_sign=7, moon_degree=22.0, birth_date=date(1985, 3, 3))
    result = sandbox_dasha(req)
    from app.astro.constants import DASHA_ORDER

    for entry in result["mahadashas"]:
        assert entry["planet"] in DASHA_ORDER


def test_transits_return_all_9_grahas_for_any_date():
    result = sandbox_transits(SandboxTransitRequest(on_date=date(2026, 8, 25), lagna_sign=1, moon_sign=4))
    assert result["date"] == "2026-08-25"
    for planet in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]:
        assert planet in result["planets"]
        assert 1 <= result["planets"][planet]["sign"] <= 12
        assert 1 <= result["planets"][planet]["house_from_lagna"] <= 12


def test_transit_dignity_present_for_classical_seven_not_nodes():
    result = sandbox_transits(SandboxTransitRequest(on_date=date(2026, 8, 25), lagna_sign=1, moon_sign=4))
    assert "dignity" in result["planets"]["Saturn"]
    assert "dignity" not in result["planets"]["Rahu"]


def test_transit_ketu_always_180_from_rahu():
    result = sandbox_transits(SandboxTransitRequest(on_date=date(2026, 8, 25), lagna_sign=1, moon_sign=4))
    rahu_lon = result["planets"]["Rahu"]["longitude"]
    ketu_lon = result["planets"]["Ketu"]["longitude"]
    diff = abs(rahu_lon - ketu_lon) % 360
    assert abs(diff - 180.0) < 0.01


def test_transits_without_natal_planets_return_empty_contacts():
    result = sandbox_transits(SandboxTransitRequest(on_date=date(2026, 8, 25), lagna_sign=1, moon_sign=4))
    assert result["planets"]["Sun"]["natal_contacts"] == []


def test_transit_natal_conjunction_detected_within_orb():
    # Transit Sun on 2026-08-25 sits in Leo (sign 5) ~7.86 deg -- a natal
    # Sun a few degrees away in the SAME sign is a real conjunction.
    req = SandboxTransitRequest(
        on_date=date(2026, 8, 25),
        lagna_sign=1,
        moon_sign=4,
        natal_planets={"Sun": NatalPointer(sign=5, degree=9.0)},
    )
    result = sandbox_transits(req)
    contacts = result["planets"]["Sun"]["natal_contacts"]
    assert any(c["natal_planet"] == "Sun" and c["kind"] == "conjunction" for c in contacts)


def test_transit_natal_conjunction_outside_orb_not_reported():
    req = SandboxTransitRequest(
        on_date=date(2026, 8, 25),
        lagna_sign=1,
        moon_sign=4,
        natal_planets={"Sun": NatalPointer(sign=5, degree=25.0)},  # ~17 deg away, outside orb
    )
    result = sandbox_transits(req)
    contacts = result["planets"]["Sun"]["natal_contacts"]
    assert not any(c["natal_planet"] == "Sun" and c["kind"] == "conjunction" for c in contacts)


def test_transit_natal_aspect_detected_via_house_not_fabricated_as_conjunction():
    # Natal Saturn placed in a DIFFERENT sign that transit Saturn's own
    # special aspect (3rd/7th/10th) reaches -- must report 'aspect', with
    # no orb (sign-based, not exact-degree), never a fabricated conjunction.
    # lagna_sign=1 makes house_from_lagna == sign directly, keeping the
    # inversion trivial and unambiguous for this test.
    base = sandbox_transits(SandboxTransitRequest(on_date=date(2026, 8, 25), lagna_sign=1, moon_sign=4))
    sat = base["planets"]["Saturn"]
    target_sign = sat["aspects_houses"][0]
    req = SandboxTransitRequest(
        on_date=date(2026, 8, 25),
        lagna_sign=1,
        moon_sign=4,
        natal_planets={"Saturn": NatalPointer(sign=target_sign, degree=15.0)},
    )
    result = sandbox_transits(req)
    contacts = result["planets"]["Saturn"]["natal_contacts"]
    if sat["sign"] == target_sign:
        assert any(c["natal_planet"] == "Saturn" and c["kind"] == "conjunction" for c in contacts)
    else:
        matching = [c for c in contacts if c["natal_planet"] == "Saturn"]
        assert any(c["kind"] == "aspect" and c["orb_deg"] is None for c in matching)


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
