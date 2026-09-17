"""Generator: Remedy Prescription rules (20) -- build_plan.md Phase 6
("gated on functional-benefic/malefic classification being rule-driven").

Wraps app.derived.remedies's already-computed, safety-gated verdicts into
v2 Rule schema entries -- same "wrap already-computed logic" pattern as
generate_dosha_rules.py. Nothing here re-derives functional nature or
invents a new safety threshold; every condition below reads a field
remedies.py already produced.

  REM-GEM-<CODE>    (9): gemstone remedy is APPROPRIATE for this planet
                         (triple-confirmed per Remedy Safety Rule 2, or
                         the narrower Rule 6/7 gates for Saturn/Rahu).
  REM-NOGEM-<CODE>  (9): gemstone remedy is CONTRAINDICATED (functional
                         malefic, or a permanent safe default for
                         Rahu/Ketu absent their documented exception) --
                         the single most safety-critical rule family here
                         (Remedy Safety Rule 1).
  REM-SAT-SPECIAL   (1): Saturn's generic functional_benefic status is
                         NOT enough on its own -- the yogakaraka-only
                         gate (Rule 6) specifically blocked it.
  REM-RAHU-SPECIAL  (1): Rahu's narrow documented exception (well-placed
                         AND strong dispositor, Rule 7) is actually met.

Total: 9 + 9 + 1 + 1 = 20.

Run: .venv/bin/python -m app.rules.generators.generate_remedy_rules
"""
from __future__ import annotations

from pathlib import Path

import yaml

OUTPUT_PATH = Path(__file__).resolve().parents[1] / "compiled" / "remedy_v2.yaml"

PLANET_CODES = {
    "Sun": "SUN", "Moon": "MOO", "Mars": "MAR", "Mercury": "MER", "Jupiter": "JUP",
    "Venus": "VEN", "Saturn": "SAT", "Rahu": "RAH", "Ketu": "KET",
}
ALL_9 = list(PLANET_CODES.keys())


def _gemstone_appropriate_rules() -> list[dict]:
    rules = []
    for planet in ALL_9:
        code = PLANET_CODES[planet]
        rules.append({
            "id": f"REM-GEM-{code}",
            "title": f"Gemstone remedy appropriate for {planet}",
            "category": "remedy",
            "source_tier": 1,
            "source_ref": "docs/domain-playbooks.md Remedy Safety Rules 2/6/7",
            "tradition": "parasari",
            "conditions": [{"path": f"remedies.planets.{planet}.gemstone_appropriate", "op": "eq", "value": True,
                             "description": f"{planet}'s gemstone gate is satisfied"}],
            "outputs": [{"kind": "classification", "payload": {
                "planet": planet,
                "effect": f"{planet} passes the full gemstone safety gate (functional benefic + weak/afflicted + not combust, with Saturn/Rahu's stricter Rule 6/7 gates applied where relevant).",
            }}],
            "confidence": "high", "status": "ACTIVE", "computation_model": "classical",
            "notes": ["Wraps app.derived.remedies verbatim -- this generator adds no new safety logic, only v2 schema exposure."],
        })
    return rules


def _gemstone_contraindicated_rules() -> list[dict]:
    rules = []
    for planet in ALL_9:
        code = PLANET_CODES[planet]
        rules.append({
            "id": f"REM-NOGEM-{code}",
            "title": f"Gemstone remedy CONTRAINDICATED for {planet}",
            "category": "remedy",
            "source_tier": 1,
            "source_ref": "docs/domain-playbooks.md Remedy Safety Rule 1 (NEVER prescribe a gemstone for a functional malefic)",
            "tradition": "parasari",
            "conditions": [{"path": f"remedies.planets.{planet}.gemstone_contraindicated", "op": "eq", "value": True,
                             "description": f"{planet}'s gemstone is contraindicated"}],
            "outputs": [{"kind": "classification", "payload": {
                "planet": planet,
                "effect": f"{planet} is functionally malefic (or, for Rahu/Ketu, lacks its documented narrow exception) -- gemstone amplification is unsafe. Dana of {planet}'s significations is the preferred remedy (Rule 5).",
            }}],
            "confidence": "high", "status": "ACTIVE", "computation_model": "classical",
            "notes": ["Safety-critical rule family -- directly implements Remedy Safety Rule 1, the single most important gate in this pack."],
        })
    return rules


def _special_gate_rules() -> list[dict]:
    return [
        {
            "id": "REM-SAT-SPECIAL",
            "title": "Saturn blocked by the yogakaraka-only gemstone gate",
            "category": "remedy", "source_tier": 1,
            "source_ref": "docs/domain-playbooks.md Remedy Safety Rule 6 (NEVER blue sapphire unless Saturn is yogakaraka)",
            "tradition": "parasari",
            "conditions": [{"path": "remedies.planets.Saturn.blocked_by_yogakaraka_gate", "op": "eq", "value": True,
                             "description": "Saturn is functional_benefic (kendra-only inversion) but NOT yoga_karaka"}],
            "outputs": [{"kind": "classification", "payload": {
                "effect": "Saturn's generic functional_benefic status (natural-malefic-ruling-kendra-only inversion) is NOT sufficient for blue sapphire -- Rule 6 requires the stricter yogakaraka test specifically, which this chart does not meet.",
            }}],
            "confidence": "high", "status": "ACTIVE", "computation_model": "classical",
            "notes": ["Demonstrates the safety rule actually blocking what a naive generic-benefic reading would have wrongly allowed."],
        },
        {
            "id": "REM-RAHU-SPECIAL",
            "title": "Rahu's narrow hessonite exception is met",
            "category": "remedy", "source_tier": 4,
            "source_ref": "docs/domain-playbooks.md Remedy Safety Rule 7 (NEVER hessonite unless Rahu is well-placed and its dispositor is strong)",
            "tradition": "parasari",
            "conditions": [{"path": "remedies.planets.Rahu.well_placed_and_strong_dispositor", "op": "eq", "value": True,
                             "description": "Rahu is not in a dusthana AND its sign dispositor is strong/very_strong"}],
            "outputs": [{"kind": "classification", "payload": {
                "effect": "Rahu is well-placed (not in a dusthana) and its sign dispositor tests strong -- Rule 7's narrow exception is met, so hessonite may be considered (still not a default recommendation).",
            }}],
            "confidence": "medium", "status": "ACTIVE", "computation_model": "classical",
            "notes": ["Reports that the exception CONDITION is met -- does not itself force a gemstone recommendation, per Rule 7's own cautious framing."],
        },
    ]


def build_rules() -> list[dict]:
    return _gemstone_appropriate_rules() + _gemstone_contraindicated_rules() + _special_gate_rules()


def main() -> None:
    rules = build_rules()
    assert len(rules) == 20, f"expected 20 remedy rules, got {len(rules)}"
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as handle:
        yaml.safe_dump(rules, handle, allow_unicode=True, sort_keys=False, default_flow_style=False)
    print(f"Wrote {len(rules)} rules to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
