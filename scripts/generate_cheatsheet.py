"""Generates docs/JYOTISHA_CHEATSHEET.md from
app.engine.cheatsheet.concepts.CONCEPTS -- the single generated source for
the Phase 7 "learning platform" cheat sheet (build_plan.md Phase 7).

Never hand-edit docs/JYOTISHA_CHEATSHEET.md directly -- it will be
overwritten the next time this runs. Edit app/engine/cheatsheet/concepts.py
instead, exactly like app/rules/compiled/*.yaml is never hand-edited and
app/rules/generators/emit_all.py is re-run instead.

Usage:
    .venv/bin/python scripts/generate_cheatsheet.py
"""
from __future__ import annotations

import os
import sys
from datetime import date

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.engine.cheatsheet.concepts import CONCEPTS, concepts_by_category

CATEGORY_TITLES = {
    "foundations": "Foundations -- Lagna, Karakatva, Dignity, Functional Nature, Aspects, Combustion",
    "vargas": "Divisional Charts & Arudha -- Vargas, Vimsopaka Bala, Bhavapada",
    "strength": "Strength Engines -- Shadbala, Ishta/Kashta Phala, Ashtakavarga",
    "timing": "Timing -- Vimshottari Dasha, Gochara, Sade Sati",
    "dosha": "Doshas -- the 8 mandatory afflictions checked every reading",
    "yoga": "Yogas -- the compiled central tranche (of 269 named yogas total)",
    "nakshatra": "Nakshatras -- 27 lunar mansions, Gandanta/Abhukta Mula",
    "intervention": "Interventions -- Argala",
    "domain": "Domain Syntheses -- Marriage, Career, Remedies",
    "meta": "Meta -- how to read this project's own honesty machinery",
}

QUALITY_LEGEND = """
| Label | Meaning |
|---|---|
| `computed` | Full classical-precision derivation, cross-checked where a reference exists. |
| `computed_simplified` | A practical proxy or compositional synthesis -- honestly downgraded even when every input resolves cleanly. |
| `computed_with_conflict` | Two source formulas disagree; both are preserved, never silently reconciled. |
| `data_gap` | Genuinely not implemented (or, for a handful of process/meta entries, not a calculator at all) -- never guessed or faked. |
"""


def _render_concept(entry) -> str:
    lines = [f"### {entry.english_gloss}" + (f" ({entry.sanskrit_term})" if entry.sanskrit_term else "")]
    lines.append("")
    lines.append(f"- **Classical definition:** {entry.classical_definition}")
    lines.append(f"- **Primary citation:** {entry.primary_citation}")
    lines.append(f"- **Quality label:** `{entry.quality_label}`")
    if entry.code_ref:
        lines.append(f"- **Implemented at:** `{entry.code_ref}`")
    else:
        lines.append("- **Implemented at:** _(documentation/process concept, not a calculator)_")
    if entry.caveats:
        lines.append("- **Caveats:**")
        for caveat in entry.caveats:
            lines.append(f"  - {caveat}")
    if entry.cross_check_note:
        lines.append(f"- **Cross-check status:** {entry.cross_check_note}")
    lines.append("")
    return "\n".join(lines)


def generate() -> str:
    grouped = concepts_by_category()
    parts = [
        "# Jyotisha Learning Cheat Sheet",
        "",
        f"> **Generated {date.today().isoformat()} by `scripts/generate_cheatsheet.py` from "
        "`app/engine/cheatsheet/concepts.py` -- never hand-edit this file, it will be "
        "overwritten. This is the Phase 7 'learning platform' artifact: read it top to bottom "
        "and you should come away understanding both the classical Jyotisha concept AND exactly "
        "how (and how completely, and with what caveats) this project computes it.**",
        "",
        "For deeper prose than this summary provides, follow each entry's **Primary citation** "
        "to the referenced `docs/*.md` file or classical text. For live, per-chart validation of "
        "every claim below, see the Cheat-Sheet Cross-Validation Console "
        "(`GET /api/v2/cheatsheet/claims`, `cheatsheet_claims` DB table) -- this document "
        "describes what SHOULD be true; that console confirms whether it currently IS true.",
        "",
        f"**{len(CONCEPTS)} concepts** across **{len(grouped)} categories**, spanning every "
        "layer of `AGENTS.md`'s Process (Truth -> Derived -> Rules -> Engine) and every "
        "classical topic this codebase claims to implement.",
        "",
        "## Quality label legend",
        QUALITY_LEGEND,
        "## Classical text hierarchy",
        "",
        "When texts conflict: **BPHS** (primary Parasari authority) > Brihat Jataka > "
        "Phaladipika > Saravali > Sarvartha Cintamani (primary transit-methodology authority) > "
        "Jataka Parijata > Uttara Kalamrita > Nakshatra Cintamani. Jaimini-specific topics "
        "(karakas, chara dasha, karakamsha) defer to the Jaimini Sutras (Sanjay Rath commentary "
        "primary). See `AGENTS.md` §7.",
        "",
    ]

    for category in CATEGORY_TITLES:
        entries = grouped.get(category, [])
        if not entries:
            continue
        parts.append(f"## {CATEGORY_TITLES[category]}")
        parts.append("")
        for entry in entries:
            parts.append(_render_concept(entry))

    parts.append("---")
    parts.append("")
    parts.append(
        "*This document is generated, not authored -- it can never silently drift from the "
        "code it describes the way hand-written prose can. Re-run "
        "`scripts/generate_cheatsheet.py` after any change to `app/engine/cheatsheet/concepts.py`, "
        "and `scripts/sync_db.py` to refresh the DB-backed `cheatsheet_concepts` table alongside it.*"
    )
    return "\n".join(parts)


def main() -> None:
    output_path = os.path.join(os.path.dirname(__file__), "..", "docs", "JYOTISHA_CHEATSHEET.md")
    content = generate()
    with open(output_path, "w", encoding="utf-8") as handle:
        handle.write(content)
    print(f"Wrote {output_path} ({len(content)} chars, {len(CONCEPTS)} concepts).")


if __name__ == "__main__":
    main()
