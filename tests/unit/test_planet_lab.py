"""Unit tests for app.derived.reference_tables.get_planet_lab -- the
chart-SPECIFIC Planet Lab profile assembly (Phase 2)."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.derived.factors import build_chart_context
from app.derived.reference_tables import ALL_PLANETS, NODES, get_planet_lab
from app.fixtures import load_chart_fixture


def _ajay_ctx():
    return build_chart_context(load_chart_fixture("ajay_kumar"))


def test_planet_lab_covers_all_9_grahas():
    lab = get_planet_lab(_ajay_ctx())
    assert set(lab["planets"].keys()) == set(ALL_PLANETS + NODES)


def test_planet_lab_nodes_have_no_house_ownership():
    lab = get_planet_lab(_ajay_ctx())
    for node in NODES:
        assert lab["planets"][node]["functional"]["tag"] == "N/A"
        assert lab["planets"][node]["functional"]["houses_owned"] == []


def test_planet_lab_reuses_same_shadbala_and_ishta_kashta_as_context():
    """No separate calculation path -- must match build_chart_context exactly."""
    ctx = _ajay_ctx()
    lab = get_planet_lab(ctx)
    for planet in ALL_PLANETS + NODES:
        assert lab["planets"][planet]["shadbala"] == ctx["shadbala"][planet]
        assert lab["planets"][planet]["ishta_kashta"] == ctx["ishta_kashta"][planet]


def test_planet_lab_ajay_saturn_owns_h3_h4_not_h7_h8():
    """Cross-check for the RC-001 audit finding via a fully independent
    computation path (get_planet_lab, not the rule engine)."""
    lab = get_planet_lab(_ajay_ctx())
    saturn = lab["planets"]["Saturn"]["functional"]
    assert set(saturn["houses_owned"]) == {3, 4}


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
