# 4. Recommendations & Roadmap

## Top-line recommendation

**Do not depend on, vendor, or import any of the three repos.** Keep
building `app/astro/` and `app/derived/` as planned in
`docs/technical-architecture.md`. Use these repos exactly the way we use
BPHS/Bṛhat Jātaka/Phaladīpikā: read, cite, cross-check, never copy-paste.

This is a "build vs. adopt" decision where the honest answer is neither
pure "build" nor pure "adopt" — it's **"build, but validate against these
before shipping any new calculator."** That's a genuinely more rigorous
process than either extreme, and it's cheap: PyJHora and OpenJyotish are
free to keep on disk (as zips, gitignored) as a permanent scratch-venv
reference oracle.

## Immediate actions (this week)

1. **Done as part of this review:** `public-git-repos/` added to
   `.gitignore`; `public-git-repos/extracted/` (the unzipped trees) can be
   deleted now that this review is written — the zips are the retained
   record. Run `rm -rf public-git-repos/extracted` when convenient.
2. **Add a one-line policy note to `AGENTS.md` or `docs/architecture.md`**
   pointing at this review folder, so future sessions (human or agent)
   don't re-discover-and-re-litigate the AGPL question from scratch. (See
   proposed wording at the bottom of this file.)
3. **Fold the two validation findings from `03-validation-cross-checks.md`
   into the engine backlog:**
   - Add `node_type` (`mean`/`true`) as an explicit parameter to
     `app/astro/engine.py::all_planets_sidereal()` — currently hardcoded to
     `swe.MEAN_NODE`. This was already on the roadmap
     (`technical-architecture.md` §4.1) as part of the "configurable
     ayanamsha/node/house-system" work; this review's Rahu/Ketu discrepancy
     is a concrete, chart-specific illustration of why it matters, not a
     new requirement.
   - Add rāśi-sandhi proximity (<1 degree from a sign boundary) as an
     explicit numbered condition in `docs/dosha-registry.md`'s Kuja Doṣa
     cancellation checklist — surfaced by the PyJHora cross-check as a
     legitimate factor we weren't citing explicitly.
   - Install actual Swiss Ephemeris `.se1` data files (`ephe/` — currently
     gitignored and absent, engine silently falls back to Moshier) to close
     the sub-arcminute residual gap and get JPL-grade precision. This is a
     pre-existing gap this review's Check 1 makes concretely visible, not a
     new discovery.

## Medium-term: build order for the `data_gap` calculators

Per `02-feature-comparison.md`, here is a suggested build order, sequenced
by (a) how confirmed-buildable each is against reference material, and
(b) dependency order (some need vargas infra from `technical-architecture.md`
Phase 1 first):

| Order | Calculator | Why this order | Reference material to validate against (read-only) |
|---|---|---|---|
| 1 | `node_type` config knob | Small, unblocks Check 1's gap, no dependencies | This review, Check 1 |
| 2 | Full Aṣṭakavarga (Bhinna + Sarva) | Well-trodden in both PyJHora and OpenJyotish, formula is mechanical (bindu tables per BPHS), good first "full classical, not simplified" win | `ashtakavarga.py` in both repos |
| 3 | Bhāvapada family (A1-A12 + graha ārūḍhas) | We already have Upapada (A7/UL) with the dual-formula conflict preserved (see `AGENTS.md` §6 "Known Conflicts") — extending the *same* Ārūḍha logic to the full family is incremental, not a new subsystem | `arudhas.py` (PyJHora), `calc/arudha.py` (OpenJyotish) |
| 4 | Full Pañcāṅga (tithi/yoga/karaṇa/vāra beyond what's already approximated) | Directly closes a named `data_gap` (`Ajay_Kumar_Validation.md` §2 already flags "Yoga/Karaṇa are approximate") | `panchanga/drik.py` (PyJHora) |
| 5 | Vimśopaka Bala (4 schemes) | Needs the full vargas engine (D1-D60) from Phase 1 first — sequence after that work lands | `calc/vimsopaka.py` (OpenJyotish — the only one of the two Python repos that has it as a dedicated module) |
| 6 | Full Śaḍbala (ṣaṣṭyāṁśa precision) | Hardest, most classically contested calculator (many sub-components: Sthāna/Dig/Kāla/Cheṣṭā/Naisargika/Dṛk Bala) — do this after the team has built confidence on 1-5 | `strength.py` (PyJHora), `calc/shadbala.py` (OpenJyotish) |
| 7 | Classical Argala (with strength comparison) | No reference implementation found in either Python repo (see `02-feature-comparison.md`) — this one genuinely has to be built from BPHS/Phaladīpikā text alone; budget extra review time, get a second human check before marking `ACTIVE` | None found — text-only (BPHS Ch. on Argala, Phaladīpikā) |
| 8 | Full Iṣṭa/Kaṣṭa Phala | Not clearly isolated as a standalone module in either repo either — likely folded into strength calculations; needs its own investigation pass before estimating | Investigate `strength.py`/`shadbala.py` internals further first |

**Process for every item above, no exceptions:**
1. Write the calculator in `app/astro/` or `app/derived/` from the
   classical source text first (BPHS/Bṛhat Jātaka/Phaladīpikā per
   `AGENTS.md` §7 text hierarchy) — never start by reading the reference
   repo's code.
2. Once a first version is working, run the *disposable scratch-venv cross-
   check pattern* demonstrated in `03-validation-cross-checks.md` against
   PyJHora and/or OpenJyotish for 2-3 of our existing golden fixtures
   (`ajay_kumar`, `sandeep_0700`, plus whichever fixture is most relevant to
   the calculator).
3. Document the comparison in a short note (a `docs/calculator-notes/` file,
   or a section in the calculator's own docstring) — "verified against
   PyJHora `strength.py` for fixtures X, Y on <date>; differences: none /
   explained by Z" — same rigor as this review's Check 1/Check 2 sections.
4. **Never leave the reference repo's code imported, vendored, or even
   commented-in as a "TODO: copy this."** Delete the scratch script after
   the comparison is documented; the doc note is the permanent artifact,
   not the code.
5. Only after a passing cross-check does the calculator's quality label
   graduate from `data_gap` to `computed` per `AGENTS.md` §9 — this review's
   cross-check pattern is now the recommended (not yet mandatory — propose
   promoting it to mandatory once the first 2-3 calculators have used it
   successfully) gate for that promotion.

## What NOT to do

- Do not add `pyjhora`, `openjyotish`, or any package depending on them to
  `requirements.txt` — even as a dev/test-only dependency. AGPL's network
  clause doesn't distinguish "used at runtime" from "used to generate test
  fixtures that ship with the product"; keep the boundary hard: reference
  repos never enter the dependency graph, period.
- Do not port VedAstro's C# `Library/` wholesale even though MIT allows it —
  it would introduce a second language/runtime into a project that has a
  clear, working Python stack, for no accuracy benefit over doing the same
  formula research directly from classical texts (which we're already
  equipped to do well, per the existing `docs/*.md` corpus).
- Do not treat "PyJHora agrees with us" as license to skip citing the
  primary classical source. The citation discipline in `AGENTS.md` Cardinal
  Rule 5 ("Cite sources — every interpretive claim needs a text+chapter
  reference") stays BPHS/Bṛhat Jātaka/etc., not "PyJHora `dosha.py`."
  Software cross-checks validate arithmetic; they are not a citation.

## Proposed one-line addition to project memory (for future sessions)

Suggested wording for `AGENTS.md` §3 (Mandatory Reference Index table) or a
short note near §6 (Known Conflicts):

> **Public reference repos** (`public-git-repos/*.zip`, git-ignored, never
> imported into `app/`): OpenJyotish and PyJHora are AGPL-3.0 — read-only
> reference for formula cross-checking via disposable scratch venvs only,
> never a dependency. VedAstro is MIT but C#/.NET — same read-only-reference
> treatment for stack-fit reasons. Full analysis:
> `docs/public-repo-review/`.

This has also been written to the Puppy Kennel's repo memory (see below) so
it survives even if this doc is ever moved.
