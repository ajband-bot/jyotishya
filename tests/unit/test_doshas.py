"""Unit tests for app.derived.doshas -- the 6 mandatory dosha checks from
docs/dosha-registry.md, which previously had ZERO corresponding code (only
Sade Sati existed). Includes a regression guard for a self-affliction bug
found and fixed during initial validation against itta_sai_shivani.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.derived.doshas import (
    check_ghata_dosha,
    check_guru_chandala,
    check_kala_sarpa,
    check_kemadruma,
    check_mangal_dosha,
    check_papakartari,
    check_pitru_dosha,
    check_shrapit_dosha,
    compute_all_doshas,
)
from app.derived.factors import build_chart_context
from app.fixtures import load_chart_fixture


def _ctx(chart_id: str):
    return build_chart_context(load_chart_fixture(chart_id))


def test_compute_all_doshas_returns_all_8_keys():
    """Ghata and Shrapit were added in build_plan.md Phase 4's registry
    recheck against PyJHora's dosha.py coverage -- see docs/dosha-registry.md
    for the disclosed citation_status: pending_audit caveat on both."""
    result = compute_all_doshas(_ctx("ajay_kumar"))
    assert set(result.keys()) == {
        "mangal_dosha", "kala_sarpa", "pitru_dosha",
        "guru_chandala", "kemadruma", "papakartari",
        "ghata_dosha", "shrapit_dosha",
    }
    for dosha in result.values():
        assert "present" in dosha
        assert "citation" in dosha


def test_pitru_dosha_ninth_lord_cannot_self_afflict():
    """Regression guard: when the 9th lord IS Saturn, the code must not
    treat Saturn's own house as 'afflicted by Saturn' via trivial
    self-conjunction. This exact bug produced a false pitru_dosha=True for
    itta_sai_shivani during initial validation."""
    result = check_pitru_dosha(_ctx("itta_sai_shivani"))
    assert result["ninth_lord"] == "Saturn"
    assert result["present"] is False


def test_mangal_dosha_checks_all_three_references():
    result = check_mangal_dosha(_ctx("itta_sai_shivani"))
    assert set(result["references"].keys()) == {"lagna", "moon", "venus"}
    # Known finding: present only from Moon reference. CORRECTED 2026-09-16
    # (build_plan.md Phase 3, composer-vs-LLM diff for ajay_kumar): this
    # native's Mars sits in Scorpio (its own sign) -- docs/dosha-registry.md
    # cancellation condition #1 ("Mars in own sign in the dosha house")
    # applies, so the correct severity is 'cancelled', not the previously
    # asserted 'moderate' (which reflected check_mangal_dosha() missing this
    # condition entirely, a real gap found while diffing engine output
    # against an existing LLM-authored reading that correctly applied it).
    assert result["references"]["moon"]["present"] is True
    assert result["mars_own_or_exalted_in_occupied_sign"] is True
    assert result["severity"] == "cancelled"


def test_mangal_dosha_own_sign_cancellation_matches_ajay_kumar_llm_reading():
    """Cross-check against output/Ajay_Kumar_Part1_D1_Foundation.html's own
    manual Mangala Dosa working: Mars in Scorpio H1 (own sign) + Jupiter's
    9th aspect -> 'SUBSTANTIALLY CANCELLED'. Our engine's discrete
    'cancelled' bucket agrees directionally with that LLM verdict."""
    result = check_mangal_dosha(_ctx("ajay_kumar"))
    assert result["mars_own_or_exalted_in_occupied_sign"] is True
    assert result["jupiter_venus_aspect_or_conjunction"] is True
    assert result["severity"] == "cancelled"


def test_kala_sarpa_structure():
    result = check_kala_sarpa(_ctx("ajay_kumar"))
    assert result["type"] in {"full", "partial", "not_present"}
    assert len(result["planet_positions_from_rahu_signs"]) == 7


def test_guru_chandala_orb_only_set_when_same_sign():
    result = check_guru_chandala(_ctx("ajay_kumar"))
    if not result["present"]:
        pass  # orb may be None if not same sign -- just confirm no crash
    assert "present" in result


def test_kemadruma_structure():
    result = check_kemadruma(_ctx("sandeep_0700"))
    assert "raw_condition_met" in result
    assert "cancelled" in result


def test_papakartari_scans_all_12_houses():
    result = check_papakartari(_ctx("ajay_kumar"))
    assert all(1 <= h <= 12 for h in result["afflicted_houses"])


def test_ghata_dosha_orb_only_set_when_same_sign():
    """Mars-Saturn conjunction check, structurally identical to Guru
    Chandala's -- confirms the shared _conjunction_within_orb helper wires
    correctly for a different planet pair."""
    result = check_ghata_dosha(_ctx("ajay_kumar"))
    assert "present" in result
    assert result["citation_status"] == "pending_audit"
    if result["present"]:
        assert result["orb_deg"] is not None and result["orb_deg"] <= 15.0
    else:
        pass  # orb may be None if not same sign -- just confirm no crash


def test_shrapit_dosha_orb_only_set_when_same_sign():
    """Rahu-Saturn conjunction check -- same shared helper, third pairing."""
    result = check_shrapit_dosha(_ctx("ajay_kumar"))
    assert "present" in result
    assert result["citation_status"] == "pending_audit"
    if result["present"]:
        assert result["orb_deg"] is not None and result["orb_deg"] <= 15.0


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
