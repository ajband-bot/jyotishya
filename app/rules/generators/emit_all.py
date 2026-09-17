"""Run every Phase 2 rule generator and regenerate all compiled YAML packs
under app/rules/compiled/. Idempotent -- safe to re-run any time the source
knowledge modules or generator templates change.

Run: .venv/bin/python -m app.rules.generators.emit_all
"""
from __future__ import annotations

from app.rules.generators import (
    generate_career_rules,
    generate_dasha_rules,
    generate_dosha_rules,
    generate_lord_placement,
    generate_marriage_rules,
    generate_nakshatra_rules,
    generate_planet_in_house,
    generate_planet_in_sign,
    generate_remedy_rules,
    generate_yoga_rules,
)

GENERATORS = [
    generate_planet_in_house,
    generate_lord_placement,
    generate_planet_in_sign,
    generate_dosha_rules,
    generate_yoga_rules,
    generate_nakshatra_rules,
    generate_dasha_rules,
    generate_marriage_rules,
    generate_career_rules,
    generate_remedy_rules,
]


def main() -> None:
    for module in GENERATORS:
        module.main()


if __name__ == "__main__":
    main()
