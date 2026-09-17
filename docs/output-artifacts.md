# Output Artifacts

## End User Artifacts
1. Chart fixture-backed rule evaluation JSON via `/api/rules/{chart_id}`.
2. Human-readable rule evidence rows: rule id, evidence, outcome, quality.
3. Dasha timing summary: MD / AD / PD.
4. Transit reference summary from Moon, Lagna, and Sun.
5. Strength summaries for each graha.

## Owner / System Artifacts
1. Versioned chart fixtures in `data/charts/`.
2. Versioned rule packs in `app/rules/`.
3. Reproducible execution path in code.
4. Explicit conflict capture when corpus formulas disagree.
5. Migration docs and architecture docs.
6. Golden-chart validation surface for regression testing.

## Typical Deliverables Per Chart
- Computed chart context
- Rule evaluation table
- Strength table
- Dasha timeline
- Transit snapshot
- Conflict register if formulas disagree

## Intended Consumers
- End user: readable conclusions with evidence.
- Owner: versioned, testable, auditable runtime artifacts.
