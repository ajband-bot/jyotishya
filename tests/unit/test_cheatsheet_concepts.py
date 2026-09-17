"""Unit tests for the Phase 7 concept registry
(app.engine.cheatsheet.concepts) -- the "learning platform" cheat sheet's
data source. Guards against the registry silently drifting from the code
it describes (a stale code_ref is a real regression, not a documentation
nit -- see app.engine.cheatsheet.differ._validate_concept_claim).
"""
from __future__ import annotations

import importlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.engine.cheatsheet.concepts import CONCEPTS, concepts_by_category, get_concept
from app.engine.cheatsheet.differ import validate_claims
from app.engine.cheatsheet.extractor import extract_concept_claims

ALLOWED_QUALITY_LABELS = {"computed", "computed_simplified", "computed_with_conflict", "data_gap"}


def test_every_concept_has_required_fields():
    for entry in CONCEPTS:
        assert entry.concept_id, "concept_id must not be empty"
        assert entry.category, f"{entry.concept_id} missing category"
        assert entry.english_gloss, f"{entry.concept_id} missing english_gloss"
        assert entry.classical_definition, f"{entry.concept_id} missing classical_definition"
        assert entry.primary_citation, f"{entry.concept_id} missing primary_citation"
        assert entry.quality_label in ALLOWED_QUALITY_LABELS, (
            f"{entry.concept_id} has an unsanctioned quality_label: {entry.quality_label}"
        )


def test_concept_ids_are_unique():
    ids = [entry.concept_id for entry in CONCEPTS]
    assert len(ids) == len(set(ids)), "duplicate concept_id found in CONCEPTS"


def test_get_concept_lookup_works():
    assert get_concept("mangal_dosha") is not None
    assert get_concept("does_not_exist") is None


def test_concepts_by_category_covers_every_entry():
    grouped = concepts_by_category()
    total = sum(len(v) for v in grouped.values())
    assert total == len(CONCEPTS)


def test_every_code_ref_that_exists_actually_resolves():
    """The registry's own honesty claim: if code_ref is set, the module
    must import and the function/attribute must exist. This is the same
    check the differ runs live -- duplicated here as a fast, DB-free unit
    test so a stale code_ref fails CI immediately, not just the console."""
    for entry in CONCEPTS:
        if not entry.code_ref:
            continue
        module_name, _, fn_name = entry.code_ref.partition(":")
        module = importlib.import_module(module_name)
        assert hasattr(module, fn_name), (
            f"{entry.concept_id}: '{fn_name}' does not exist in {module_name} -- "
            f"stale code_ref, fix the registry entry or the code, don't ignore this."
        )


def test_concept_claims_all_validate_to_match_or_honest_data_gap():
    """No concept_coverage claim should ever come back 'mismatch' in a
    clean tree -- that would mean the registry documents a calculator that
    doesn't actually exist. A 'data_gap' verdict is fine (it just means the
    registry is honestly labeling something incomplete)."""
    results = validate_claims(extract_concept_claims())
    mismatches = [r for r in results if r.verdict == "mismatch"]
    assert not mismatches, f"stale concept registry entries: {[r.claim.concept_id for r in mismatches]}"


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
