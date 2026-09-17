"""Generator: Yoga rules compiled from app.derived.yogas (build_plan.md
Phase 4). Wraps the ~20-yoga Phase 4 tranche as inspectable v2 Rules,
following the exact same pattern as generate_dosha_rules.py -- real Python
logic already exists and is tested (tests/unit/test_yogas.py); this
generator's only job is exposing each verdict to the generic evaluator /
Narrative Composer's yoga.jinja template.

Run: .venv/bin/python -m app.rules.generators.generate_yoga_rules
"""
from __future__ import annotations

from pathlib import Path

import yaml

OUTPUT_PATH = Path(__file__).resolve().parents[1] / "compiled" / "yoga_v2.yaml"

RULES = [
    {"id": "YOG-001", "title": "Gajakesari Yoga present", "source_tier": 1, "source_ref": "BPHS Ch.36",
     "path": "yogas.gajakesari.present", "effect": "Jupiter occupies a kendra (1/4/7/10) from Moon -- noble character, wisdom, and fame."},
    {"id": "YOG-002", "title": "Sunapha Yoga present", "source_tier": 1, "source_ref": "BPHS Ch.37",
     "path": "yogas.sunapha.present", "effect": "A planet (other than Sun) occupies the 2nd house from Moon -- self-earned resources and reputation."},
    {"id": "YOG-003", "title": "Anapha Yoga present", "source_tier": 1, "source_ref": "BPHS Ch.37",
     "path": "yogas.anapha.present", "effect": "A planet (other than Sun) occupies the 12th house from Moon -- good health, comfort, and refined tastes."},
    {"id": "YOG-004", "title": "Durudhara Yoga present", "source_tier": 1, "source_ref": "BPHS Ch.37",
     "path": "yogas.durudhara.present", "effect": "Planets occupy BOTH the 2nd and 12th houses from Moon simultaneously -- wealth, vehicles, and a supportive circle."},
    {"id": "YOG-005", "title": "Chandra-Mangala Yoga present", "source_tier": 4, "source_ref": "Saravali",
     "path": "yogas.chandra_mangala.present", "effect": "Moon and Mars conjunct -- wealth through enterprise, real estate, or commercial drive."},
    {"id": "YOG-006", "title": "Adhi Yoga present", "source_tier": 4, "source_ref": "BPHS/Saravali (common Adhi Yoga formulation)",
     "path": "yogas.adhi_yoga.present", "effect": "Natural benefics occupy the 6th, 7th, and/or 8th houses from Moon -- leadership capacity and sustained good fortune."},
    {"id": "YOG-007", "title": "Budha-Aditya Yoga present", "source_tier": 4, "source_ref": "Saravali",
     "path": "yogas.budha_aditya.present", "effect": "Mercury and Sun conjunct within 14 degrees -- sharp intellect, eloquence, and analytical fame."},
    {"id": "YOG-008", "title": "Pancha Mahapurusha Yoga present (any of the 5)", "source_tier": 1, "source_ref": "BPHS Ch.75",
     "path": "yogas.pancha_mahapurusha.any_present", "effect": "One of Mars/Mercury/Jupiter/Venus/Saturn is in its own sign or exaltation, occupying a kendra from Lagna -- Maharaja-level qualities of that planet."},
    {"id": "YOG-009", "title": "Neechabhanga Raja Yoga present", "source_tier": 1, "source_ref": "BPHS (Neechabhanga doctrine)",
     "path": "yogas.neechabhanga_raja_yoga.present", "effect": "A debilitated planet's debility is cancelled by its debilitation-sign lord occupying a kendra -- debility transforms into raja yoga potential."},
    {"id": "YOG-010", "title": "Parivartana Yoga present", "source_tier": 3, "source_ref": "build_plan.md YL-001 (classification over app.derived.dispositors raw evidence)",
     "path": "yogas.parivartana.present", "effect": "Two planets mutually occupy each other's sign of rulership -- a structural exchange whose auspiciousness depends on the houses involved (see evidence for maha/dainya-kashta/neutral classification)."},
    {"id": "YOG-011", "title": "Kendradhipati Dosha present (yoga-view)", "source_tier": 1, "source_ref": "BPHS Ch.34 (via app.derived.functional_nature)",
     "path": "yogas.kendradhipati_dosha.present", "effect": "A natural benefic rules a kendra house alone -- loses some unconditioned benefic purity (does not turn malefic)."},
    {"id": "YOG-012", "title": "Viparita Raja Yoga present (any of Harsha/Sarala/Vimala)", "source_tier": 3, "source_ref": "build_plan.md YL-005 (stub_pending_translation)",
     "path": "yogas.viparita_raja_yoga.any_present", "effect": "A dusthana lord (6th/8th/12th) occupies another dusthana house -- the mutual affliction self-cancels, and the native rises from difficulty."},
    {"id": "YOG-013", "title": "Graha Yuddha (planetary war) present", "source_tier": 4, "source_ref": "build_plan.md YL-006 (stub_pending_translation)",
     "path": "yogas.graha_yuddha.present", "effect": "Two planets (excluding Sun/Moon/nodes) sit within 1 degree of longitude -- the loser's themes and house lordships are weakened for outcome delivery."},
    {"id": "YOG-014", "title": "Kahala Yoga present", "source_tier": 4, "source_ref": "build_plan.md YL-004 (stub_pending_translation)",
     "path": "yogas.kahala.present", "effect": "4th and 9th lords occupy mutual kendras from each other -- courageous wealth and authority."},
    {"id": "YOG-015", "title": "Shankha Yoga present", "source_tier": 4, "source_ref": "build_plan.md YL-004 (stub_pending_translation)",
     "path": "yogas.shankha.present", "effect": "5th and 6th lords occupy mutual kendras from each other -- charitable disposition and learned prosperity."},
    {"id": "YOG-016", "title": "Lakshmi Yoga present", "source_tier": 4, "source_ref": "Common Parashari convention (app.knowledge.houses.RAJ_YOGA_COMBOS)",
     "path": "yogas.lakshmi.present", "effect": "9th lord occupies a kendra in its own sign or exaltation -- immense wealth and fortune."},
    {"id": "YOG-017", "title": "Vasumati Yoga present", "source_tier": 4, "source_ref": "Common Parashari convention",
     "path": "yogas.vasumati.present", "effect": "At least 2 natural benefics occupy upachaya houses (3/6/10/11) from Lagna -- growing prosperity over the lifetime."},
    {"id": "YOG-018", "title": "Amala Yoga present", "source_tier": 4, "source_ref": "Common Parashari convention",
     "path": "yogas.amala.present", "effect": "A benefic occupies the 10th house from Lagna or from Moon -- spotless reputation and lasting good name."},
]


def build_rules() -> list[dict]:
    rules = []
    for spec in RULES:
        rules.append({
            "id": spec["id"],
            "title": spec["title"],
            "category": "yoga",
            "source_tier": spec["source_tier"],
            "source_ref": spec["source_ref"],
            "tradition": "parasari",
            "conditions": [
                {"path": spec["path"], "op": "eq", "value": True, "description": spec["title"]},
            ],
            "outputs": [
                {"kind": "yoga_flag", "payload": {"yoga": spec["id"], "effect": spec["effect"]}},
            ],
            "confidence": "high" if spec["source_tier"] <= 1 else "medium",
            "status": "ACTIVE",
            "computation_model": "classical",
            "notes": [
                "Wraps already-computed, already-tested logic in app.derived.yogas (tests/unit/test_yogas.py) -- "
                "this generator adds no new astrological logic, only v2 schema exposure, per build_plan.md \u00a73.2.",
                "Part of build_plan.md Phase 4's re-baselined yoga scope: 269 distinct named yogas exist in the "
                "PyJHora reference corpus; this ~20-yoga tranche covers the classically central set already present "
                "in this codebase's v1 knowledge or YL-series scaffolding. Remaining yogas tracked in "
                "docs/yoga-compilation-backlog.md, not silently dropped.",
            ],
        })
    return rules


def main() -> None:
    rules = build_rules()
    assert len(rules) == 18, f"expected 18 yoga rules, got {len(rules)}"
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as handle:
        yaml.safe_dump(rules, handle, allow_unicode=True, sort_keys=False, default_flow_style=False)
    print(f"Wrote {len(rules)} rules to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
