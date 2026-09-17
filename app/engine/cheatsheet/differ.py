"""Differ engine for the Cheat-Sheet Cross-Validation Console.

Runs each extracted ClaimRecord against computed truth:
- house_ownership claims -> recompute house_lord() for the claimed Lagna and
  compare against every claimed house.
- coverage claims -> check whether app.derived.doshas actually defines the
  referenced function (this is how docs/dosha-registry.md's 6 mandatory
  doshas were confirmed to have ZERO code before this session, and all 6
  present after app/derived/doshas.py was added).

Verdicts follow the spec's fixed vocabulary: match / mismatch / unverifiable
/ data_gap. Never silently reconciled -- a mismatch stays a mismatch until a
human re-audits the source document (docs/technical-architecture.md 4.4).
"""
from __future__ import annotations

import app.derived.doshas as doshas_module
from app.derived.factors import house_lord
from app.engine.cheatsheet.models import ClaimRecord, ValidationResult


def _validate_house_ownership_claim(claim: ClaimRecord) -> ValidationResult:
    if claim.lagna_sign is None or claim.planet is None or not claim.claimed_houses:
        return ValidationResult(
            claim=claim,
            verdict="unverifiable",
            diff_detail="Could not parse a complete (lagna, planet, houses) triple from this claim.",
        )

    computed_houses = [h for h in range(1, 13) if house_lord(claim.lagna_sign, h) == claim.planet]
    claimed_set = set(claim.claimed_houses)
    computed_set = set(computed_houses)

    if claimed_set == computed_set:
        return ValidationResult(
            claim=claim,
            computed_value={"planet": claim.planet, "houses_owned": computed_houses},
            verdict="match",
            diff_detail="Claimed houses match computed whole-sign lordship exactly.",
        )

    # Partial overlap still counts as mismatch -- spec explicitly prohibits
    # silent reconciliation of partial agreement.
    return ValidationResult(
        claim=claim,
        computed_value={"planet": claim.planet, "houses_owned": computed_houses},
        verdict="mismatch",
        diff_detail=(
            f"Claim says {claim.planet} owns houses {sorted(claimed_set)}, but computed "
            f"whole-sign lordship for this Lagna gives {claim.planet} houses {sorted(computed_set)}. "
            f"Re-audit the source example against BPHS Ch.34 before trusting it."
        ),
    )


def _validate_coverage_claim(claim: ClaimRecord) -> ValidationResult:
    fn_name = claim.formula_ref
    implemented = fn_name is not None and hasattr(doshas_module, fn_name)
    if implemented:
        return ValidationResult(
            claim=claim,
            computed_value={"function": fn_name, "module": "app.derived.doshas"},
            verdict="match",
            diff_detail=f"{claim.section} has a corresponding calculator: doshas.{fn_name}().",
        )
    return ValidationResult(
        claim=claim,
        computed_value=None,
        verdict="data_gap",
        diff_detail=(
            f"{claim.section} is mandated by docs/dosha-registry.md but no calculator "
            f"named '{fn_name}' exists yet -- this dosha can only be checked by hand."
        ),
    )


def _validate_concept_claim(claim: ClaimRecord) -> ValidationResult:
    """Resolve claim.formula_ref as 'module.path:function_name' and confirm
    the callable actually exists -- generalizes _validate_coverage_claim
    (which is hardcoded to app.derived.doshas) to any module in the
    project. A concept documented as `data_gap` with no code_ref (e.g. a
    process rule like the classical-text-hierarchy entry) is expected to
    have formula_ref=None -- that is reported as `data_gap`, not treated as
    a broken claim."""
    import importlib

    from app.engine.cheatsheet.concepts import get_concept

    concept = get_concept(claim.concept_id) if claim.concept_id else None
    if concept is None:
        return ValidationResult(claim=claim, verdict="unverifiable", diff_detail="No matching concept registry entry found.")

    if not concept.code_ref:
        return ValidationResult(
            claim=claim,
            computed_value=None,
            verdict="data_gap",
            diff_detail=f"{concept.concept_id} has no code_ref (documentation/process concept, not a calculator) -- expected, not a bug.",
        )

    module_name, _, fn_name = concept.code_ref.partition(":")
    try:
        module = importlib.import_module(module_name)
    except ImportError as exc:
        return ValidationResult(
            claim=claim,
            computed_value=None,
            verdict="mismatch",
            diff_detail=f"Module '{module_name}' failed to import ({exc}) -- registry claims this concept is {concept.quality_label}, but its code_ref is broken.",
        )

    if not hasattr(module, fn_name):
        return ValidationResult(
            claim=claim,
            computed_value=None,
            verdict="mismatch",
            diff_detail=f"'{fn_name}' no longer exists in {module_name} -- concepts.py's registry is stale, a real regression to fix (not silently update the registry to hide it).",
        )

    if concept.quality_label == "data_gap":
        verdict = "data_gap"
        detail = f"{concept.concept_id}'s code_ref resolves, but the registry itself honestly labels this a data_gap -- partial/no real computation yet."
    else:
        verdict = "match"
        detail = f"{concept.concept_id} resolves to a live callable ({concept.code_ref}), quality_label={concept.quality_label}."

    return ValidationResult(
        claim=claim,
        computed_value={"code_ref": concept.code_ref, "quality_label": concept.quality_label},
        verdict=verdict,
        diff_detail=detail,
    )


def validate_claim(claim: ClaimRecord) -> ValidationResult:
    if claim.claim_type == "house_ownership":
        return _validate_house_ownership_claim(claim)
    if claim.claim_type == "coverage":
        return _validate_coverage_claim(claim)
    if claim.claim_type == "concept_coverage":
        return _validate_concept_claim(claim)
    return ValidationResult(claim=claim, verdict="unverifiable", diff_detail="Unknown claim_type.")


def validate_claims(claims: list[ClaimRecord]) -> list[ValidationResult]:
    return [validate_claim(c) for c in claims]
