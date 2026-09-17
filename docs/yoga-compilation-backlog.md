# Yoga Compilation Backlog

> Referenced by `app/derived/yogas.py` and `app/rules/generators/generate_yoga_rules.py`.
> Tracks the gap between what's compiled (18 yogas) and the true reference
> scope, so the remainder is a visible backlog, never silently implied "done."

## 1. Re-baselined scope

`build_plan.md` originally estimated "~50+" yogas (from `LLM_ZERO_BRAINSTORM.md`).
Reading PyJHora's `horoscope/chart/yoga.py` directly (build_plan.md §5a's own
instruction) found **269 distinct named yogas** (1034 raw functions,
including `_from_jd_place` / `_from_planet_positions` / `_calculation`
wrapper variants per named yoga). This is the corrected baseline.

## 2. What's compiled today (18, Phase 4)

`app/derived/yogas.py` + `app/rules/compiled/yoga_v2.yaml` (YOG-001..YOG-018):
Gajakesari, Sunapha, Anapha, Durudhara, Chandra-Mangala, Adhi Yoga,
Budha-Aditya, Pancha Mahapurusha (5 sub-yogas as one rule), Neechabhanga
Raja Yoga, Parivartana (classified), Kendradhipati Dosha (yoga-view),
Viparita Raja Yoga (3 subtypes as one rule), Graha Yuddha, Kahala, Shankha,
Lakshmi, Vasumati, Amala.

**Selection rationale**: every yoga above was either (a) already
informally implemented in `app.knowledge.interpreter.detect_yogas` /
`app.knowledge.houses.RAJ_YOGA_COMBOS` (v1 prose/code, now formalized), or
(b) already scaffolded with concrete activation conditions in
`app/rules/bphs_top20_rule_cards_v1.yaml`'s YL-series cards. This kept the
tranche to yogas this codebase already had *some* verified basis for,
rather than researching 20 brand-new yogas from a cold start.

## 3. What's NOT compiled (~251 remaining)

The bulk of PyJHora's 269 fall into a few categories, none silently
dropped -- just not yet worth the citation-research cost for a
personal-reading engine:

- **Highly specific body/health yogas** (~40+): `guhyaroga_yoga`,
  `sirachcheda_yoga`, `swetakushta_yoga`, `kushtaroga_yoga` variants,
  `vaatharoga_yoga`, etc. -- niche medical-astrology combinations, rarely
  load-bearing in a general reading.
- **Progeny-outcome yogas** (~30+): `bahu_puthra_yoga`, `aputhra_yoga`,
  `eka_puthra_yoga`, `dattha_puthra_yoga` variants and their numbered
  sub-variants -- fine-grained child-count/adoption predictions.
- **Marriage/character-affliction yogas** (~15+): `bharyasahavyabhichara_yoga`,
  `vamsacheda_yoga`, `apakeerthi_yoga` -- sensitive-topic predictions that
  also need the strongest possible citation confidence before being
  surfaced (Cardinal Rule 9: never sugarcoat, but also never assert
  something this consequential on a thin source).
- **Numbered variant families** (e.g. `sarpasaapa_yoga_212` through `_215`,
  `mathibhramana_yoga_291` through `_294`) -- these are the SAME base yoga
  computed via alternate classical formulas/sources within PyJHora itself;
  compiling even the base yoga requires picking (or preserving, per
  Cardinal Rule 3) among the variant formulas, real editorial work.
- **The other ~230 yoga.py functions not itemized above** -- genuinely
  not yet triaged individually. This backlog file itself should be the
  first stop before compiling any of them, to avoid duplicate research.

## 4. How to pull the next batch

Follow build_plan.md §3.2's compilation workflow per yoga:
1. Read the actual classical source (BPHS/Saravali/Phaladeepika/Jataka
   Parijata) for the yoga's condition -- PyJHora's docstring/function name
   is a pointer to WHAT to look up, never a citation in itself (AD-4).
2. Cross-check the formula SHAPE only against PyJHora's implementation
   (never copy code).
3. Implement in `app/derived/yogas.py`, add to `compute_all_yogas()`.
4. Add rows to `app/rules/generators/generate_yoga_rules.py`'s `RULES` list,
   re-run `app.rules.generators.emit_all`.
5. Write a unit test (mirrors `tests/unit/test_yogas.py`'s pattern).
6. Update the counts in this file and in `build_plan.md`'s Phase 4 entry.
