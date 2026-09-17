# 1. License & Legal Analysis

## Summary table

| Repo | Declared License | Verified in | Copyleft scope | Verdict |
|---|---|---|---|---|
| OpenJyotish | AGPL-3.0-or-later | `LICENSE` (full GNU AGPLv3 text), `pyproject.toml` (`license = {text = "AGPL-3.0-or-later"}`) | Network use = distribution | BLOCKED — do not vendor or link against |
| PyJHora | AGPL-3.0-or-later | `LICENSE` (full GNU AGPLv3 text), `pyproject.toml` (`license-expression = "AGPL-3.0-or-later"`) | Network use = distribution | BLOCKED — do not vendor or link against |
| VedAstro | MIT | `LICENSE.md` (standard MIT, copyright VedAstro.org 2014-2022) | None (permissive) | ALLOWED — legally reusable, but see stack-fit note in `02-feature-comparison.md` |

## Why AGPL is disqualifying here, specifically

AGPL-3.0 is the strictest of the GPL family. Two clauses matter for us:

1. **Copyleft on modification** — any modified version must also be
   released under AGPL with source available.
2. **The "network clause" (§13)** — *running* the software to serve users
   over a network counts as "conveying" it, even if you never distribute a
   binary. If our FastAPI app imported `jhora` (PyJHora) or vendored
   OpenJyotish's calculators and served results to a single end user over
   HTTP, that alone would trigger the obligation to offer our combined
   work's *complete corresponding source* to that user — likely including
   our proprietary rule engine, YAML rule packs, and any Walmart-adjacent
   integration code, depending on how "the Program" is scoped.

For a project that:
- already has a defined proprietary rule-engine direction
  (`docs/technical-architecture.md` — Rule Engine v2, event scoring,
  evidence engine — all clearly meant to be our own IP), and
- runs under Walmart infrastructure guidance (`AGENTS.md` Walmart rules
  block explicitly forbids things like Snyk-suppression tricks — the spirit
  is "don't paper over compliance risk"),

...importing or copy-pasting AGPL code is a real liability, not a
theoretical one. **This is true even for a single function.** AGPL
attaches per file/module that derives from the licensed work, not per
"whole program" — the safe assumption is "if code originated in these
repos and ended up in `app/`, the whole `app/` module it lives in is now
AGPL-tainted."

This is not a novel conclusion — OpenJyotish's own README says it plainly:
*"Modifications must remain open. Network use counts as distribution."*
They are not shy about it; take them at their word.

## The MIT one (VedAstro) — what it actually buys us

VedAstro's `Library/` (the calculation core, no ASP.NET/Blazor/Azure
dependencies bundled in) is MIT-licensed and could, in principle, be:
- read for algorithm reference (no restriction at all — even copying code
  outright is legally fine under MIT, just requires the notice+license text
  to travel with any copied files), or
- ported/rewritten into Python and merged into `app/astro/` with an
  attribution comment.

But (see `02-feature-comparison.md`) it's a 60k-line C# codebase built
around `SwissEphNet` (a C# ephemeris port), Azure Table Storage, and a
Blazor/ASP.NET web front end. There is no drop-in Python surface — pulling
in "VedAstro" in practice means **reading C# and re-deriving the formula in
Python**, which is exactly the clean-room workflow we should be doing with
the AGPL repos anyway (minus the legal risk). MIT doesn't save us porting
effort; it just means we could paste-and-adapt instead of read-and-rewrite
if we ever did want a literal port of a specific calculator.

## Practical policy going forward

1. **Never `import jhora` (OpenJyotish or PyJHora) from `app/`.** Not even
   behind a feature flag, not even in `tests/`. The one exception already
   exercised in this review — a disposable one-off validation script run
   from a scratch venv, never committed, never wired into the product — is
   fine and is exactly how this review's cross-checks in
   `03-validation-cross-checks.md` were produced.
2. **Treat all three repos as read-only reference material**, the same way
   we treat BPHS/Bṛhat Jātaka/Phaladīpikā — texts to cite formulas from, not
   code to copy. `docs/technical-architecture.md`'s already-planned
   `Vimśopaka`, full `Shadbala`, `Ashtakavarga`, `Argala`, and `Panchanga`
   calculators should each get a short "verified against: PyJHora
   `strength.py`, OpenJyotish `calc/vimsopaka.py`" note in their own
   docstring/doc — citation, not code reuse.
3. **Do not commit the zips or extracted trees to git.** `public-git-repos/`
   has been added to `.gitignore` (see repo root). If someone needs to
   re-review, the zips remain on disk locally; they should never enter the
   Walmart-adjacent git history given the AGPL content inside two of them.
4. **If a genuine need for a full desktop/GUI Jyotiṣa tool ever appears**
   (not our current product direction), OpenJyotish's AGPL is a fine choice
   *to run standalone, unmodified, un-networked* (e.g., a local user-facing
   desktop app installed per-machine) — AGPL's network clause doesn't bite
   for local-only, non-networked use. That's a different product decision
   than "wire it into our FastAPI backend," and isn't recommended here
   given we already have a working, controllable engine.
