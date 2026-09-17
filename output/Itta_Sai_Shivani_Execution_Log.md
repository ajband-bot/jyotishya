# Execution Log — Itta Sai Shivani

> Audit trail proving AGENTS.md §2 Steps 0-7 were actually performed for this profile.

---

## Step 0 — Input Lock

All required fields provided directly by the user in one message: name, dob (14–9–1999, unambiguously DD-MM-YYYY since 14 cannot be a month), tob (02:05 IST), location (Kadiri), lat (14.12° N / 14°7'N), lon (78.17° E / 78°10'E). No halt required.

## Step 1 — Dual Computation

- **Pass 1**: `scripts/compute_chart_cli.py` run via `app.astro.engine` (Swiss Ephemeris, Lahiri ayanāṁśa, whole-sign houses) — full JSON captured (Lagna, D1×10 grahas, D9, house lords, yogas, dashas).
- **Pass 2 (independent)**: bare-Python re-derivation of pañcāṅga (tithi/yoga/karaṇa from elongation math), all 10 nakṣatra/pāda values, gaṇḍānta scan (all 3 junctions), combustion distances, Kāla Sarpa hemisphere check, weekday — **full match against Pass 1, zero discrepancies.**
- **Pass 3 (add-on, this profile only)**: Puṣkara Navāṁśa/Bhāga scan against the 24-division table, and direct function calls to `app.derived.factors.arudha_pada()`, `upapada_lagna_project_legacy()`, and `is_yoga_karaka()` against a reconstructed chart dict — used to verify every Ārūḍha, Jaimini kāraka, and the flagged engine bug claim against actual project code, not just manual arithmetic.
- **Divisional charts**: D2, D3, D4, D7, D10, D12, D16, D20, D24, D27, D30, D40, D45, D60 computed fresh via the project's standard portion-based scheme functions (same schemes as `scripts/compute_nikita.py`) — no fixture existed for these prior to this profile.

No mismatches found at any stage. No halt triggered.

## Step 2 — Validation Document

`output/Itta_Sai_Shivani_Validation.md` produced covering all 20 mandated sections plus a Key Risk Flags appendix. Presented to user for confirmation. **User confirmed and requested Part generation** in the following turn.

## Step 3 — Style Reference

`output/Itta_Sai_Nikita_Part1-5*.html` (most recently generated profile, same Kadiri family) read in full as the structure/tone/depth reference before drafting Shivani's Parts — matched: Observation→Principle→Interpretation→Prediction framing, HTML template/CSS conventions, planet-tag styling, Internal-document debug/confidence-table format, and the "never sugarcoat, always pair with a growth reframe" balance.

## Step 4 — Generate Parts

Both Internal and Shareable sets produced for all 5 Parts (10 files total):

| Part | Shareable | Internal |
|------|-----------|----------|
| 1 — D1 Foundation | Itta_Sai_Shivani_Part1_D1_Foundation.html | Itta_Sai_Shivani_Internal_Part1_D1_Foundation.html |
| 2 — D2 to D10 | Itta_Sai_Shivani_Part2_D2_to_D10.html | Itta_Sai_Shivani_Internal_Part2_D2_to_D10.html |
| 3 — D12 to D60 Karmic | Itta_Sai_Shivani_Part3_D12_to_D60_Karmic.html | Itta_Sai_Shivani_Internal_Part3_D12_to_D60_Karmic.html |
| 4 — Daśā/Bhukti/Transits | Itta_Sai_Shivani_Part4_Dasha_Bhukti_Transits.html | Itta_Sai_Shivani_Internal_Part4_Dasha_Bhukti_Transits.html |
| 5 — Forecast/Remedies | Itta_Sai_Shivani_Part5_Forecast_Remedies.html | Itta_Sai_Shivani_Internal_Part5_Forecast_Remedies.html |

Every framework in `docs/interpretive-frameworks.md`, `docs/dosha-registry.md`, `docs/domain-playbooks.md`, `docs/nakshatra-framework.md` applied: 8-step yoga verification, 5-condition Neechābhaṅga check, 5-layer daśā/transit-timing protocol (marriage Part 4 §4, career Part 4 §5), Marriage Five-Pillar framework, remedy safety rules (gemstone-eligibility audit, priority order dāna→pūjā).

## Step 5 — Post-Generation Verification

- All positions/dates cross-checked against Pass 1/2/3 computation — no discrepancies.
- All yoga/doṣa claims traced to their verification tables in the Validation doc and Part 1 Internal §4.
- No gemstone recommended for any planet — audited explicitly in Part 5 Internal §1 against the four functional-classification/combustion/yogakāraka tests; family-precedent policy (dāna+pūjā only, no gemstone/mantra specifics) applied consistently with Nikita/Raghunandan readings.
- Shareable set scanned for debug content, confidence percentages, or "AI" language — none found.
- All 10 HTML files passed a Python `html.parser` structural parse check with zero errors.
- Known corpus conflict (Upapada canonical Virgo vs. legacy Gemini) preserved in both Validation doc §13 and Part 3 §4 — not silently resolved.
- Engine bug (`is_yoga_karaka()` false-flagging Mercury as yogakāraka for Gemini Lagna, same root cause as Nikita's Pisces/Jupiter case) documented in Validation §6 and Part 1 Internal §1; correction applied consistently — Mercury is never called "yogakāraka" in any Shareable file.
- Self-correction transparency: an initial mis-filing of Gajakesarī Yoga under "not present" during Validation-doc drafting was caught and corrected within the same session, documented explicitly in Validation §8 and Part 1 Internal §5 rather than silently fixed and hidden.

## Step 6 — Completion Summary

**Lagna**: Gemini, 29°17'46.7" — Vargottama (D9 Lagna also Gemini), time-sensitive (~2.8 min buffer).
**Current daśā**: Saturn MD (2025–2044) / Saturn AD (2025–2028) / Venus PD (04 Mar–03 Sep 2026).
**Sade Sati**: Not active (past cycle 2009–2017; next cycle 2038–2046).
**Headline findings**: Bhadra Yoga (Mercury, combustion-tempered), Gajakesarī Yoga (Jupiter-Moon, D9-confirmed), Neechābhaṅga on Saturn (single condition — D9 exaltation), Kendrādhipati Doṣa on Jupiter (D9-exalted), genuine Moon⇄Venus Parivartana, and a second confirmed instance of the `is_yoga_karaka()` engine bug.

## Step 7 — Execution Log

This document. All 7 steps of AGENTS.md §2 completed and verifiably documented for Itta Sai Shivani.

---

**Outstanding items** (consistent with standing project data gaps, AGENTS.md §6): Internal-tier docs not yet cross-reconciled against a dedicated Marriage_Timing_Analysis or Speaker_Cheatsheet deliverable for this profile (same standing gap noted for Raghunandan/Nikita); no dedicated Iṣṭa Devatā calculator exists in `app/derived/` (manual four-method synthesis used, per standing practice); `tests/run_suite.py` could not be run this session due to a pre-existing broken `.venv` (missing `pip`/`PyYAML`) — unrelated to this profile's changes (only a new YAML fixture was added, no code touched).
