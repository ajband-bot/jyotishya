# Execution Process

## Objective
Run scripture-backed rule evaluation on a chart using computed astronomical values first, then derived factors, then rules.

## End-to-End Flow
1. Load chart fixture from `data/charts/*.yaml`.
2. Compute Julian day, ayanamsha, sidereal longitudes, houses, combustion, retrograde, D9, and Vimshottari dasha using `app/astro/`.
3. Compute derived factors in `app/derived/`:
   - house lords
   - maraka lords
   - aspect map
   - Lagna Pada
   - Upapada
   - simplified Shadbala
   - simplified Ishta/Kashta
   - practical D1/D9 varga quality
   - transit assessment
4. Load rule pack from `app/rules/bphs_top20_rule_cards_v1.yaml`.
5. Evaluate each rule against computed context in `app/rules/evaluator.py`.
6. Return structured evidence, outcome, and quality labels.

## Current Output Labels
- `computed`
- `computed_simplified`
- `computed_with_conflict`
- `data_gap`

## Current Timing Layers
- Mahadasha
- Antardasha
- Pratyantardasha
- Current Jupiter/Saturn/Rahu/Ketu transit references from Moon/Lagna/Sun

## Policy
- Markdown corpus is documentation only.
- Runtime never silently hides formula disagreements.
- If a guide and computed runtime differ, the conflict must be preserved until resolved.

## Current Important Missing Modules
- Full classical Vimsopaka
- Full classical Shadbala in shastiamsa terms
- Full classical Ishta/Kashta
- Argala
- Ashtakavarga
- Bhavapada family beyond A1/UL
- D10 and D7 derived interpretation layers
