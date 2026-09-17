"""Generator: Dosha rules + cancellations (build_plan.md target: ~15).

Unlike the compositional planet-in-house/sign/lord-placement generators,
these rules wrap ALREADY-COMPUTED, already-cited logic in
app.derived.doshas (BPHS Ch.77/80/24 + Saravali + documented conventions)
-- so computation_model stays "classical" throughout; nothing here is a
synthesized proxy. This is the most straightforward case of build_plan.md
\u00a73.2's compilation workflow: real Python logic already exists and is
tested (tests/unit/test_doshas.py); this generator's only job is exposing
each already-computed verdict as an inspectable, data-driven v2 Rule so it
can be picked up by the generic evaluator / future Narrative Composer
alongside every other rule category, instead of only being reachable via a
direct Python import.

Sade Sati (DSH-015) is deliberately categorized "transit", not "dosha" --
it is a transit phenomenon (Saturn's gochara relative to natal Moon), not a
natal affliction, even though docs/dosha-registry.md documents it in the
same file for context-budget reasons. Categorizing it honestly here avoids
quietly blurring two distinct classical mechanisms (Cardinal Rule 3).

Run: .venv/bin/python -m app.rules.generators.generate_dosha_rules
"""
from __future__ import annotations

from pathlib import Path

import yaml

OUTPUT_PATH = Path(__file__).resolve().parents[1] / "compiled" / "dosha_v2.yaml"

RULES = [
    {
        "id": "DSH-001", "title": "Mangal Dosha (Kuja Dosha) present",
        "category": "dosha", "source_tier": 1, "source_ref": "BPHS Ch.77",
        "path": "doshas.mangal_dosha.present", "value": True,
        "effect": "Mars occupies a Mangal Dosha house (1/2/4/7/8/12) from at least one of Lagna, Moon, or Venus.",
    },
    {
        "id": "DSH-002", "title": "Mangal Dosha severity: severe (all 3 references afflicted, uncancelled)",
        "category": "dosha", "source_tier": 1, "source_ref": "BPHS Ch.77",
        "path": "doshas.mangal_dosha.severity", "value": "severe",
        "effect": "Mars afflicts the Mangal Dosha houses from Lagna, Moon, AND Venus simultaneously, with no cancellation.",
    },
    {
        "id": "DSH-003", "title": "Mangal Dosha cancelled",
        "category": "dosha", "source_tier": 1, "source_ref": "BPHS Ch.77",
        "path": "doshas.mangal_dosha.severity", "value": "cancelled",
        "effect": "A cancellation condition (Jupiter/Venus aspect or conjunction with Mars) neutralizes the Dosha.",
    },
    {
        "id": "DSH-004", "title": "Chandra-Mangala Yoga concurrent with Mangal Dosha check",
        "category": "yoga", "source_tier": 1, "source_ref": "BPHS Ch.77 (noted alongside Mangal Dosha check)",
        "path": "doshas.mangal_dosha.chandra_mangala_yoga_present", "value": True,
        "effect": "Moon and Mars conjunct -- a wealth-through-real-estate yoga classically noted alongside the Mangal Dosha check.",
    },
    {
        "id": "DSH-005", "title": "Kala Sarpa Dosha -- full",
        "category": "dosha", "source_tier": 4, "source_ref": "Classical Kala Sarpa doctrine (not in core BPHS; widely-used convention)",
        "path": "doshas.kala_sarpa.type", "value": "full",
        "effect": "All 7 classical planets are hemmed on one side of the Rahu-Ketu axis, with none conjunct either node.",
    },
    {
        "id": "DSH-006", "title": "Kala Sarpa Dosha -- partial",
        "category": "dosha", "source_tier": 4, "source_ref": "Classical Kala Sarpa doctrine (not in core BPHS; widely-used convention)",
        "path": "doshas.kala_sarpa.type", "value": "partial",
        "effect": "All 7 classical planets are hemmed on one side of the axis, but one or more sit conjunct Rahu/Ketu, partially breaking the Dosha.",
    },
    {
        "id": "DSH-007", "title": "Pitru Dosha present",
        "category": "dosha", "source_tier": 1, "source_ref": "BPHS Ch.80",
        "path": "doshas.pitru_dosha.present", "value": True,
        "effect": "Sun in H9 afflicted by Rahu/Saturn, or the 9th lord is afflicted -- karmic debt to father/ancestors indicated.",
    },
    {
        "id": "DSH-008", "title": "Pitru Dosha via afflicted 9th lord specifically",
        "category": "dosha", "source_tier": 1, "source_ref": "BPHS Ch.80",
        "path": "doshas.pitru_dosha.ninth_lord_afflicted", "value": True,
        "effect": "The 9th lord itself (not the Sun-in-H9 condition) is conjunct or aspected by Rahu/Saturn.",
    },
    {
        "id": "DSH-009", "title": "Guru Chandala Yoga present",
        "category": "dosha", "source_tier": 4, "source_ref": "Saravali / common Parashari convention",
        "path": "doshas.guru_chandala.present", "value": True,
        "effect": "Jupiter conjunct Rahu within a 15-degree orb in the same sign -- corrupts Jupiter's wisdom/judgment.",
    },
    {
        "id": "DSH-010", "title": "Kemadruma Dosha -- raw condition met (before cancellation check)",
        "category": "dosha", "source_tier": 1, "source_ref": "BPHS Ch.24",
        "path": "doshas.kemadruma.raw_condition_met", "value": True,
        "effect": "No planet occupies the 2nd or 12th house from Moon -- the Kemadruma condition, prior to any cancellation check.",
    },
    {
        "id": "DSH-011", "title": "Kemadruma Dosha cancelled",
        "category": "dosha", "source_tier": 1, "source_ref": "BPHS Ch.24",
        "path": "doshas.kemadruma.cancelled", "value": True,
        "effect": "Moon in kendra, another planet in kendra from Lagna, or Jupiter/Venus aspecting Moon -- cancels the raw Kemadruma condition.",
    },
    {
        "id": "DSH-012", "title": "Kemadruma Dosha present (net verdict, cancellation-aware)",
        "category": "dosha", "source_tier": 1, "source_ref": "BPHS Ch.24",
        "path": "doshas.kemadruma.present", "value": True,
        "effect": "Kemadruma's raw condition is met AND no cancellation applies -- the Dosha is genuinely active.",
    },
    {
        "id": "DSH-013", "title": "Papakartari Yoga present (at least one house hemmed by malefics)",
        "category": "dosha", "source_tier": 4, "source_ref": "General Parashari principle (papa-kartari-yoga)",
        "path": "doshas.papakartari.present", "value": True,
        "effect": "At least one of the 12 houses is hemmed between two malefics (one immediately before, one immediately after) -- that house's affairs are constricted.",
    },
    {
        "id": "DSH-014", "title": "Mangal Dosha cancelled via Lagna-house own-sign/exaltation dignity",
        "category": "dosha", "source_tier": 1, "source_ref": "BPHS Ch.77 (house-specific full-cancellation table)",
        "path": "doshas.mangal_dosha.references.lagna.house_dignity_cancellation", "value": True,
        "effect": "Mars occupies its own Dosha house in a sign where Mars itself is dignified (e.g. Aries Lagna H1, Aries/Scorpio H4) -- BPHS treats this as no Dosha at all, not merely a mitigated one.",
    },
    {
        "id": "DSH-015", "title": "Sade Sati currently active",
        "category": "transit", "source_tier": 1, "source_ref": "Classical Sade Sati doctrine (Saturn gochara relative to natal Moon)",
        "path": "transits.saturn_assessment.sade_sati.active", "value": True,
        "effect": "Transit Saturn is in the 12th, 1st (over Moon), or 2nd house from natal Moon -- one of the three Sade Sati phases is currently running.",
    },
]


def build_rules() -> list[dict]:
    rules = []
    for spec in RULES:
        rules.append({
            "id": spec["id"],
            "title": spec["title"],
            "category": spec["category"],
            "source_tier": spec["source_tier"],
            "source_ref": spec["source_ref"],
            "tradition": "parasari",
            "conditions": [
                {"path": spec["path"], "op": "eq", "value": spec["value"], "description": spec["title"]},
            ],
            "outputs": [
                {"kind": "yoga_flag" if spec["category"] in ("yoga",) else "classification",
                 "payload": {"verdict": spec["id"], "effect": spec["effect"]}},
            ],
            "confidence": "high",
            "status": "ACTIVE",
            "computation_model": "classical",
            "notes": [
                "Wraps already-computed, already-tested logic in app.derived.doshas / app.astro.transits "
                "(tests/unit/test_doshas.py) -- this generator adds no new astrological logic, only v2 schema exposure, "
                "per build_plan.md \u00a73.2.",
            ],
        })
    return rules


def main() -> None:
    rules = build_rules()
    assert len(rules) == len(RULES) == 15, f"expected 15 dosha rules, got {len(rules)}"
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as handle:
        yaml.safe_dump(rules, handle, allow_unicode=True, sort_keys=False, default_flow_style=False)
    print(f"Wrote {len(rules)} rules to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
