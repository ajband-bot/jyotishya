# Jyotisha

Swiss Ephemeris-backed Vedic astrology engine with a rule-driven interpretation layer.

## Current Direction
The project is being refactored toward:
- a canonical astronomy kernel in `app/astro/`
- derived calculators in `app/derived/`
- scripture-backed YAML rule packs in `app/rules/`
- versioned chart fixtures in `data/charts/`

## Runtime Principle
Compute first. Interpret second. Never finalize a rule without computed evidence.

## Current Runtime Flow
- Chart fixtures live in `data/charts/`.
- Core rule pack lives in `app/rules/bphs_top20_rule_cards_v1.yaml`.
- Rule evaluation is available through `app.rules.evaluator.evaluate_chart_fixture()`.
- FastAPI exposes fixture evaluation at `/api/rules/{chart_id}`.

## Current Known Conflict
- Ajay's Upapada has a corpus disagreement:
	canonical Arudha-style formula computes `Aries`
	guide-compatible inclusive-count branch computes `Sagittarius`
- The runtime preserves both until the corpus is reconciled.

## Golden Fixtures
- `ajay_kumar`
- `sandeep_0700`

## Robust Test Suite
- Verify mode (critical checks + regression baseline compare):
	- `.venv/bin/python tests/run_suite.py --mode verify`
- Accept baseline mode (explicitly update expected regression snapshot):
	- `.venv/bin/python tests/run_suite.py --mode accept-baseline`

Baseline updates are opt-in only and never auto-applied during verify mode.

## Execution Standard
All execution rules, persona, validation process, and output specifications are defined in **[AGENTS.md](AGENTS.md)**.
That file is the single source of truth for AI-assisted horoscope generation.
