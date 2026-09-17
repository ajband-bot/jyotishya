# Public Git Repo Review — Index

> Requested by Ajay (2026-09-16): three public repos were dropped into
> `public-git-repos/` as zips. This review validates them, cross-checks their
> output against our own `output/` artifacts, and recommends how (if at all)
> to use them going forward.

**TL;DR: Do not adopt any of the three as a dependency or vendored codebase.
Two are AGPL-3.0 (viral copyleft — a real legal risk for anything we build on
top and ship/host), and the third (MIT) is a 60k-line C#/.NET monorepo that
doesn't fit our Python/FastAPI stack. All three are however excellent
*reference material* — read them, learn their formulas, validate our numbers
against them, cite them in our docs — never copy their code into `app/`.**

Our own engine (`app/astro/engine.py`) was cross-checked against PyJHora
(the most respected of the three, upstream of OpenJyotish) for Ajay Kumar's
chart and matched to within **~1 arc-minute** on Lagna + all 7 classical
grahas, and produced an **identical Kuja Doṣa verdict with matching
cancellation reasons**. That is strong independent evidence our pipeline is
already correct — see `03-validation-cross-checks.md`.

## Files in this review

| File | What's in it |
|---|---|
| [`01-license-and-legal.md`](01-license-and-legal.md) | License text findings for all three repos, why AGPL is disqualifying, what MIT does/doesn't buy us |
| [`02-feature-comparison.md`](02-feature-comparison.md) | Line-count/feature-matrix comparison against our own `app/`, mapped directly to the `data_gap` list in `AGENTS.md` §6 |
| [`03-validation-cross-checks.md`](03-validation-cross-checks.md) | Two independent sample checks: planetary positions + Kuja Doṣa for Ajay Kumar, our output vs. PyJHora's own computation |
| [`04-recommendations-roadmap.md`](04-recommendations-roadmap.md) | Concrete next steps: what to build, in what order, with a "reference-only, clean-room" workflow spelled out |

## What was reviewed

| Repo | Zip size | Uncompressed | Language | License |
|---|---|---|---|---|
| `OpenJyotish-main.zip` | 3.1 MB | ~8 MB (270 files) | Python (CLI/GUI/TUI) | **AGPL-3.0-or-later** |
| `PyJHora-main.zip` | 149.7 MB | ~282 MB (525 files) | Python (library + PyQt6 GUI) | **AGPL-3.0-or-later** |
| `VedAstro-master.zip` | 451.5 MB | ~967 MB (4014 files) | C# / .NET (ASP.NET API + Blazor site + mobile) | MIT |

Extraction was done to `public-git-repos/extracted/` for this review only;
that directory is now git-ignored (see `.gitignore` update) and can be safely
deleted to reclaim ~1.8 GB — the source zips stay as the record of what was
reviewed. Re-run `unzip <name>.zip -d extracted/` if you need to dig in again.
