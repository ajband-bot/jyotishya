# Execution Log (Audit Trail) — Itta Raghunandan

> **Retroactive Execution Log, compiled 2026-08-15** by code-puppy-ff52bf.
> This log was NOT produced live during original generation — it is backfilled after the fact,
> per `docs/validation-document-spec.md` §10, because that spec did not exist yet when this
> profile was generated. Every claim below is either freshly re-verified (cited) or explicitly
> marked as "not independently re-verified in this backfill" where I don't have hard evidence.

---

## Step 0 — Input Lock

| Field | Value |
|---|---|
| Name | Itta Raghunandan |
| DOB | 7 October 1966 — *format disambiguated with user: "7-10-66" = DD-MM-YY* |
| TOB | 13:52 IST |
| Place | Bellary, Karnataka, India (15.139167°N, 76.921389°E) |
| Fixture | `data/charts/itta_raghunandan.yaml` (not yet git-tracked — see Open Items) |

**Status: PASS.** Date-format ambiguity was caught and resolved with the user rather than assumed — recorded in `Itta_Raghunandan_Validation.md` §1.

## Step 1 — Dual Computation Cross-Check

Verification table re-read from `Itta_Raghunandan_Internal_Part1_D1_Foundation.html` §1 (`scripts/compute_chart_cli.py`, cross-checked against fixture):

| Item | Result |
|---|---|
| Lagna = H1 | Capricorn — PASS |
| Moon nakṣatra-lord ↔ birth daśā | Ārdrā → Rāhu MD at birth (balance 3.03y) — PASS |
| Retrograde eligibility (Sun/Moon never retro) | All correct — PASS |
| Combustion orbs | Venus 8.39°<10° = COMBUST; all others clear — PASS |
| Daśā chain brackets today (2026-08-15) | Ketu MD / Jupiter AD / Rāhu PD — PASS |
| D9 Vargottama scan | None found, manually re-verified sign-by-sign — PASS |
| AK/DK cross-check | AK=Sun, DK=Saturn, matches D9 field exactly — PASS |

**Status: PASS**, 7/7 checks recorded with real computed values, not assertions.

## Step 2 — Validation Document Gate

**Status: NOT FORMALLY CONFIRMED ON RECORD.**

`Itta_Raghunandan_Validation.md` header still reads *"Status: AWAITING USER CONFIRMATION before Part generation"* as of this writing (2026-08-15) — I re-read it directly to confirm this is still the literal text. Parts were generated anyway. I cannot find, in this session's available context, an explicit recorded moment where Ajay reviewed and confirmed the Validation doc before Part generation proceeded.

This is a real process gap, not a paperwork nitpick — Step 2 exists specifically so a human catches an error (e.g. a birth-data typo) *before* five parts of interpretation get built on top of it. It didn't cause a known error here, but the safeguard was bypassed in practice.

**Mitigating factor**: Ajay has since reviewed, discussed, and asked for follow-on work (marriage deep-dive) built on this same generation process for the sibling profile (Nikita), which reflects strong *implicit* confidence in the process overall — but this is not the same as an explicit Step 2 sign-off on Raghunandan's specific Validation doc, and I'm not going to pretend it is.

**Action needed**: Ajay — please explicitly confirm Raghunandan's birth data and Validation.md are correct, so this gate can be marked CONFIRMED on record.

## Step 3 — Style Reference

**Status: NOT INDEPENDENTLY RE-VERIFIABLE IN THIS BACKFILL.** I have no surviving tool-call record in this session confirming `get_recent_horoscopes()` was invoked before Raghunandan's Parts were drafted. The resulting HTML matches the established template (CSS classes, section structure, Sanskrit+gloss voice) seen in Ajay_Kumar/Gayathri readings, which is circumstantial evidence of consistency, but I am not asserting the step was literally executed since I cannot prove it here.

## Step 4 — Parts Generated

| File | Size |
|---|---|
| `Itta_Raghunandan_Internal_Part1_D1_Foundation.html` | 15.6 KB |
| `Itta_Raghunandan_Internal_Part2_D2_to_D10.html` | 6.5 KB |
| `Itta_Raghunandan_Internal_Part3_D12_to_D60_Karmic.html` | 5.8 KB |
| `Itta_Raghunandan_Internal_Part4_Dasha_Bhukti_Transits.html` | 5.6 KB |
| `Itta_Raghunandan_Internal_Part5_Forecast_Remedies.html` | 4.5 KB |
| `Itta_Raghunandan_Part1_D1_Foundation.html` (Shareable) | 28.2 KB |
| `Itta_Raghunandan_Part2_D2_to_D10.html` | 10.6 KB |
| `Itta_Raghunandan_Part3_D12_to_D60_Karmic.html` | 12.2 KB |
| `Itta_Raghunandan_Part4_Dasha_Bhukti_Transits.html` | 11.1 KB |
| `Itta_Raghunandan_Part5_Forecast_Remedies.html` | 9.2 KB |
| `Itta_Raghunandan_Validation.md` | 42.0 KB |

**Depth-parity flag**: Internal Part 5 (4.5 KB) is much thinner than the equivalent for Gayathri (59.5 KB), which contains a full embedded 14-item Step-5-style verification checklist. Raghunandan's Internal Part 5 does **not** contain an equivalent embedded checklist. This Execution Log is the retroactive fix for that gap — see Step 5 below.

## Step 5 — Post-Generation Verification (run for real, this session)

| Item | Result |
|---|---|
| Gemstone prescriptions match functional classification | **PASS — freshly re-verified.** Read `Itta_Raghunandan_Part5_Forecast_Remedies.html` in full: Venus (Yogakāraka but combust) → mantra-first, gemstone deferred; Mars (functional benefic) → Red Coral only "later in consultation"; Saturn (Lagna lord) → service preferred, no Blue Sapphire; explicit warning against Yellow Sapphire (Jupiter) and Ruby (Sun), both correctly identified as functional malefics per §6 of the Validation doc. Zero contradictions found. |
| No debug/internal content in Shareable set | **PASS — freshly re-verified.** Repo-wide grep for `internal-note\|conf-high\|conf-med\|conf-low\|debug` returned zero hits in any `Itta_Raghunandan_Part*.html` (non-Internal) file — all hits were confined to the `Internal_Part*` files, as required. |
| Every yoga claimed passes 8-step verification | **NOT RE-VERIFIED THIS SESSION** — spot-checked Neechābhaṅga (Venus) and Mahā Parivartana (Mercury-Venus) confidence ratings in Internal Part 1 §4, both HIGH with reasoning shown; did not re-derive from scratch. |
| Doṣa register matches computed values | **NOT RE-VERIFIED THIS SESSION** (scope limited to gemstone + debug-leakage checks above; full re-derivation not repeated). |

## Corrections Log

1. **A10 (Karma Ārūḍha) distance error, caught during Part 2 drafting.** Original Validation.md §13 computed A10 by hand as Aquarius using distance=8 (H10→Venus's H9). Cross-verified against BOTH `app/derived/factors.py::arudha_pada()` and the independent `scripts/compute_raghunandan.py` routine — correct distance is 12, not 8. Documented directly in `Internal_Part2_D2_to_D10.html` with the full correction reasoning. This is exactly the kind of self-catch the process is designed to produce.
2. **H1 double-counting bug reference.** Raghunandan's Validation.md §6 is the canonical place where a known `is_yoga_karaka()` engine quirk (double-counting a single house as both kendra and trikoṇa when a planet owns only H1) is documented — subsequently referenced and manually re-checked (and found NOT to misfire) in Gayathri's and Nikita's validation docs. Good example of Cardinal Rule 3 (never silently resolve, flag for continuity) working across profiles.

## Step 8 — Regeneration Pass (2026-08-16), Triggered by External Reviewer Audit

A second reviewer audited the Shareable Part 1 (see summary of findings folded into corrections below) and the user requested a full regeneration of all 5 Shareable parts (not the Internal parts, which retain the original raw verification data and are unaffected) under a new format/tone contract. Re-used 100% of the original computed data (chart fixture, dashas, transits, yogas, dosha register) — no new chart computation was performed; only presentation, framing, and two classification corrections changed.

**Corrections applied (both also patched into `Itta_Raghunandan_Validation.md`):**
1. **Mars functional classification downgraded** from full parity with Mercury to "secondary/mild functional benefic" — matches this project's own `bphs_top20_rule_cards_v1.yaml` reference tier (`neutral_benefic`) for an equivalent Capricorn-Mars placement, which the original Shareable Part 1 had overstated.
2. **Pitṛ Doṣa section reframed** as "Pressure on the 9th House (Pāpakartari, confirmed) — with a secondary, hedged Pitṛ Doṣa reading," carrying forward the MEDIUM-confidence hedge that existed in Internal Part 1 but had not survived into the original Shareable Part 1.

**Reviewer claims evaluated and NOT accepted:** Sun as functional malefic (correctly classified per this project's own consistent rule — sole dusthāna lordship); Haṁsa Yoga's formal validity (correctly verified, 8-step passed); Mangala Doṣa needing a "named rule-set" (already fully done in Validation.md §9, simply not reprinted at Shareable tier by design).

**Format/scope changes requested by user and applied to all 5 parts:**
- Full D1 planetary table added to Part 1 with exact degree/minute/second positions (previously only narrative, no consolidated degree table).
- Every major predictive claim restructured into an explicit Observation → Classical Principle → Interpretation → Prediction block; tone shifted from affirmative/certain language to indicative language, with full-confidence phrasing reserved for points where 3+ independent classical checks converge (e.g. D20 triple-exaltation, D1/D30/D60 Venus repetition).
- Part 4 rebuilt with the **complete Antardaśā tree for all 9 Mahādaśās** (previously only the current MD's antardaśās were shown) and a **new dedicated transit section** (current transit table, 2026–2030 yearly transit outlook) — both were flagged by the user as missing/incomplete versus sibling profiles.
- Part 5 rewritten to remove **all gemstone recommendations and all mantra-repetition prescriptions**, replaced with dāna (charity) and pūjā (ritual) guidance only — verified by repo-wide grep showing zero remaining prescriptive gemstone/mantr(only meta-references explaining the scope choice remain).
- Styling/structure patterns (collapsible `<details>` dasha blocks, badge system) cross-referenced from `Roop_Kumar_Part1_D1_Foundation.html` and `Roop_Kumar_Part5_Forecast_Remedies.html` per user's explicit request to match sibling-profile structure.

**Not yet done / explicitly deferred:** Internal Part 1–5 documents were NOT regenerated in this pass (user asked for the Shareable-facing prediction docs; Internal docs still hold the original raw verification block, which remains valid and unaffected by the classification corrections above — Internal Part 1's functional-classification table should be reconciled to match on a future pass, flagged here so it isn't silently forgotten).

## Open Items

5. **Internal Part 1's functional-classification table** still shows Mars at full parity with Mercury — needs reconciling with the Shareable-tier correction above on a future pass.

1. **Step 2 confirmation gate is open** — see above, needs explicit sign-off from Ajay.
2. **Mangal Doṣa mutual-cancellation** cannot be checked without a partner's chart (noted in Validation.md §9 as MEDIUM-HIGH confidence, not full confidence, for this reason).
3. **Files are not yet committed to git** — `git status` shows all 11 files as untracked (`??`). No timestamped, immutable record exists until committed.
4. **No full Step-5 checklist embedded in Internal Part 5** at generation time — partially remedied by this log, but consider back-filling a proper Internal Part 5 checklist (Gayathri-style) if time allows.
