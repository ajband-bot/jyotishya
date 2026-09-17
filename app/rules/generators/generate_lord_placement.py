"""Generator: House-Lord-to-Destination-House rules (144 = 12x12).

build_plan.md Phase 2 item 1 / RC-004 ("Bhava Lord Effects: Lord of X in
Y"). Unlike planet-in-house (which fires on a fixed planet), this rule set
fires on a computed, lagna-agnostic field: `lord_placements.<source>
.occupies_house` (wired into app.derived.factors.build_chart_context).
This is deliberately how BPHS itself teaches bhava-lord effects -- "the
lord of the Nth house placed in the Mth house" is a relationship between
HOUSES, not a fixed planet-to-house fact, so the same 144 rules apply
unmodified regardless of which Lagna (and therefore which literal planet)
occupies the lord role for a given chart.

No direct verse exists for all 144 combinations in any single source we
hold (BPHS/Phaladeepika discuss a worked subset, not an exhaustive table).
Rather than fabricate 144 individual citations, this generator applies
BPHS's own well-documented derivation method: combine the SOURCE house's
signification (whose affairs are at stake) with the DESTINATION house's
signification and classical nature (kendra/trikona/dusthana/upachaya) --
see app.knowledge.houses.HOUSES / house_nature(). Every rule is tagged
`computation_model: practical_proxy` so the generic evaluator honestly
reports `computed_simplified`, never silently claiming full per-combination
verse-citation depth (Cardinal Rule 4/9).

Run: .venv/bin/python -m app.rules.generators.generate_lord_placement
"""
from __future__ import annotations

from pathlib import Path

import yaml

from app.knowledge.houses import HOUSES, house_nature

OUTPUT_PATH = Path(__file__).resolve().parents[1] / "compiled" / "lord_placement_v2.yaml"


def _ordinal(n: int) -> str:
    suffix = "th" if 11 <= n % 100 <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


def _effect_text(source: int, dest: int) -> str:
    src = HOUSES[source]
    dst = HOUSES[dest]
    nature = house_nature(dest).split(" ")[0]  # strip the Telugu parenthetical, keep e.g. "kendra"
    if source == dest:
        return (
            f"Lord of the {_ordinal(source)} house ({src['en']}) sits in its own house -- "
            f"a self-supporting placement that concentrates {src['en'].lower()} matters directly in their own domain, "
            f"without needing to be routed through another house's affairs."
        )
    return (
        f"Lord of the {_ordinal(source)} house ({src['en']}) is placed in the {_ordinal(dest)} house "
        f"({dst['en']}, a {nature} house). {src['en']} matters are expressed through, gained via, or tested by "
        f"{dst['en'].lower()} themes -- the native's path to {src['en'].lower()} runs through {dst['en'].lower()} affairs."
    )


def build_rules() -> list[dict]:
    rules = []
    for source in range(1, 13):
        for dest in range(1, 13):
            rules.append({
                "id": f"LPH-{source:02d}-{dest:02d}",
                "title": f"Lord of House {source} in House {dest}",
                "category": "lord_placement",
                "source_tier": 3,
                "source_ref": (
                    "Compositional synthesis of BPHS Ch.11 / Saravali Ch.4 / Phaladeepika Ch.7 house significations "
                    "(see app.knowledge.houses.HOUSES) via BPHS's own source-house + destination-house combination "
                    "method; not a per-combination direct verse citation."
                ),
                "tradition": "parasari",
                "conditions": [
                    {"path": f"lord_placements.{source}.occupies_house", "op": "eq", "value": dest,
                     "description": f"Lord of House {source} occupies House {dest}"},
                ],
                "outputs": [
                    {"kind": "classification", "payload": {
                        "source_house": source, "dest_house": dest, "effect": _effect_text(source, dest),
                    }},
                ],
                "confidence": "medium",
                "status": "ACTIVE",
                "computation_model": "practical_proxy",
                "notes": [
                    "This rule is lagna-agnostic by design -- it fires on the computed lord_placements field, "
                    "not on any fixed planet, so it applies identically regardless of which planet ends up ruling "
                    "House {0} for a given chart.".format(source),
                    "computation_model=practical_proxy -> generic evaluator reports quality=computed_simplified "
                    "even when the condition matches cleanly (build_plan.md Phase 2 item 1).",
                ],
            })
    return rules


def main() -> None:
    rules = build_rules()
    assert len(rules) == 144, f"expected 144 lord-placement rules, got {len(rules)}"
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as handle:
        yaml.safe_dump(rules, handle, allow_unicode=True, sort_keys=False, default_flow_style=False)
    print(f"Wrote {len(rules)} rules to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
