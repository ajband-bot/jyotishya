"""Unit tests for the Chart Lab sandbox (app/derived/sandbox.py) -- the
drag-and-drop hypothetical-chart analysis engine."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.derived.sandbox import (
    ALL_9,
    PlanetPlacement,
    SandboxRequest,
    analyze_sandbox,
    build_sandbox_chart,
)


def _basic_request(**overrides) -> SandboxRequest:
    planets = {
        "Sun": PlanetPlacement(sign=4, degree=10),
        "Moon": PlanetPlacement(sign=1, degree=5),
        "Mars": PlanetPlacement(sign=8, degree=20),
        "Mercury": PlanetPlacement(sign=5, degree=8),
        "Jupiter": PlanetPlacement(sign=11, degree=12),
        "Venus": PlanetPlacement(sign=3, degree=25),
        "Saturn": PlanetPlacement(sign=1, degree=18, retrograde=True),
        "Rahu": PlanetPlacement(sign=11, degree=3),
    }
    return SandboxRequest(lagna_sign=8, planets=planets, **overrides)


def test_ketu_is_always_180_from_rahu():
    req = _basic_request()
    chart = build_sandbox_chart(req)
    diff = abs(chart["Rahu"]["longitude"] - chart["Ketu"]["longitude"])
    assert abs(diff - 180.0) < 0.01


def test_ketu_is_always_retrograde():
    req = _basic_request()
    chart = build_sandbox_chart(req)
    assert chart["Ketu"]["retrograde"] is True


def test_house_numbering_relative_to_lagna():
    req = _basic_request()
    chart = build_sandbox_chart(req)
    # Lagna sign 8 (Scorpio); Mars also in sign 8 -> house 1
    assert chart["Mars"]["house"] == 1
    # Moon in sign 1 (Aries); rel to lagna sign 8 -> house 6
    assert chart["Moon"]["house"] == 6


def test_analyze_sandbox_produces_all_9_planets_and_12_houses():
    req = _basic_request()
    result = analyze_sandbox(req)
    assert set(result["planets"].keys()) == set(ALL_9)
    assert set(result["houses"].keys()) == set(range(1, 13))


def test_analyze_sandbox_detects_ruchaka_mahapurusha_for_own_sign_kendra_mars():
    """Mars in Scorpio (own sign) as Lagna itself (H1) for Scorpio Lagna --
    a genuine Ruchaka Mahapurusha Yoga case, real regression guard."""
    req = _basic_request()
    result = analyze_sandbox(req)
    yoga_names = [y["name"] for y in result["yogas"]]
    assert any("రుచక" in name for name in yoga_names)


def test_analyze_sandbox_flags_data_gaps_explicitly():
    req = _basic_request()
    result = analyze_sandbox(req)
    assert len(result["data_gaps"]) >= 1
    assert any("Dasha" in gap for gap in result["data_gaps"])


def test_functional_nature_present_for_classical_7_not_nodes():
    req = _basic_request()
    result = analyze_sandbox(req)
    assert "functional" in result["planets"]["Mars"]
    assert "functional" not in result["planets"]["Rahu"]


def test_day_night_toggle_changes_kala_bala():
    day_req = _basic_request(day_or_night="day")
    night_req = _basic_request(day_or_night="night")
    day_result = analyze_sandbox(day_req)
    night_result = analyze_sandbox(night_req)
    # Sun is DAY_STRONG -- kala_bala component should differ between toggles
    day_kala = day_result["planets"]["Sun"]["shadbala"]["components"]["kala_bala"]
    night_kala = night_result["planets"]["Sun"]["shadbala"]["components"]["kala_bala"]
    assert day_kala != night_kala


def test_house_connections_trace_lord_to_actual_placement():
    """House-connection tracing must follow the lord to wherever it
    ACTUALLY sits in THIS chart, not a generic lagna-only template."""
    req = _basic_request()
    result = analyze_sandbox(req)
    connections = result["house_connections"]
    assert set(connections.keys()) == set(range(1, 13))
    for house_no, conn in connections.items():
        assert conn["lord_house"] == result["planets"][conn["lord"]]["house"]
        assert "->" in conn["connection"]


def test_invalid_sign_rejected():
    import pytest
    with pytest.raises(Exception):
        PlanetPlacement(sign=13, degree=10)


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
