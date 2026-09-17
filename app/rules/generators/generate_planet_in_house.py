"""Generator: Planet-in-House rules (108 = 9 planets x 12 houses).

Compiles app.knowledge.planets.PLANET_IN_HOUSE (v1 prose, already cited
Saravali Ch.7-15 + BPHS Ch.24-32 at module level) into v2 Rule Engine
schema entries, per build_plan.md §3.2's compilation workflow and §3.3's
sequencing (planet-in-house/sign first -- every other rule set quotes
these atomic building blocks).

Run: .venv/bin/python -m app.rules.generators.generate_planet_in_house
"""
from __future__ import annotations

from pathlib import Path

import yaml

from app.knowledge.planets import PLANET_IN_HOUSE

OUTPUT_PATH = Path(__file__).resolve().parents[1] / "compiled" / "planet_in_house_v2.yaml"

PLANET_CODES = {
    "Sun": "SUN", "Moon": "MOO", "Mars": "MAR", "Mercury": "MER", "Jupiter": "JUP",
    "Venus": "VEN", "Saturn": "SAT", "Rahu": "RAH", "Ketu": "KET",
}


def build_rules() -> list[dict]:
    rules = []
    for planet, by_house in PLANET_IN_HOUSE.items():
        code = PLANET_CODES[planet]
        for house, effect_text in sorted(by_house.items()):
            rules.append({
                "id": f"PIH-{code}-{house:02d}",
                "title": f"{planet} in House {house}",
                "category": "bhava_signification",
                "source_tier": 1,
                "source_ref": "Saravali Ch.7-15 + BPHS Ch.24-32 (as cited in app.knowledge.planets.PLANET_IN_HOUSE)",
                "tradition": "parasari",
                "conditions": [
                    {"path": f"chart.{planet}.house", "op": "eq", "value": house,
                     "description": f"{planet} occupies House {house}"},
                ],
                "outputs": [
                    {"kind": "classification", "payload": {"planet": planet, "house": house, "effect": effect_text}},
                ],
                "confidence": "medium",
                "status": "ACTIVE",
                "computation_model": "classical",
                "notes": [
                    "Migrated from app.knowledge.planets.PLANET_IN_HOUSE (v1 prose dict) per build_plan.md \u00a73.2 workflow.",
                    "Source cited at module level (Saravali Ch.7-15, BPHS Ch.24-32); confidence stays 'medium' pending a "
                    "per-entry re-verification pass directly against the primary PDFs (tracked as a follow-up enrichment "
                    "task, not a blocker for ACTIVE status -- the content is not fabricated, just not yet chapter/verse-"
                    "pinned per individual entry).",
                ],
            })
    return rules


def main() -> None:
    rules = build_rules()
    assert len(rules) == 108, f"expected 108 planet-in-house rules, got {len(rules)}"
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as handle:
        yaml.safe_dump(rules, handle, allow_unicode=True, sort_keys=False, default_flow_style=False)
    print(f"Wrote {len(rules)} rules to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
