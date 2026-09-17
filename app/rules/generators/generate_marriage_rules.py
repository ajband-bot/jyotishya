"""Generator: Marriage rules (40) -- build_plan.md Phase 6.

Wraps app.derived.marriage_analysis's Five-Pillar synthesis into v2 Rule
schema entries, per the same "wrap already-computed logic" pattern as
generate_dosha_rules.py. Three families, cross-producted mechanically
(not 40 hand-authored blurbs):

  MAR-7L-01..12   (12): 7th lord placed in house 1-12 -- marriage
                        trajectory (Pillar 2). Reuses the already-computed
                        `lord_placements.7.occupies_house` field.
  MAR-VEN-01..12  (12): Venus (male-native marriage karaka) in house
                        1-12 -- spouse-quality angle (Pillar 3).
  MAR-JUP-01..12  (12): Jupiter (female-native marriage karaka) in house
                        1-12 -- spouse-quality angle (Pillar 3).
  MAR-DK-<STATE>   (4): Darakaraka's D1 dignity state -- marriage-quality
                        signal (Pillar 4). Fires on the DYNAMIC
                        `marriage_analysis.darakaraka.d1_dignity_state`
                        field (correct regardless of which literal planet
                        ends up being DK for a given chart).

Total: 12 + 12 + 12 + 4 = 40.

Run: .venv/bin/python -m app.rules.generators.generate_marriage_rules
"""
from __future__ import annotations

from pathlib import Path

import yaml

OUTPUT_PATH = Path(__file__).resolve().parents[1] / "compiled" / "marriage_v2.yaml"


def _ordinal(n: int) -> str:
    suffix = "th" if 11 <= n % 100 <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


def _seventh_lord_rules() -> list[dict]:
    rules = []
    for house in range(1, 13):
        rules.append({
            "id": f"MAR-7L-{house:02d}",
            "title": f"7th Lord (marriage significator) placed in House {house}",
            "category": "marriage",
            "source_tier": 3,
            "source_ref": "docs/domain-playbooks.md Marriage Five-Pillar Framework, Pillar 2; BPHS Ch.11",
            "tradition": "parasari",
            "conditions": [
                {"path": "lord_placements.7.occupies_house", "op": "eq", "value": house,
                 "description": f"7th lord occupies House {house}"},
            ],
            "outputs": [
                {"kind": "classification", "payload": {
                    "house": house,
                    "effect": f"The 7th lord's placement in the {_ordinal(house)} house routes marriage matters through that house's affairs -- the native's path to a stable married life runs through House {house}'s themes.",
                }},
            ],
            "confidence": "medium", "status": "ACTIVE", "computation_model": "practical_proxy",
            "notes": ["Wraps app.derived.marriage_analysis.seventh_lord_report via lord_placements.7 -- lagna-agnostic by design."],
        })
    return rules


def _karaka_rules(planet: str, code: str, applies_to: str) -> list[dict]:
    rules = []
    for house in range(1, 13):
        rules.append({
            "id": f"MAR-{code}-{house:02d}",
            "title": f"{planet} (marriage karaka, {applies_to} native) in House {house}",
            "category": "marriage",
            "source_tier": 4,
            "source_ref": "docs/domain-playbooks.md Marriage Five-Pillar Framework, Pillar 3; Marriage_Guide_Part1.md",
            "tradition": "parasari",
            "conditions": [
                {"path": f"chart.{planet}.house", "op": "eq", "value": house,
                 "description": f"{planet} occupies House {house}"},
            ],
            "outputs": [
                {"kind": "classification", "payload": {
                    "planet": planet, "house": house, "applies_to_native_gender": applies_to,
                    "effect": f"As the marriage karaka for a {applies_to} native, {planet} in House {house} concentrates the spouse/partnership theme there -- distinct from {planet}'s own generic house-{house} significations.",
                }},
            ],
            "confidence": "medium", "status": "ACTIVE", "computation_model": "practical_proxy",
            "notes": [f"Karaka-lens reading, distinct from the generic PIH-{code} planet-in-house rule (different interpretive angle, not a duplicate)."],
        })
    return rules


DK_DIGNITY_EFFECTS = {
    "exalted": "Darakaraka exalted in D1 -- a strong, elevating signal for spouse quality and marital fortune.",
    "own-sign": "Darakaraka in its own sign in D1 -- a stable, self-assured signal for spouse quality.",
    "neutral": "Darakaraka in a neutral D1 dignity -- spouse quality is average, more dependent on other pillars.",
    "debilitated": "Darakaraka debilitated in D1 -- a genuine strain signal for spouse quality, per Cardinal Rule 9 (never sugarcoat), though see Neechabhanga checks before finalizing.",
}


def _darakaraka_rules() -> list[dict]:
    rules = []
    for state, effect in DK_DIGNITY_EFFECTS.items():
        rules.append({
            "id": f"MAR-DK-{state.upper().replace('-', '_')}",
            "title": f"Darakaraka D1 dignity: {state}",
            "category": "marriage",
            "source_tier": 3,
            "source_ref": "docs/domain-playbooks.md Marriage Five-Pillar Framework, Pillar 4 (Jaimini Darakaraka)",
            "tradition": "jaimini",
            "conditions": [
                {"path": "marriage_analysis.darakaraka.d1_dignity_state", "op": "eq", "value": state,
                 "description": f"Darakaraka's D1 dignity is {state}"},
            ],
            "outputs": [
                {"kind": "classification", "payload": {"dignity_state": state, "effect": effect}},
            ],
            "confidence": "medium", "status": "ACTIVE", "computation_model": "practical_proxy",
            "notes": ["Fires on the dynamic marriage_analysis.darakaraka field -- correct regardless of which literal planet is DK for a given chart."],
        })
    return rules


def build_rules() -> list[dict]:
    return _seventh_lord_rules() + _karaka_rules("Venus", "VEN", "male") + _karaka_rules("Jupiter", "JUP", "female") + _darakaraka_rules()


def main() -> None:
    rules = build_rules()
    assert len(rules) == 40, f"expected 40 marriage rules, got {len(rules)}"
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as handle:
        yaml.safe_dump(rules, handle, allow_unicode=True, sort_keys=False, default_flow_style=False)
    print(f"Wrote {len(rules)} rules to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
