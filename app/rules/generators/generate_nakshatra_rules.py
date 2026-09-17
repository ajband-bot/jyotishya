"""Generator: Nakṣatra profile rules (27 = one per nakṣatra), keyed on the
MOON's nakṣatra -- the Janma Nak\u1e63atra, "MORE personal than the Moon sign"
per docs/nakshatra-framework.md \u00a79 item 5. Content is transcribed from
app.knowledge.nakshatras.NAKSHATRA_PROFILES (itself sourced from
docs/nakshatra-framework.md \u00a71's own BPHS Ch.86 / Nak\u1e63atra Cint\u0101ma\u1e47i
Ch.1 citation) -- no fresh research, a straightforward v1-knowledge-to-v2-
schema compilation per build_plan.md \u00a73.2.

Run: .venv/bin/python -m app.rules.generators.generate_nakshatra_rules
"""
from __future__ import annotations

from pathlib import Path

import yaml

from app.astro.constants import NAKSHATRAS
from app.knowledge.nakshatras import CITATION, GANA_TEMPERAMENT, NAKSHATRA_PROFILES

OUTPUT_PATH = Path(__file__).resolve().parents[1] / "compiled" / "nakshatra_v2.yaml"


def _effect_text(nak_id: int) -> str:
    nak = NAKSHATRAS[nak_id - 1]
    profile = NAKSHATRA_PROFILES[nak_id]
    gana = profile["gana"]
    return (
        f"Janma Nak\u1e63atra: {nak['en']}, ruled by {nak['lord']}, presided over by {nak['deity']}. "
        f"Ga\u1e47a: {gana} ({GANA_TEMPERAMENT[gana]}). Tattva: {profile['tattva']}. Yoni: {profile['yoni']}. "
        f"Underlying motivation (puru\u1e63\u0101rtha): {profile['motivation']}."
    )


def build_rules() -> list[dict]:
    rules = []
    for nak_id in range(1, 28):
        nak = NAKSHATRAS[nak_id - 1]
        rules.append({
            "id": f"NAK-{nak_id:02d}",
            "title": f"Janma Nak\u1e63atra: {nak['en']}",
            "category": "nakshatra",
            "source_tier": 1,
            "source_ref": CITATION,
            "tradition": "parasari",
            "conditions": [
                {"path": "nakshatra_analysis.Moon.nakshatra_id", "op": "eq", "value": nak_id,
                 "description": f"Moon occupies {nak['en']} nakshatra"},
            ],
            "outputs": [
                {"kind": "classification", "payload": {
                    "nakshatra_id": nak_id, "nakshatra_en": nak["en"], "effect": _effect_text(nak_id),
                }},
            ],
            "confidence": "high",
            "status": "ACTIVE",
            "computation_model": "classical",
            "notes": [
                "Migrated from app.knowledge.nakshatras.NAKSHATRA_PROFILES (itself transcribed from "
                "docs/nakshatra-framework.md \u00a71) per build_plan.md \u00a73.2 workflow.",
                "Keyed on the MOON's nak\u1e63atra (Janma Nak\u1e63atra) specifically -- the primary application per "
                "docs/nakshatra-framework.md \u00a79 item 5. The underlying app.derived.nakshatra_analysis engine "
                "computes this profile for every planet, not just Moon; a future rule set could key on Lagna/Sun/"
                "any-planet nakshatra the same way if a reading domain needs it.",
            ],
        })
    return rules


def main() -> None:
    rules = build_rules()
    assert len(rules) == 27, f"expected 27 nakshatra rules, got {len(rules)}"
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as handle:
        yaml.safe_dump(rules, handle, allow_unicode=True, sort_keys=False, default_flow_style=False)
    print(f"Wrote {len(rules)} rules to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
