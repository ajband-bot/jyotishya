# Robust Test Suite Engine

This suite enforces two layers:

- Critical behavior checks: deterministic invariants that must always hold.
- Regression behavior checks: baseline snapshot comparison for locked fixtures.

## Commands

From repository root:

```bash
.venv/bin/python tests/run_suite.py --mode verify
```

Accept intentional output changes and refresh baseline:

```bash
.venv/bin/python tests/run_suite.py --mode accept-baseline
```

Optional date anchor override:

```bash
.venv/bin/python tests/run_suite.py --mode verify --date 2026-04-11
```

## Baseline Policy

- Baselines are never auto-adjusted during verify mode.
- Baseline updates are explicit and opt-in using `--mode accept-baseline`.
- Critical checks run in both modes; baseline acceptance is blocked if critical checks fail.

## Scope

Locked fixtures:

- `ajay_kumar`
- `sandeep_0700`

Key guarded behaviors:

- Dasha chain stability on date anchor
- Aspect/combustion integrity checks
- Upapada conflict preservation
- RC-013 and RC-020 non-gap coverage
- Allowed quality-label taxonomy