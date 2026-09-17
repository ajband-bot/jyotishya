# Migration Plan

## Immediate Steps
1. Ingest BMad rule YAML into `jyotisha/app/rules/`.
2. Add chart-fixture loader and core-rule evaluator.
3. Expose a simple API endpoint for evaluating a chart fixture against the rule pack.
4. Reconcile markdown examples against live Swiss outputs.

## Completed In This Pass
- Ingested `bphs_top20_rule_cards_v1.yaml` into `app/rules/`.
- Added chart fixture loading from `data/charts/`.
- Added `evaluate_chart_fixture()` runtime path and `/api/rules/{chart_id}` endpoint.
- Implemented Lagna Pada and Upapada calculators.
- Preserved an explicit Upapada conflict for Ajay: canonical Arudha formula = Aries, guide-compatible inclusive-count branch = Sagittarius.
- Added practical Argala and practical Ashtakavarga proxy layers for runtime scoring.
- Added Sandeep as a second locked chart fixture for cross-chart validation.

## Near-Term Gaps
- Shadbala
- Vimsopaka
- Ishta/Kashta
- Argala
- Bhavapada/Lagna Pada
- Upapada
- Full classical Ashtakavarga
- Full classical Argala strength comparison

## Validation Strategy
- Golden chart fixtures: Ajay, Sandeep.
- Every discrepancy between markdown guides and live outputs must be reconciled or flagged.
