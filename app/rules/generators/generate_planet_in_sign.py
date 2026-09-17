"""Generator: Planet-in-Sign rules (108 = 9 planets x 12 signs).

build_plan.md target rule inventory ("Planet-in-sign effects, ~108, BPHS +
Brihat Jataka, not started"). Unlike planet-in-house content (which already
existed as verified v1 prose in app.knowledge.planets.PLANET_IN_HOUSE),
NO equivalent per-sign prose exists anywhere in this codebase or corpus --
compiling it as 108 individually verse-cited entries would require a fresh
Brihat Jataka Ch.4 research pass this session does not have budget for.

Rather than fabricate per-sign verse citations (Cardinal Rule 2), this
generator applies an honest, cited SYNTHESIS: the planet's own natural
karakatva (BPHS Ch.10 / Saravali Ch.2, already verified content in
app.knowledge.planets.KARAKATVA) filtered through the sign's classical
element/quality (BPHS/Saravali, app.astro.constants.SIGNS) and its formal
dignity there (BPHS Ch.3 exaltation/debilitation/own-sign table,
app.astro.engine.planet_state). Tagged `computation_model: practical_proxy`
throughout -- the generic evaluator reports quality=computed_simplified,
never silently claiming Brihat Jataka verse-level fidelity per entry. A
genuine per-sign verse-citation enrichment pass is the honest follow-up
(tracked here, not silently skipped).

Run: .venv/bin/python -m app.rules.generators.generate_planet_in_sign
"""
from __future__ import annotations

from pathlib import Path

import yaml

from app.astro.constants import SIGNS
from app.astro.engine import planet_state
from app.knowledge.planets import KARAKATVA

OUTPUT_PATH = Path(__file__).resolve().parents[1] / "compiled" / "planet_in_sign_v2.yaml"

PLANET_CODES = {
    "Sun": "SUN", "Moon": "MOO", "Mars": "MAR", "Mercury": "MER", "Jupiter": "JUP",
    "Venus": "VEN", "Saturn": "SAT", "Rahu": "RAH", "Ketu": "KET",
}


def _effect_text(planet: str, sign_no: int) -> str:
    sign = SIGNS[sign_no - 1]
    kv = KARAKATVA[planet]
    state = planet_state(planet, sign_no)
    top_significations = ", ".join(kv["signifies"][:3])
    dignity_clause = {
        "exalted": "at its classical peak here -- these themes express with maximum ease and confidence",
        "debilitated": "under classical strain here -- these themes express only with effort, delay, or via a struggle that ultimately teaches the sign's own lesson",
        "own-sign": "fully at home here -- these themes express in an unforced, natural, sustainable way",
        "neutral": "expressing in a workable, ordinary register here -- neither maximally boosted nor strained",
    }[state]
    return (
        f"{planet}'s natural significations ({top_significations}) filtered through {sign['en']} "
        f"({sign['element']} element, {sign['quality']} quality). Dignity: {state} -- {dignity_clause}."
    )


def build_rules() -> list[dict]:
    rules = []
    for planet in KARAKATVA:
        code = PLANET_CODES[planet]
        for sign_no in range(1, 13):
            rules.append({
                "id": f"PIS-{code}-{sign_no:02d}",
                "title": f"{planet} in {SIGNS[sign_no - 1]['en']}",
                "category": "dignity",
                "source_tier": 3,
                "source_ref": (
                    "Compositional synthesis of BPHS Ch.10/Saravali Ch.2 karakatva "
                    "(app.knowledge.planets.KARAKATVA) + BPHS Ch.3 sign dignity "
                    "(app.astro.constants.PLANET_STATES/SIGNS); not a per-sign Brihat Jataka verse citation."
                ),
                "tradition": "parasari",
                "conditions": [
                    {"path": f"chart.{planet}.sign", "op": "eq", "value": sign_no,
                     "description": f"{planet} occupies {SIGNS[sign_no - 1]['en']}"},
                ],
                "outputs": [
                    {"kind": "classification", "payload": {
                        "planet": planet, "sign": sign_no, "sign_en": SIGNS[sign_no - 1]["en"],
                        "effect": _effect_text(planet, sign_no),
                    }},
                ],
                "confidence": "medium",
                "status": "ACTIVE",
                "computation_model": "practical_proxy",
                "notes": [
                    "category=dignity is broader here than formal exalt/own/debil tiers alone -- this rule set covers "
                    "the full qualitative planet+sign combination, not just the 3-state dignity table; no dedicated "
                    "category exists for 'planet-in-sign' specifically and force-fitting a brand-new enum entry for "
                    "108 mechanically-generated entries was judged unwarranted (YAGNI) versus reusing 'dignity' "
                    "with this note.",
                    "computation_model=practical_proxy -> generic evaluator reports quality=computed_simplified.",
                ],
            })
    return rules


def main() -> None:
    rules = build_rules()
    assert len(rules) == 108, f"expected 108 planet-in-sign rules, got {len(rules)}"
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as handle:
        yaml.safe_dump(rules, handle, allow_unicode=True, sort_keys=False, default_flow_style=False)
    print(f"Wrote {len(rules)} rules to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
