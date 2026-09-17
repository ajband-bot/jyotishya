"""Unit tests for app.derived.interventions -- classical Argala (BPHS
Ch.31), build_plan.md Phase 6.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.derived.factors import build_chart_context
from app.derived.interventions import CHANNELS, REFERENCE_HOUSES, practical_argala
from app.fixtures import list_fixture_ids, load_chart_fixture


def _ctx(chart_id: str):
    return build_chart_context(load_chart_fixture(chart_id))


def test_four_channels_including_the_5th_9th_correction():
    """BPHS Ch.31 v.2-9 names FOUR support/obstruction channels, not
    three -- the 5th/9th pair was a real gap in the original 3-channel
    engine, fixed here."""
    assert (5, 9) in CHANNELS
    assert len(CHANNELS) == 4


def test_reference_houses_include_9_for_verse18_trikona_check():
    assert 9 in REFERENCE_HOUSES


def test_every_channel_has_a_counter_channel():
    counter_offsets = {c[1] for c in CHANNELS}
    assert counter_offsets == {12, 10, 3, 9}


def test_practical_argala_runs_for_every_fixture_and_exposes_composites():
    for chart_id in list_fixture_ids():
        ctx = _ctx(chart_id)
        result = practical_argala(ctx)
        assert result["model"] == "house_argala_v2"
        assert set(result["houses"].keys()) >= set(REFERENCE_HOUSES)
        assert "raja_yoga_via_argala" in result
        assert "fame_via_argala" in result
        for house_data in result["houses"].values():
            assert len(house_data["channels"]) == 4
            assert house_data["verdict"] in ("supportive", "obstructive", "mixed")


def test_classical_effect_text_present_for_every_reference_house():
    ctx = _ctx("ajay_kumar")
    result = practical_argala(ctx)
    for house in REFERENCE_HOUSES:
        assert result["houses"][house]["classical_effect"] is not None


def test_vipareeta_argala_flag_only_fires_with_3_or_more_malefics_in_the_3rd_counter_house():
    """Synthetic sanity check on the vipareeta detection logic itself,
    independent of any real fixture happening to have this rare condition."""
    from app.derived.interventions import _compute_house_argala

    chart = {p: {"house": 1} for p in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]}
    # Put 3 malefics in house 3 (the counter house for the 11th-house channel, reference=1).
    chart["Sun"]["house"] = 3
    chart["Mars"]["house"] = 3
    chart["Saturn"]["house"] = 3
    shadbala = {p: {"total_score": 50.0} for p in chart}
    result = _compute_house_argala(1, chart, shadbala, [])
    eleven_three_channel = next(c for c in result["channels"] if c["counter_house"] == 3)
    assert eleven_three_channel["vipareeta_argala"] is True
    assert eleven_three_channel["status"] == "vipareeta_favorable"


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
