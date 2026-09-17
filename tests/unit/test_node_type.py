"""Unit tests for the node_type (mean/true) config knob.

build_plan.md Phase 1 item; originally flagged by
docs/public-repo-review/03-validation-cross-checks.md Check 1 -- a real
~21' Rahu/Ketu discrepancy against PyJHora on Ajay Kumar's chart was
explained entirely by our engine hardcoding mean-node while PyJHora
defaulted to true-node. This test locks in that the knob (a) actually
changes the computed position, (b) never touches any other planet as a
side effect, (c) defaults to "mean" for full backward compatibility with
every existing chart fixture, and (d) fails loudly on a bad value instead
of silently defaulting (AGENTS.md Cardinal Rule #2 -- never fabricate).
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.astro.engine import all_planets_sidereal, julian_day
from app.astro.transits import transit_chart
from app.derived.factors import build_chart_context
from app.fixtures import load_chart_fixture
from datetime import date

_JD = julian_day(1988, 6, 15, 10.5, 5.5)
_LAT, _LON = 17.385, 78.4867


def test_mean_and_true_node_produce_different_rahu_position():
    mean = all_planets_sidereal(_JD, _LAT, _LON, node_type="mean")
    true = all_planets_sidereal(_JD, _LAT, _LON, node_type="true")
    assert mean["Rahu"]["longitude"] != true["Rahu"]["longitude"]
    # Mean/true node divergence is bounded (never more than ~1.5 degrees
    # in practice) -- a sanity ceiling, not a precise physical constant.
    diff_deg = abs(mean["Rahu"]["longitude"] - true["Rahu"]["longitude"])
    assert diff_deg < 1.5


def test_ketu_follows_rahu_180_regardless_of_node_type():
    for node_type in ("mean", "true"):
        chart = all_planets_sidereal(_JD, _LAT, _LON, node_type=node_type)
        expected_ketu = (chart["Rahu"]["longitude"] + 180.0) % 360.0
        assert abs(chart["Ketu"]["longitude"] - expected_ketu) < 0.001


def test_node_type_has_no_side_effect_on_other_planets():
    mean = all_planets_sidereal(_JD, _LAT, _LON, node_type="mean")
    true = all_planets_sidereal(_JD, _LAT, _LON, node_type="true")
    for planet in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Lagna"]:
        assert mean[planet]["longitude"] == true[planet]["longitude"], (
            f"{planet} must be identical regardless of node_type -- "
            "node_type must never leak into unrelated computations"
        )


def test_default_node_type_is_mean_for_backward_compatibility():
    default = all_planets_sidereal(_JD, _LAT, _LON)
    explicit_mean = all_planets_sidereal(_JD, _LAT, _LON, node_type="mean")
    assert default["Rahu"]["longitude"] == explicit_mean["Rahu"]["longitude"]


def test_invalid_node_type_raises_instead_of_silently_defaulting():
    with pytest.raises(ValueError):
        all_planets_sidereal(_JD, _LAT, _LON, node_type="bogus")


def test_transit_chart_also_honors_node_type():
    d = date(2026, 1, 1)
    mean = transit_chart(d, node_type="mean")
    true = transit_chart(d, node_type="true")
    assert mean["Rahu"]["longitude"] != true["Rahu"]["longitude"]
    assert mean["Sun"]["longitude"] == true["Sun"]["longitude"]


def test_build_chart_context_reads_fixture_node_type_not_hardcoded():
    """Every fixture in data/charts/ declares node_type: mean explicitly.
    Before this fix that field was decorative -- the engine always used
    mean regardless. Verify build_chart_context now actually threads it."""
    fixture = load_chart_fixture("ajay_kumar")
    assert fixture.get("settings", {}).get("node_type") == "mean"
    ctx = build_chart_context(fixture)
    expected = all_planets_sidereal(
        ctx["jd"], fixture["location"]["latitude"], fixture["location"]["longitude"],
        node_type="mean",
    )
    assert ctx["chart"]["Rahu"]["longitude"] == expected["Rahu"]["longitude"]

    # Now prove it's not just coincidentally matching "mean" -- flip the
    # fixture's declared node_type in memory and confirm the output changes.
    fixture_true = dict(fixture)
    fixture_true["settings"] = {**fixture.get("settings", {}), "node_type": "true"}
    ctx_true = build_chart_context(fixture_true)
    assert ctx_true["chart"]["Rahu"]["longitude"] != ctx["chart"]["Rahu"]["longitude"]


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
