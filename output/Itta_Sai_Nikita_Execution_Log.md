# Execution Log (Audit Trail) - Itta Sai Nikita

> **Retroactive Execution Log, compiled 2026-08-15** by code-puppy-ff52bf.
> Backfilled after the fact, per `docs/validation-document-spec.md` section 10, since that spec
> did not exist when this profile was generated. Claims below are either freshly re-verified
> (cited) or explicitly marked "not independently re-verified in this backfill."

---

## Step 0 - Input Lock

| Field | Value |
|---|---|
| Name | Itta Sai Nikita |
| DOB | 20 December 1997 |
| TOB | 12:15 PM IST |
| Place | Kadiri, Andhra Pradesh, India (14.12N, 78.16E) |
| Fixture | `data/charts/itta_sai_nikita.yaml` (not yet git-tracked - see Open Items) |

**Status: PASS.** Validation.md section 1 notes "Birth data provided directly and unambiguously - no date-format disambiguation was needed for this profile" - a genuinely different, simpler case than Raghunandan's.

## Step 1 - Dual Computation Cross-Check

Verification table re-read from `Itta_Sai_Nikita_Internal_Part1_D1_Foundation.html` section 1 (`scripts/compute_nikita.py`):

| Item | Result |
|---|---|
| Lagna = H1 | Pisces, 04d05'50.6" - PASS |
| Moon nakshatra-lord <-> birth dasha | Purva Phalguni -> Venus MD at birth (balance 14.45y) - PASS |
| Retrograde eligibility | Mercury=T, Rahu=T, Ketu=T, all others F, Sun/Moon never - PASS |
| Combustion orbs | Mercury 6.91d < 14d = COMBUST under both standard and retrograde-orb conventions; all others clear - PASS |
| Dasha chain brackets today (2026-08-15) | Moon MD / Venus AD / Moon PD - PASS |
| D9 Vargottama scan | None found, manually re-verified sign-by-sign - PASS |
| AK/DK cross-check | AK=Mercury, DK=Sun, matches D9 field exactly - PASS |
| Jupiter yogakaraka status vs. known H1 double-count bug | Manually re-verified: Jupiter owns H1 and H10 as genuinely distinct houses - not a bug artifact - PASS |
| Neechabhanga cancellation | Saturn in H1 (kendra) confirmed; second independent condition (Mars exalted in same house as Jupiter) also confirmed - PASS, double-confirmed |

**Status: PASS**, 9/9 checks, including an explicit cross-reference back to a bug documented in Raghunandan's Validation.md - this is the corpus-continuity practice (Cardinal Rule 3) working as intended across profiles.

## Step 2 - Validation Document Gate

**Status: NOT FORMALLY CONFIRMED ON RECORD.**

`Itta_Sai_Nikita_Validation.md` header reads *"Status: AWAITING USER CONFIRMATION before Part generation"* - re-read directly to confirm this is still the literal text as of today. Parts were generated, and a further deep-dive (Marriage Timing Analysis) was built on top, without an explicit recorded confirmation step in between.

Same gap as Raghunandan's profile, same honest treatment: this did not cause a *known* downstream error on the base chart data, but it is a real bypass of the safeguard Step 2 exists to provide.

**Action needed**: Ajay - please explicitly confirm Nikita's birth data and Validation.md are correct, so this gate can be marked CONFIRMED on record.

## Step 3 - Style Reference

**Status: NOT INDEPENDENTLY RE-VERIFIABLE IN THIS BACKFILL.** Same honest caveat as Raghunandan's log - no surviving tool-call record in this session proves `get_recent_horoscopes()` was invoked. Structural/tonal consistency with prior readings is observable but not proof of the step.

## Step 4 - Parts Generated

| File | Size |
|---|---|
| `Itta_Sai_Nikita_Internal_Part1_D1_Foundation.html` | 15.6 KB |
| `Itta_Sai_Nikita_Internal_Part2_D2_to_D10.html` | 7.0 KB |
| `Itta_Sai_Nikita_Internal_Part3_D12_to_D60_Karmic.html` | 7.0 KB |
| `Itta_Sai_Nikita_Internal_Part4_Dasha_Bhukti_Transits.html` | 6.9 KB |
| `Itta_Sai_Nikita_Internal_Part5_Forecast_Remedies.html` | 5.6 KB |
| `Itta_Sai_Nikita_Part1_D1_Foundation.html` (Shareable) | 27.9 KB |
| `Itta_Sai_Nikita_Part2_D2_to_D10.html` | 11.2 KB |
| `Itta_Sai_Nikita_Part3_D12_to_D60_Karmic.html` | 13.8 KB |
| `Itta_Sai_Nikita_Part4_Dasha_Bhukti_Transits.html` | 12.0 KB |
| `Itta_Sai_Nikita_Part5_Forecast_Remedies.html` | 11.3 KB |
| `Itta_Sai_Nikita_Validation.md` | 35.4 KB |
| `Itta_Sai_Nikita_Marriage_Timing_Analysis.html` (follow-up deep-dive, this session's earlier work) | 22.8 KB |

**Depth-parity flag**: same pattern as Raghunandan - Internal Part 5 (5.6 KB) has no embedded Gayathri-style Step-5 checklist.

## Step 5 - Post-Generation Verification (run for real, this session)

| Item | Result |
|---|---|
| Gemstone prescriptions match functional classification | **PASS - freshly re-verified.** `Itta_Sai_Nikita_Part5_Forecast_Remedies.html`: Yellow Sapphire offered for Jupiter (Lagna lord + yogakaraka, correctly the chart's single most important planet) but explicitly gated on "mantra/charity practice established" first; Emerald explicitly withheld for combust-and-gandanta Mercury; Diamond/White Sapphire (Venus) and Blue Sapphire (Saturn) both explicitly flagged "do not amplify... without full consultation" despite Saturn's structural role in the chart's central yoga. No contradictions found. |
| No debug/internal content in Shareable set | **PASS - freshly re-verified.** Same repo-wide grep sweep as Raghunandan's log found zero `internal-note/conf-high/conf-med/conf-low/debug` hits in any non-Internal `Itta_Sai_Nikita_Part*.html` file. |
| 7th house / Mercury occupancy claim | **FAIL, CAUGHT AND FIXED this session.** `Itta_Sai_Nikita_Part4_Dasha_Bhukti_Transits.html` incorrectly stated the 7th house (Virgo) was "occupied by" Mercury. Corrected via `replace_in_file` to state Virgo/H7 is empty and Mercury (Atmakaraka, 7th lord) rules H7 from its actual seat in H9. Part 1 already had this correct - the error was isolated to Part 4. This is exactly the class of error Step 5 is supposed to catch before delivery, and it was caught late (during a follow-up marriage analysis, not the original Step 5 pass) - see Open Items. |
| Every yoga claimed passes 8-step verification | **NOT RE-VERIFIED THIS SESSION** beyond the Neechabhanga/Parivartana spot-check already covered in Step 1 above. |
| Doshas register matches computed values | **NOT RE-VERIFIED THIS SESSION** in full; Pitru Dosha's aspect-based (not conjunction-based) evidence is explicitly hedged in Validation.md section 9 - good practice, no correction needed there. |

## Corrections Log

1. **7th house occupancy error (Part 4), caught 2026-08-15 during the Marriage Timing Analysis deep-dive - not during original Step 5.** See table above. Fixed via targeted `replace_in_file`; verified clean via re-read.
2. **Emoji-filter corruption in `Marriage_Timing_Analysis.html`.** Checkmark symbols used in table cells were silently stripped by the project's emoji filter, leaving blank cells. Replaced with plain text labels (Yes/No/Partial). Lesson: never rely on unicode checkmark glyphs in HTML tables for this project - use text.
3. **Jupiter yogakaraka double-count bug explicitly re-checked and confirmed NOT to misfire** for this chart (see Step 1) - this is a positive correction-log entry: the check was run and passed, not just assumed.

## Open Items

1. **Step 2 confirmation gate is open** - needs explicit sign-off from Ajay, same as Raghunandan.
2. **The 7th-house/Mercury error was caught late** - during a follow-up deep-dive three parts and one extra document later, not during the original Step 5 pass. This is the strongest concrete evidence in either profile that Step 5 needs to be run as a literal, real checklist pass (like this log now documents) rather than an implicit assumption of correctness.
3. **Files are not yet committed to git** - `git status` shows all 12 files (including the Marriage Timing Analysis) as untracked (`??`). No timestamped, immutable record exists until committed.
4. **D60 sign-level shortcut** (`d60_scheme()` in `scripts/compute_nikita.py`) does not implement the full classical Shashtyamsha deity/lord table - flagged as MEDIUM-HIGH confidence, not full, in Internal Part 3. Genuine data_gap, correctly disclosed rather than hidden.

---

## Step 8 - Regeneration Pass (2026-08-16, second-reviewer audit response)

A second, independent Jyotisha-logic audit of Raghunandan's Part 1 surfaced a lossy-translation pattern (Internal-tier hedges not reaching the Shareable tier, absolutist language, an outdated retrograde citation). Per user request, the same audit lens plus the corrected Raghunandan format was applied to this profile, with an explicit added emphasis on house/lord/aspect tracing and a 4-layer Observation/Classical-Principle/Interpretation/Prediction synthesis for every graha and every bhava (not just headline yogas).

### New finding this pass: a second, distinct engine bug (bigger than the 7th-house slip above)

While re-verifying the Step 1 yogakaraka check above (previously marked PASS), a direct comparison against this project's own `app/rules/bphs_top20_rule_cards_v1.yaml::yoga_karaka_by_lagna` reference table revealed a contradiction: that table explicitly lists **`Pisces: {yoga_karaka: null, most_benefic: Mars, reason: H9_lord}`** - i.e. Pisces has *no* classical yogakaraka, and Mars (exalted, 9th lord) is this Lagna's designated most-benefic planet. This directly contradicts the earlier Step-1 finding, which had manually "confirmed" Jupiter as yogakaraka.

**Root cause**: `app/derived/factors.py::is_yoga_karaka()` returns True for any planet owning one kendra AND one trikona house, without excluding the Lagna's own trivial trikona status for the Lagna lord. Since Jupiter (Pisces Lagna lord) owns H1 (Lagna, always trikona) and H10 (kendra), the naive check fires - a false positive. The earlier Step-1 "manual re-verification" checked only that the two houses were genuinely distinct (they are), but did not check the deeper classical restriction that this project's own reference table encodes. **This is a new, separate bug from the Raghunandan H1-double-counting bug** (though it lives in the same function) and likely affects every dual/common-sign Lagna (Gemini, Virgo, Sagittarius, Pisces - the four other `yoga_karaka: null` entries in the same table).

### Corrections applied this pass

| # | File(s) | Correction |
|---|---|---|
| 1 | `Validation.md` §6 | Jupiter re-labeled 
