"""Unit tests for build_plan.md Phase 4: yoga detection engine
(app.derived.yogas). Cross-checks against the Phase 3 composer-vs-LLM diff
finding (ajay_kumar's Ruchaka Mahapurusha Yoga, which the LLM reading
correctly identified but no compiled rule could render at the time).
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.derived.factors import build_chart_context
from app.derived.yogas import (
    check_adhi_yoga,
    check_amala_yoga,
    check_budha_aditya_yoga,
    check_chandra_mangala_yoga,
    check_durudhara_yoga,
    check_gajakesari_yoga,
    check_graha_yuddha,
    check_kahala_yoga,
    check_kendradhipati_dosha,
    check_lakshmi_yoga,
    check_neechabhanga_raja_yoga,
    check_pancha_mahapurusha_yogas,
    check_parivartana_yoga,
    check_shankha_yoga,
    check_sunapha_yoga,
    check_vasumati_yoga,
    check_viparita_raja_yoga,
    compute_all_yogas,
)
from app.fixtures import list_fixture_ids, load_chart_fixture


def _ctx(fixture_id: str):
    return build_chart_context(load_chart_fixture(fixture_id))


def test_compute_all_yogas_returns_18_keys_for_every_fixture():
    expected_keys = {
        "gajakesari", "sunapha", "anapha", "durudhara", "chandra_mangala", "adhi_yoga",
        "budha_aditya", "pancha_mahapurusha", "neechabhanga_raja_yoga", "parivartana",
        "kendradhipati_dosha", "viparita_raja_yoga", "graha_yuddha", "kahala", "shankha",
        "lakshmi", "vasumati", "amala",
    }
    for fixture_id in list_fixture_ids():
        result = compute_all_yogas({
            "chart": _ctx(fixture_id)["chart"],
            "lagna_sign": _ctx(fixture_id)["lagna_sign"],
            "functional_nature": _ctx(fixture_id)["functional_nature"],
        })
        assert set(result.keys()) == expected_keys


def test_ruchaka_mahapurusha_yoga_matches_phase3_llm_diff_finding_for_ajay():
    """docs/phase3-composer-vs-llm-diff.md: ajay_kumar's Mars is own-sign
    (Scorpio) in Kendra (H1) -- Ruchaka Mahapurusha Yoga, exactly as the
    existing LLM-authored reading identified."""
    ctx = _ctx("ajay_kumar")
    result = check_pancha_mahapurusha_yogas({"chart": ctx["chart"]})
    assert result["planets"]["Mars"]["present"] is True
    assert result["planets"]["Mars"]["yoga_name"] == "Ruchaka"


def test_gajakesari_yoga_kendra_from_moon():
    ctx = _ctx("ajay_kumar")
    result = check_gajakesari_yoga({"chart": ctx["chart"]})
    moon_house = ctx["chart"]["Moon"]["house"]
    jupiter_house = ctx["chart"]["Jupiter"]["house"]
    from app.derived.aspects import KENDRA
    expected = (((jupiter_house - moon_house) % 12) + 1) in KENDRA
    assert result["present"] == expected


def test_sunapha_anapha_durudhara_are_mutually_consistent():
    for fixture_id in list_fixture_ids():
        chart = _ctx(fixture_id)["chart"]
        sunapha = check_sunapha_yoga({"chart": chart})
        durudhara = check_durudhara_yoga({"chart": chart})
        if durudhara["present"]:
            assert sunapha["present"] is True


def test_chandra_mangala_yoga_moon_mars_same_house():
    for fixture_id in list_fixture_ids():
        chart = _ctx(fixture_id)["chart"]
        result = check_chandra_mangala_yoga({"chart": chart})
        assert result["present"] == (chart["Moon"]["house"] == chart["Mars"]["house"])


def test_budha_aditya_orb_under_14_degrees_when_present():
    for fixture_id in list_fixture_ids():
        chart = _ctx(fixture_id)["chart"]
        result = check_budha_aditya_yoga({"chart": chart})
        if result["present"]:
            assert result["orb_deg"] < 14


def test_neechabhanga_cancellation_lord_always_in_kendra_when_present():
    for fixture_id in list_fixture_ids():
        ctx = _ctx(fixture_id)
        result = check_neechabhanga_raja_yoga({"chart": ctx["chart"]})
        from app.derived.aspects import KENDRA
        for cancellation in result["cancellations"]:
            assert cancellation["dispositor_house"] in KENDRA


def test_parivartana_classification_never_contradicts_raw_mutual_reception_evidence():
    from app.derived.dispositors import detect_mutual_receptions

    for fixture_id in list_fixture_ids():
        ctx = _ctx(fixture_id)
        raw_pairs = detect_mutual_receptions(ctx["chart"])
        result = check_parivartana_yoga({"chart": ctx["chart"], "lagna_sign": ctx["lagna_sign"]})
        assert result["present"] == bool(raw_pairs)
        assert len(result["exchanges"]) == len(raw_pairs)


def test_kendradhipati_dosha_wrapper_agrees_with_functional_nature_directly():
    for fixture_id in list_fixture_ids():
        ctx = _ctx(fixture_id)
        result = check_kendradhipati_dosha({"functional_nature": ctx["functional_nature"]})
        expected = [p for p, d in ctx["functional_nature"]["planets"].items() if d["classification"] == "kendradhipati_dosha"]
        assert result["planets"] == expected


def test_viparita_raja_yoga_three_subtypes_present():
    for fixture_id in list_fixture_ids():
        ctx = _ctx(fixture_id)
        result = check_viparita_raja_yoga({"chart": ctx["chart"], "lagna_sign": ctx["lagna_sign"]})
        assert set(result["subtypes"].keys()) == {"harsha", "sarala", "vimala"}


def test_graha_yuddha_excludes_sun_and_moon():
    for fixture_id in list_fixture_ids():
        ctx = _ctx(fixture_id)
        result = check_graha_yuddha({"chart": ctx["chart"]})
        for war in result["wars"]:
            assert "Sun" not in war["planets"]
            assert "Moon" not in war["planets"]


def test_kahala_shankha_lakshmi_vasumati_amala_run_without_error_on_every_fixture():
    for fixture_id in list_fixture_ids():
        ctx = _ctx(fixture_id)
        base_ctx = {"chart": ctx["chart"], "lagna_sign": ctx["lagna_sign"]}
        for fn in (check_kahala_yoga, check_shankha_yoga, check_lakshmi_yoga, check_vasumati_yoga, check_amala_yoga):
            result = fn(base_ctx)
            assert "present" in result and "citation" in result


def test_yogas_wired_into_chart_context():
    ctx = _ctx("ajay_kumar")
    assert "yogas" in ctx
    assert ctx["yogas"]["pancha_mahapurusha"]["planets"]["Mars"]["present"] is True


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
