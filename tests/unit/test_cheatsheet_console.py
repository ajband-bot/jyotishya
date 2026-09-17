"""Unit tests for the Cheat-Sheet Cross-Validation Console
(app/engine/cheatsheet/) -- extractor + differ pipeline."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.engine.cheatsheet.differ import validate_claim, validate_claims
from app.engine.cheatsheet.extractor import (
    extract_all_claims,
    extract_dosha_coverage_claims,
    extract_rule_card_claims,
)
from app.engine.cheatsheet.models import ClaimRecord


def test_extract_rule_card_claims_finds_rc001_examples():
    claims = extract_rule_card_claims()
    assert len(claims) >= 2
    assert all(c.formula_ref == "RC-001" for c in claims)


def test_rc001_ajay_example_resolves_to_ajay_kumar_chart():
    claims = extract_rule_card_claims()
    ajay_claims = [c for c in claims if c.applies_to_chart == "ajay_kumar"]
    assert len(ajay_claims) == 1
    assert ajay_claims[0].planet == "Saturn"
    assert set(ajay_claims[0].claimed_houses) == {7, 8}


def test_rc001_sandeep_example_matches_computed_lordship():
    claims = extract_rule_card_claims()
    sandeep_claim = next(c for c in claims if c.applies_to_chart == "sandeep_0700")
    result = validate_claim(sandeep_claim)
    assert result.verdict == "match"


def test_rc001_ajay_example_is_a_known_mismatch():
    claims = extract_rule_card_claims()
    ajay_claim = next(c for c in claims if c.applies_to_chart == "ajay_kumar")
    result = validate_claim(ajay_claim)
    assert result.verdict == "mismatch"
    assert result.computed_value["houses_owned"] == [3, 4]


def test_dosha_coverage_claims_all_match_after_doshas_module_added():
    """8 claims since build_plan.md Phase 4's registry recheck added Ghata
    and Shrapit to docs/dosha-registry.md (was 6 before that recheck)."""
    claims = extract_dosha_coverage_claims()
    assert len(claims) == 8
    results = validate_claims(claims)
    assert all(r.verdict == "match" for r in results)


def test_unknown_coverage_target_is_a_data_gap():
    fake_claim = ClaimRecord(
        claim_id="FAKE-1",
        source_file="docs/fake.md",
        section="Nonexistent Dosha",
        claim_text="test",
        formula_ref="check_nonexistent_dosha",
        claim_type="coverage",
    )
    result = validate_claim(fake_claim)
    assert result.verdict == "data_gap"


def test_extract_all_claims_combines_both_extractors():
    claims = extract_all_claims()
    assert any(c.claim_type == "house_ownership" for c in claims)
    assert any(c.claim_type == "coverage" for c in claims)


def test_house_ownership_claim_missing_data_is_unverifiable():
    incomplete_claim = ClaimRecord(
        claim_id="INCOMPLETE-1",
        source_file="test",
        section="test",
        claim_text="test",
        claim_type="house_ownership",
        lagna_sign=None,
        planet="Mars",
        claimed_houses=[1],
    )
    result = validate_claim(incomplete_claim)
    assert result.verdict == "unverifiable"


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
