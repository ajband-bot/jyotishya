"""Claim extraction for the Cheat-Sheet Cross-Validation Console.

Two extraction strategies, matched to what's actually structured enough to
extract mechanically:

1. `extract_rule_card_claims()` -- parses the "examples" field of every
   card in bphs_top20_rule_cards_v1.yaml. These are free-text but follow a
   consistent pattern: "Name (SignName lagna): Planet rules H<n>[+H<m>]..."
   or "...is Lagna lord (H1[+H<n>] owner)...". This is the exact pattern
   that caught the RC-001 bug (Ajay/Scorpio/Saturn) -- generalizing that
   catch to every example in the file.

2. `extract_dosha_coverage_claims()` -- parses docs/dosha-registry.md's
   `### <Dosha Name>` headers to produce one coverage claim per dosha the
   registry MANDATES be checked. The differ then checks whether a computed
   calculator actually exists for each one (it didn't, before
   app/derived/doshas.py was added in this same session).
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from app.astro.constants import SIGNS
from app.fixtures import resolve_chart_id_by_name
from app.rules.loader import load_rule_pack
from app.engine.cheatsheet.models import ClaimRecord

REPO_ROOT = Path(__file__).resolve().parents[3]

_SIGN_NAME_TO_ID = {s["en"].lower(): s["id"] for s in SIGNS}

_HEADER_RE = re.compile(r"^([A-Za-z][\w ]*?)\s*\((\w+)\s+lagna\)\s*:\s*(.*)$")
_HOUSE_CLAIM_RE = re.compile(
    r"(\b[A-Z][a-z]+)\s+(?:is Lagna lord\s*\((H1(?:\+H\d+)*)\s*owner\)"
    r"|rules\s+(H\d+(?:\+H\d+)*))"
)


def _parse_house_numbers(house_str: str) -> list[int]:
    return [int(n) for n in re.findall(r"H(\d+)", house_str)]


def extract_rule_card_claims() -> list[ClaimRecord]:
    """Every checkable (Name, Lagna, Planet -> Houses) assertion embedded in
    the rule cards' worked examples."""
    pack = load_rule_pack()
    claims: list[ClaimRecord] = []
    for card in pack.get("rule_cards", []):
        rule_id = card.get("rule_id", "UNKNOWN")
        examples = card.get("card_fields", {}).get("examples", [])
        for idx, example_text in enumerate(examples):
            header_match = _HEADER_RE.match(example_text.strip())
            if not header_match:
                continue
            name, sign_name, remainder = header_match.groups()
            lagna_sign = _SIGN_NAME_TO_ID.get(sign_name.lower())
            chart_id = resolve_chart_id_by_name(name.split()[0])

            for house_idx, house_match in enumerate(_HOUSE_CLAIM_RE.finditer(remainder)):
                planet, lagna_lord_houses, ruled_houses = house_match.groups()
                house_str = lagna_lord_houses or ruled_houses
                houses = _parse_house_numbers(house_str)
                claims.append(
                    ClaimRecord(
                        claim_id=f"{rule_id}-ex{idx}-h{house_idx}",
                        source_file="app/rules/bphs_top20_rule_cards_v1.yaml",
                        section=rule_id,
                        claim_text=example_text.strip(),
                        formula_ref=rule_id,
                        applies_to_chart=chart_id,
                        claim_type="house_ownership",
                        lagna_sign=lagna_sign,
                        planet=planet,
                        claimed_houses=houses,
                    )
                )
    return claims


# Doshas docs/dosha-registry.md mandates, in the order they appear, mapped
# to the function name in app/derived/doshas.py that (should) implement
# each one. Kept here (not auto-parsed from prose headings) because the
# mapping from doc-heading-text to code-symbol-name is an editorial
# decision, not something safe to regex-guess.
_DOSHA_REGISTRY_ITEMS = [
    ("Mangala Dosha (Kuja Dosha)", "check_mangal_dosha"),
    ("Kala Sarpa Dosha", "check_kala_sarpa"),
    ("Pitru Dosha", "check_pitru_dosha"),
    ("Guru Chandala Yoga", "check_guru_chandala"),
    ("Kemadruma Dosha", "check_kemadruma"),
    ("Papakartari Yoga", "check_papakartari"),
    ("Ghata Dosha", "check_ghata_dosha"),
    ("Shrapit Dosha", "check_shrapit_dosha"),
]


def extract_dosha_coverage_claims() -> list[ClaimRecord]:
    """One coverage claim per dosha docs/dosha-registry.md says MUST be
    checked for every chart. Not chart-specific -- these validate that the
    ENGINE has a corresponding calculator at all, independent of any one
    person's results."""
    claims = []
    for idx, (dosha_name, expected_fn) in enumerate(_DOSHA_REGISTRY_ITEMS):
        claims.append(
            ClaimRecord(
                claim_id=f"DOSHA-COVERAGE-{idx}",
                source_file="docs/dosha-registry.md",
                section=dosha_name,
                claim_text=f"docs/dosha-registry.md mandates every Validation Document check {dosha_name}.",
                formula_ref=expected_fn,
                applies_to_chart=None,
                claim_type="coverage",
            )
        )
    return claims


def extract_concept_claims() -> list[ClaimRecord]:
    """One coverage claim per app.engine.cheatsheet.concepts registry entry
    (build_plan.md Phase 7: generalizes the dosha-coverage pattern above to
    the WHOLE project's concept surface -- every classical concept this
    codebase claims to implement gets a live 'does the code_ref still
    exist' check, not just the 8 doshas)."""
    from app.engine.cheatsheet.concepts import CONCEPTS

    claims = []
    for entry in CONCEPTS:
        claims.append(
            ClaimRecord(
                claim_id=f"CONCEPT-{entry.concept_id}",
                source_file="app/engine/cheatsheet/concepts.py",
                section=entry.english_gloss,
                claim_text=(
                    f"{entry.concept_id} ({entry.quality_label}) is implemented at "
                    f"'{entry.code_ref}', per {entry.primary_citation}."
                ),
                formula_ref=entry.code_ref,
                applies_to_chart=None,
                claim_type="concept_coverage",
                concept_id=entry.concept_id,
            )
        )
    return claims


def extract_all_claims() -> list[ClaimRecord]:
    return extract_rule_card_claims() + extract_dosha_coverage_claims() + extract_concept_claims()
