"""Generator: Career rules (30) -- build_plan.md Phase 6.

Wraps app.derived.career_analysis into v2 Rule schema entries, mirroring
the marriage generator's "cross-produced, not hand-authored" discipline:

  CAR-10L-01..12  (12): 10th lord placed in house 1-12 -- career
                        trajectory (docs/domain-playbooks.md 10th Lord row).
  CAR-OCC-<CODE>   (9): occupant of the 10th house -- classical
                        profession-type flavor, one per planet (10th House
                        row). Reuses app.derived.career_analysis's own
                        TENTH_HOUSE_OCCUPANT_PROFESSION table (DRY).
  CAR-LORDIS-<CODE> (7): the 10th lord's IDENTITY (which of the 7
                        classical planets it is) -- career flavor via
                        KARAKATVA's natural professions (only 7 planets
                        can be sign lords; Rahu/Ketu excluded honestly,
                        not force-fit).
  CAR-YK            (1): 10th lord is a yoga-karaka for this Lagna --
                        strongest career-success signal (reuses
                        functional_nature, zero new logic).
  CAR-KD            (1): 10th lord suffers Kendradhipati Dosha (natural
                        benefic ruling kendra-only) -- career purity
                        caveat (reuses functional_nature, zero new logic).

Total: 12 + 9 + 7 + 1 + 1 = 30.

Run: .venv/bin/python -m app.rules.generators.generate_career_rules
"""
from __future__ import annotations

from pathlib import Path

import yaml

from app.derived.career_analysis import TENTH_HOUSE_OCCUPANT_PROFESSION
from app.knowledge.planets import KARAKATVA

OUTPUT_PATH = Path(__file__).resolve().parents[1] / "compiled" / "career_v2.yaml"

PLANET_CODES = {
    "Sun": "SUN", "Moon": "MOO", "Mars": "MAR", "Mercury": "MER", "Jupiter": "JUP",
    "Venus": "VEN", "Saturn": "SAT", "Rahu": "RAH", "Ketu": "KET",
}
CLASSICAL_7 = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]


def _ordinal(n: int) -> str:
    suffix = "th" if 11 <= n % 100 <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


def _tenth_lord_placement_rules() -> list[dict]:
    rules = []
    for house in range(1, 13):
        rules.append({
            "id": f"CAR-10L-{house:02d}",
            "title": f"10th Lord (career significator) placed in House {house}",
            "category": "career",
            "source_tier": 3,
            "source_ref": "docs/domain-playbooks.md Career Analysis Framework, 10th Lord row; BPHS Ch.11",
            "tradition": "parasari",
            "conditions": [
                {"path": "lord_placements.10.occupies_house", "op": "eq", "value": house,
                 "description": f"10th lord occupies House {house}"},
            ],
            "outputs": [
                {"kind": "classification", "payload": {
                    "house": house,
                    "effect": f"The 10th lord's placement in the {_ordinal(house)} house routes career success through that house's affairs.",
                }},
            ],
            "confidence": "medium", "status": "ACTIVE", "computation_model": "practical_proxy",
            "notes": ["Wraps app.derived.career_analysis.tenth_lord_report via lord_placements.10 -- lagna-agnostic by design."],
        })
    return rules


def _occupant_profession_rules() -> list[dict]:
    rules = []
    for planet, text in TENTH_HOUSE_OCCUPANT_PROFESSION.items():
        code = PLANET_CODES[planet]
        rules.append({
            "id": f"CAR-OCC-{code}",
            "title": f"{planet} occupies the 10th house (career profession-type)",
            "category": "career",
            "source_tier": 3,
            "source_ref": "docs/domain-playbooks.md Career Analysis Framework, 10th House row (classical occupant-profession convention)",
            "tradition": "parasari",
            "conditions": [
                {"path": f"chart.{planet}.house", "op": "eq", "value": 10,
                 "description": f"{planet} occupies House 10"},
            ],
            "outputs": [{"kind": "classification", "payload": {"planet": planet, "effect": text}}],
            "confidence": "medium", "status": "ACTIVE", "computation_model": "practical_proxy",
            "notes": ["Distinct interpretive lens from the generic PIH-*-10 planet-in-house rule (profession-TYPE, not general house-10 significations)."],
        })
    return rules


def _lord_identity_rules() -> list[dict]:
    rules = []
    for planet in CLASSICAL_7:
        code = PLANET_CODES[planet]
        professions = KARAKATVA[planet]["professions"]
        rules.append({
            "id": f"CAR-LORDIS-{code}",
            "title": f"10th Lord IS {planet} (career flavor via natural karakatva)",
            "category": "career",
            "source_tier": 1,
            "source_ref": "BPHS Ch.10 / Saravali Ch.2 (app.knowledge.planets.KARAKATVA)",
            "tradition": "parasari",
            "conditions": [
                {"path": "house_lords.10", "op": "eq", "value": planet,
                 "description": f"10th lord is {planet}"},
            ],
            "outputs": [{"kind": "classification", "payload": {
                "planet": planet,
                "effect": f"With {planet} ruling the 10th, career naturally leans toward: {', '.join(professions)}.",
            }}],
            "confidence": "medium", "status": "ACTIVE", "computation_model": "classical",
            "notes": ["Reuses KARAKATVA's already-cited professions list verbatim (DRY) -- only the 7 classical planets can be sign lords, Rahu/Ketu honestly excluded."],
        })
    return rules


def _yoga_karaka_and_kendradhipati_rules() -> list[dict]:
    return [
        {
            "id": "CAR-YK", "title": "10th Lord is a Yoga-Karaka for this Lagna",
            "category": "career", "source_tier": 1, "source_ref": "BPHS Ch.34 (via app.derived.functional_nature)",
            "tradition": "parasari",
            "conditions": [{"path": "career_analysis.tenth_lord.is_yoga_karaka", "op": "eq", "value": True,
                             "description": "10th lord is classified yoga_karaka"}],
            "outputs": [{"kind": "classification", "payload": {
                "effect": "The 10th lord also rules a trikona -- the strongest possible functional-benefic case for career success (BPHS Ch.34).",
            }}],
            "confidence": "high", "status": "ACTIVE", "computation_model": "classical",
            "notes": ["Wraps app.derived.functional_nature verbatim -- zero new logic."],
        },
        {
            "id": "CAR-KD", "title": "10th Lord suffers Kendradhipati Dosha",
            "category": "career", "source_tier": 1, "source_ref": "BPHS Ch.34 (via app.derived.functional_nature)",
            "tradition": "parasari",
            "conditions": [{"path": "career_analysis.tenth_lord.is_kendradhipati_dosha", "op": "eq", "value": True,
                             "description": "10th lord is classified kendradhipati_dosha"}],
            "outputs": [{"kind": "classification", "payload": {
                "effect": "The 10th lord is a natural benefic ruling ONLY a kendra -- it still delivers career results but loses some unconditioned benefic purity (BPHS Ch.34).",
            }}],
            "confidence": "high", "status": "ACTIVE", "computation_model": "classical",
            "notes": ["Wraps app.derived.functional_nature verbatim -- zero new logic."],
        },
    ]


def build_rules() -> list[dict]:
    return (
        _tenth_lord_placement_rules()
        + _occupant_profession_rules()
        + _lord_identity_rules()
        + _yoga_karaka_and_kendradhipati_rules()
    )


def main() -> None:
    rules = build_rules()
    assert len(rules) == 30, f"expected 30 career rules, got {len(rules)}"
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as handle:
        yaml.safe_dump(rules, handle, allow_unicode=True, sort_keys=False, default_flow_style=False)
    print(f"Wrote {len(rules)} rules to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
