"""Lagna-balanced regression dataset audit (build_plan.md Phase 2 item 10,
first half).

This module does NOT fabricate charts to fill gaps -- Cardinal Rule 2
forbids inventing a native to make a coverage number look better. Instead
it reports, honestly and mechanically, which of the 12 Lagna signs the
CURRENT fixture set (`data/charts/*.yaml`) actually exercises, and which
functional-nature classifications (`app.derived.functional_nature`) are
exercised by at least one real fixture -- both are real regression-quality
signals, and both are allowed to show gaps. Filling a gap means adding a
REAL native's chart to `data/charts/`, not synthesizing one.

Historical-event validation (build_plan.md item 10, second half) is
deliberately NOT implemented as code here: it requires real, user-supplied
biographical event dates per native, which do not exist anywhere in this
repo today (`data/charts/*.yaml` carries no `events` field, confirmed by a
direct grep before writing this module). Inventing plausible-sounding life
events to "validate" against would be exactly the fabrication Cardinal
Rule 2 exists to prevent. See docs/historical-event-validation-protocol.md
for the honest, not-yet-executable protocol this is deferred to.
"""
from __future__ import annotations

from typing import Any, Callable

from app.astro.constants import SIGNS

ALL_SIGNS = list(range(1, 13))


def lagna_coverage_report(fixture_ids: list[str], context_builder: Callable[[str], dict[str, Any]]) -> dict[str, Any]:
    by_sign: dict[int, list[str]] = {sign: [] for sign in ALL_SIGNS}
    for fixture_id in fixture_ids:
        ctx = context_builder(fixture_id)
        by_sign[ctx["lagna_sign"]].append(fixture_id)

    covered = {sign for sign, fixtures in by_sign.items() if fixtures}
    missing = sorted(set(ALL_SIGNS) - covered)
    return {
        "by_sign": {SIGNS[sign - 1]["en"]: fixtures for sign, fixtures in by_sign.items()},
        "covered_signs": sorted(SIGNS[s - 1]["en"] for s in covered),
        "missing_signs": [SIGNS[s - 1]["en"] for s in missing],
        "is_fully_balanced": not missing,
        "total_fixtures": len(fixture_ids),
        "distinct_lagna_signs_covered": len(covered),
    }


def functional_nature_classification_coverage(
    fixture_ids: list[str], context_builder: Callable[[str], dict[str, Any]]
) -> dict[str, Any]:
    """Which functional-nature classifications (functional_malefic,
    functional_benefic, yoga_karaka, kendradhipati_dosha,
    functional_benefic_with_dusthana_mitigation, neutral) are actually
    exercised by at least one real fixture -- a regression-quality signal
    distinct from raw Lagna-sign coverage, since two different Lagnas can
    still fail to exercise the same rare classification."""
    seen: dict[str, list[str]] = {}
    for fixture_id in fixture_ids:
        ctx = context_builder(fixture_id)
        for planet, data in ctx["functional_nature"]["planets"].items():
            classification = data["classification"]
            seen.setdefault(classification, []).append(f"{fixture_id}:{planet}")

    all_known_classifications = {
        "functional_malefic", "functional_benefic", "yoga_karaka",
        "kendradhipati_dosha", "functional_benefic_with_dusthana_mitigation", "neutral",
    }
    missing = sorted(all_known_classifications - set(seen))
    return {
        "exercised": {classification: examples for classification, examples in seen.items()},
        "missing_classifications": missing,
        "is_fully_exercised": not missing,
    }
