"""Generator: Dasha Mahadasha x Antardasha composition rules (build_plan.md
Phase 5, target 81 = 9x9).

Deliberately NOT a table of 81 hand-authored canned blurbs -- that is
exactly the anti-pattern app.derived.dasha_synthesis's own module
docstring (Phase 2) already warns against ("the 81-combination canned-text
pattern build_plan.md warns about"). Instead, each rule's `effect` text is
MECHANICALLY COMPOSED at generation time from two already-existing,
already-cited primitives:

  1. app.knowledge.planets.KARAKATVA -- each planet's natural
     significations (BPHS Ch.10 + Saravali Ch.2), a 9-row table, not 81.
  2. app.derived.dignities.naisargika_relationship -- the MD/AD lords'
     mutual natural friendship (BPHS Ch.4), already verified against
     PyJHora in Phase 1.

So the only genuinely-authored content here is those 9 planet rows (which
already existed before this generator) plus the friendship function
(ditto) -- the 81 rules are a data CROSS-PRODUCT of that existing
knowledge, composed once at compile time since MD/AD natural friendship
is chart-independent (a fixed classical fact, unlike house placements).
Chart-SPECIFIC evidence (functional nature, owned-house Bhava Bala,
dispositor terminus for whichever lord is actually running) is
deliberately left to `ctx['dasha_synthesis']` (already built, Phase 2)
rather than duplicated here -- each rule's effect text says exactly that,
directing the reader to where the real per-chart depth lives.

Run: .venv/bin/python -m app.rules.generators.generate_dasha_rules
"""
from __future__ import annotations

from pathlib import Path

import yaml

from app.derived.dignities import naisargika_relationship
from app.knowledge.planets import KARAKATVA

OUTPUT_PATH = Path(__file__).resolve().parents[1] / "compiled" / "dasha_composition_v2.yaml"

PLANETS_9 = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]


def _signif(planet: str) -> str:
    return ", ".join(KARAKATVA[planet]["signifies"][:4])


def _relationship_phrase(md: str, ad: str) -> str:
    if md == ad:
        return "the same planet governs both Mahadasha and Antardasha -- its own themes intensify without external modulation"
    rel_md_to_ad = naisargika_relationship(md, ad)
    rel_ad_to_md = naisargika_relationship(ad, md)
    if rel_md_to_ad == "friend" and rel_ad_to_md == "friend":
        return "the two lords are mutual natural friends -- their themes generally cooperate through the period"
    if rel_md_to_ad == "enemy" and rel_ad_to_md == "enemy":
        return "the two lords are mutual natural enemies -- expect friction between their themes before results mature"
    return "the two lords have a mixed natural relationship -- how the period actually unfolds leans heavily on each lord's own strength and house-lordship in this specific chart"


def build_rules() -> list[dict]:
    rules = []
    for md in PLANETS_9:
        for ad in PLANETS_9:
            rule_id = f"DASHA-{md.upper()}-{ad.upper()}"
            effect = (
                f"{md} Mahadasha ({_signif(md)}) running {ad} Antardasha ({_signif(ad)}): "
                f"{_relationship_phrase(md, ad)}. This rule flags WHICH combination is currently "
                f"running, not a canned outcome -- chart-specific composed evidence (functional "
                f"nature, owned-house Bhava Bala, dispositor terminus for both lords) already "
                f"lives in ctx['dasha_synthesis']['stack']."
            )
            rules.append({
                "id": rule_id,
                "title": f"{md} Mahadasha / {ad} Antardasha running",
                "category": "dasha",
                "source_tier": 1,
                "source_ref": "BPHS Ch.10 (Karakatva) + Ch.4 (Graha Maitri) -- composed MD/AD combination, per build_plan.md Phase 5's compilation directive",
                "tradition": "parasari",
                "conditions": [
                    {"path": "current_dasha.mahadasha.planet", "op": "eq", "value": md, "description": f"Mahadasha lord is {md}"},
                    {"path": "current_dasha.antardasha.planet", "op": "eq", "value": ad, "description": f"Antardasha lord is {ad}"},
                ],
                "outputs": [
                    {"kind": "classification", "payload": {
                        "dasha_combination": rule_id,
                        "mahadasha_signif": _signif(md),
                        "antardasha_signif": _signif(ad),
                        "effect": effect,
                    }},
                ],
                "confidence": "medium",
                "status": "ACTIVE",
                "computation_model": "practical_proxy",
                "notes": [
                    "Composed cross-product of app.knowledge.planets.KARAKATVA (9 rows) and "
                    "app.derived.dignities.naisargika_relationship (already Phase-1-verified) -- "
                    "not 81 independently authored blurbs, per this generator's own module docstring.",
                    "computation_model=practical_proxy (quality downgrades to computed_simplified) "
                    "because this rule states a GENERAL combination principle, not a verse-by-verse "
                    "citation for this exact 81st pairing -- honest per Cardinal Rule 5/9.",
                ],
            })
    return rules


def main() -> None:
    rules = build_rules()
    assert len(rules) == 81, f"expected 81 dasha composition rules, got {len(rules)}"
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as handle:
        yaml.safe_dump(rules, handle, allow_unicode=True, sort_keys=False, default_flow_style=False)
    print(f"Wrote {len(rules)} rules to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
