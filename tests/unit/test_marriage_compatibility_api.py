"""Unit tests for the Marriage Compatibility screen API (build_plan.md
Phase 8 follow-up): GET /api/v2/marriage-compatibility/{groom}/{bride}.

Uses FastAPI's TestClient against real golden fixtures (ajay_kumar,
sravani) -- same pattern as tests/unit/test_phase8_workbench.py.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402

client = TestClient(app)


def test_unmarried_mode_returns_marriage_timing_for_both_partners():
    resp = client.get("/api/v2/marriage-compatibility/ajay_kumar/sravani?already_married=false")
    assert resp.status_code == 200
    data = resp.json()
    assert data["already_married"] is False
    assert "marriage_timing" in data["groom"]
    assert "marriage_timing" in data["bride"]
    assert "married_life_status" not in data["groom"]
    for window in data["groom"]["marriage_timing"]["upcoming_windows"]:
        assert "probability_percent" in window
        assert "reason" in window


def test_married_mode_returns_married_life_status_for_both_partners():
    resp = client.get("/api/v2/marriage-compatibility/ajay_kumar/sravani?already_married=true")
    assert resp.status_code == 200
    data = resp.json()
    assert data["already_married"] is True
    assert "married_life_status" in data["groom"]
    assert "married_life_status" in data["bride"]
    assert "marriage_timing" not in data["groom"]
    assert "strengths" in data["groom"]["married_life_status"]
    assert "cautions" in data["groom"]["married_life_status"]


def test_pure_compatibility_metrics_present_regardless_of_married_flag():
    """Ashtakuta/synastry/D9-cross-compatibility are marital-status-
    independent -- they must appear identically either way."""
    unmarried = client.get("/api/v2/marriage-compatibility/ajay_kumar/sravani?already_married=false").json()
    married = client.get("/api/v2/marriage-compatibility/ajay_kumar/sravani?already_married=true").json()
    assert unmarried["ashtakuta"] == married["ashtakuta"]
    assert unmarried["synastry"] == married["synastry"]
    assert unmarried["d9_cross_compatibility"] == married["d9_cross_compatibility"]


def test_ashtakuta_includes_mangal_dosha_and_interpretation_band():
    resp = client.get("/api/v2/marriage-compatibility/ajay_kumar/sravani")
    data = resp.json()
    assert "mangal_dosha" in data["ashtakuta"]
    assert data["ashtakuta"]["interpretation"] in (
        "perfect", "excellent", "good", "average", "challenging", "requires_strong_overriding_factors",
    )


def test_same_chart_for_both_roles_is_rejected():
    resp = client.get("/api/v2/marriage-compatibility/ajay_kumar/ajay_kumar")
    assert resp.status_code == 400


def test_unknown_chart_id_returns_404():
    resp = client.get("/api/v2/marriage-compatibility/ajay_kumar/does-not-exist")
    assert resp.status_code == 404


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
