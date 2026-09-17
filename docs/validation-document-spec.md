# Validation Document Spec, HTML Template & Operational Detail

> **Status: MANDATORY.** Referenced by AGENTS.md §3 (The Process), Step 2. Split out of
> AGENTS.md purely for context-budget reasons — carries the same authority as AGENTS.md itself.

---

## 1. The Validation Document — Full 20-Section Spec

Before generating any horoscope parts, produce a **Validation Document** containing:

1. **Birth Data Table** — all input fields echoed back with Julian Day and ayanāṁśa
2. **Pañcāṅga (Five Limbs)** — Tithi (lunar day), Vāra (weekday), Nakṣatra (Moon's constellation), Yoga (Sun-Moon angular relationship), Karaṇa (half-tithi)
3. **Chart Vitality Assessment** — Lagna lord strength, Moon strength, Sun strength, planets in kendras vs dusthānas count, overall vitality rating (Strong/Moderate/Weak)
4. **D1 Planetary Positions Table** — all 10 bodies (Lagna + 9 grahas) with: rāśi, bhāva, degree, nakṣatra·pāda, nak-lord, retrograde flag, combustion flag, vargottama flag, special notes
5. **D9 Summary Table** — all bodies with D9 sign, D9 house, state, vargottama flag
6. **Functional Classification** — for the specific Lagna: which planets are functional benefics, malefics, yogakārakas, mārakas, kendrādhipati doṣa planets (cite BPHS Ch.34). This classification governs ALL subsequent interpretation and remedy prescription.
7. **Yogas Identified** — with 8-step verification status, formation logic, strength rating, activation daśā, and verse reference
8. **Yogas NOT Present** — explicitly list checked-but-absent yogas to prove thoroughness
9. **Doṣa Register** — Maṅgala Doṣa (from Lagna/Moon/Venus, with cancellation check), Kāla Sarpa, Pitṛ Doṣa, Guru Chaṇḍāla, Kemādruma, Pāpakartarī — each with status and severity (see `docs/dosha-registry.md`)
10. **Neechābhaṅga Check** — for any debilitated planet, check all 5 cancellation conditions (`docs/interpretive-frameworks.md` §H). If cancelled, flag as Neechābhaṅga Rāja Yoga.
11. **Vimśottari Daśā Timeline** — full MD chain with current MD/AD/PD stack and dates
12. **House Lordship Matrix** — all 12 houses with sign, lord, lord's house, lord's state, dispositor chain terminator, one-line verdict
13. **Ārūḍha Padas** — at minimum: AL (Lagna Ārūḍha), A10 (Karma Ārūḍha), UL (Upapada)
14. **Ātma-Kāraka & Jaimini Kārakas** — AK, AmK, BK, MK, PK, GK, DK identification with degrees
15. **Sade Sati Status** — current status, phase, historical periods, mitigation factors
16. **Chart Signature** — dominant element (fire/earth/air/water), dominant modality (cardinal/fixed/dual), dominant planet, overall personality archetype
17. **Parivartana Yogas** — check all possible mutual exchanges among 12 lords; classify type
18. **Nakṣatra Analysis** (see `docs/nakshatra-framework.md`) — Janma Nakṣatra personality profile (deity, gaṇa, motivation, nak-lord chain), gandānta flags for any planet within 3°20' of junction, puṣkara navāṁśa/bhāga positions, Tārā bala for current transit Moon, nak-lord sub-dispositor chains for Lagna + Moon + AK
19. **Top 5 Validation Questions** — life-event correlation questions (see §2 below)
20. **Proposed Part Structure** — confirm 3-part (base) or 5-part (advanced) with section titles

**Save as**: `output/{Name}_Validation.md`

**Gate**: Present to user. Proceed to Part generation ONLY after user confirms or corrects.

---

## 2. Top 5 Validation Questions — Derivation Rules

Before proceeding past the Validation Document, derive exactly 5 questions to ask the customer. These MUST be derived from the chart's most statistically impactful placements — not generic.

**Selection criteria** (pick the 5 strongest signals):
- Yogakāraka placement or absence → ask about the corresponding life domain
- Daśā transitions that bracket major life-phase boundaries (ages 18, 25, 30, 40, 50) → ask about career/marriage/health shifts at those times
- Combust or retrograde planets owning key houses (1, 5, 7, 9, 10) → ask about delays or hidden strengths in those domains
- Stelliums (3+ planets in one house) → ask about intensity in that house's domain
- Lagneśa in dusthāna (6, 8, 12) → ask about transformative or difficult early-life experiences
- Rāhu/Ketu axis houses → ask about unconventional paths or obsessions in those domains
- 7th house/lord afflictions → ask about marriage timing, complexity
- D9 Darakāraka placement → ask about spouse characteristics
- Sade Sati periods coinciding with major life events → ask about those periods
- Active doṣas → ask about corresponding life challenges
- Neechābhaṅga planets → ask about late-blooming success in those domains

**Question format**: Frame as experiential ("Did you experience..." / "Was there significance around..." / "Has your career involved...") — not as yes/no. The customer should be able to correlate easily.

**Purpose**: If 4/5 questions resonate, birth time and chart are likely accurate. If fewer than 3 resonate, consider birth-time rectification (`docs/domain-playbooks.md`) before the full reading.

---

## 3. Part Structure

### Base Version (3 Parts) — for quick readings

| Part | Label | Coverage |
|------|-------|----------|
| 1 | `D1_Foundation` | Pañcāṅga, chart vitality, Lagna analysis, all 9 grahas (6 questions each with nakṣatra personality), house lords, yogas (8-step verified), doṣas, functional classification, ārūḍhas, Jaimini kārakas, neechābhaṅga check, parivartana yogas, dispositor chains, nakṣatra analysis, chart signature, core personality |
| 2 | `Dashas_Transits` | Full daśā timeline (5-layer reading per period), current MD/AD/PD deep analysis, transit assessment (5-layer protocol), Sade Sati, marriage timing (5-pillar), career timing, timing of key life events |
| 3 | `Forecast_Remedies` | 8-week forecast using transit overlay, remedies (safety rules apply), nāḍī advice, closing blessing |

### Advanced Version (5 Parts) — full reading

| Part | Label | Coverage |
|------|-------|----------|
| 1 | `D1_Foundation` | Pañcāṅga, chart vitality, Lagna analysis, all 9 grahas (6 questions each + nakṣatra), house lords, yogas, doṣas (full register), functional classification, ārūḍhas, Jaimini kārakas, neechābhaṅga, parivartana, dispositor chains, nakṣatra deep analysis (all 9 graha nakṣatras, gandānta, puṣkara, nak-lord chains, Tārā bala), chart signature, core personality, dharma path |
| 2 | `D2_to_D10` | D2 Hora, D3 Drekkāṇa, D4 Caturthāṁśa, D5 Pañcāṁśa, D6 Ṣaṣṭhāṁśa, D7 Saptāṁśa, D9 Navāṁśa (deep with D1+D9 matrix), D10 Daśāṁśa |
| 3 | `D12_to_D60_Karmic` | D12–D60 higher vargas, past-life karma (D60), Upapada deep analysis, Kārakāṁśa, Iṣṭa-devatā |
| 4 | `Dasha_Bhukti_Transits` | Full daśā chain (5-layer reading), current stack analysis, past daśā life-mapping, transit cosmology (5-layer protocol), Sade Sati analysis, marriage timing, career timing |
| 5 | `Forecast_Remedies` | 8–12 week granular forecast, week-by-week guidance using transit micro-triggers, remedies (safety rules), mantras, gems (only for functional benefics), dāna, fasting, deity worship, yantras, nāḍī/karmic synthesis, closing blessing |

---

## 4. Post-Generation Verification Checklist

After generating all parts, verify:
- [ ] Every planetary position mentioned in text matches `compute_chart` output exactly
- [ ] Every daśā date mentioned matches the computed daśā timeline exactly
- [ ] No nakṣatra or pāda is stated without being sourced from computation
- [ ] All yogas claimed pass the 8-step verification
- [ ] All doṣas listed match the computed doṣa register
- [ ] No prediction contradicts computed evidence
- [ ] No prediction is stated without passing through 3 Lenses
- [ ] Gandānta planets flagged and interpreted
- [ ] Puṣkara positions identified and factored into strength assessment
- [ ] Janma Nakṣatra personality analysis included with deity/gaṇa/motivation
- [ ] All remedy prescriptions comply with Remedy Safety Rules
- [ ] No gemstone is prescribed for a functional malefic
- [ ] Both Internal and Shareable sets are saved
- [ ] Shareable set contains NO internal/debug content

---

## 5. Completion Summary Format

Present a summary box after every reading:
```
+=======================================================================+
|  Jyotisha Reading Complete                                            |
|  Name : {name}                                                        |
|  Born : {dob} {tob} (UTC{offset}) | {lat} N {lon} E                   |
|  Lagna: {lagna_sign} ({nakshatra} P{pada})                            |
|  MD/AD/PD: {md}/{ad}/{pd}                                             |
|  Sade Sati: {status}                                                  |
|  Chart Signature: {element}/{modality}/{dominant planet}              |
+-----------------------------------------------------------------------+
|  Internal Set ({N} parts):                                            |
|    output/{Name}_Internal_Part1_D1_Foundation.html                    |
|    ...                                                                |
|  Shareable Set ({N} parts):                                           |
|    output/{Name}_Part1_D1_Foundation.html                             |
|    ...                                                                |
|  Validation: output/{Name}_Validation.md                              |
+-----------------------------------------------------------------------+
|  Follow-up: ask any question about {name}                             |
+=======================================================================+
```

---

## 6. HTML Output Template Standard

All HTML outputs MUST use this CSS foundation:

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{Name} — Jyotish Part {N}: {Label}</title>
<script src="https://cdn.tailwindcss.com"></script>
<style>
  :root {
    --wm-blue: #0053e2; --wm-gold: #ffc220; --wm-red: #ea1100;
    --wm-green: #2a8703; --wm-gray: #374151; --wm-light: #f8fafc;
  }
  body { font-family: 'Georgia','Times New Roman',serif; background: var(--wm-light); color: var(--wm-gray); }
  .highlight { background: #fffbeb; border-left: 4px solid var(--wm-gold); padding: 1rem; }
  .verse { background: #f0f4ff; border-left: 4px solid var(--wm-blue); padding: 1rem; font-style: italic; }
  .warn { background: #fef2f2; border-left: 4px solid var(--wm-red); padding: 1rem; }
  .blessing { background: #f0fdf4; border-left: 4px solid var(--wm-green); padding: 1rem; }
  .spiritual { background: #faf5ff; border-left: 4px solid #7c3aed; padding: 1rem; }
  .dosha { background: #fff1f2; border-left: 4px solid #be123c; padding: 1rem; }
  .remedy { background: #ecfdf5; border-left: 4px solid #059669; padding: 1rem; }
  .internal-note { background: #fef9c3; border-left: 4px solid #ca8a04; padding: 1rem; } /* Internal set only */
  table { border-collapse: collapse; width: 100%; }
  th { background: var(--wm-blue); color: white; padding: 0.5rem; text-align: left; font-size: 0.85rem; }
  td { padding: 0.5rem; border-bottom: 1px solid #e5e7eb; font-size: 0.85rem; }
  tr:hover { background: #f1f5f9; }
  h1 { color: var(--wm-blue); } h2 { color: var(--wm-blue); border-bottom: 2px solid var(--wm-gold); padding-bottom: 0.5rem; }
  h3 { color: #1e3a5f; }
  .planet-tag { display: inline-block; padding: 2px 8px; border-radius: 999px; font-size: 0.75rem; font-weight: bold; }
  .combust { background: #fecaca; color: #991b1b; }
  .retro { background: #dbeafe; color: #1e40af; }
  .yogakaraka { background: #dcfce7; color: #166534; }
  .debilitated { background: #fef3c7; color: #92400e; }
  .vargottama { background: #e0e7ff; color: #3730a3; }
  .neechabhanga { background: #fce7f3; color: #9d174d; }
</style>
</head>
```

**Internal-only additions**: use `.internal-note` blocks for helper notes, confidence ratings, and debug data. These blocks are stripped in the Shareable version.

**Note on emoji**: Do not rely on emoji/unicode symbols (checkmarks, crosses) as sole content of table cells — the project's emoji filter strips them, leaving blank cells. Use text labels (Yes/No/Partial) instead.

---

## 7. Q&A Mode (Follow-up Questions)

When the user asks a follow-up (no birth data in input):

1. **Person-specific**: Load their files via `get_recent_horoscopes(person_name=X)`, answer from computed data. Apply relevant interpretive frameworks to the specific question.
2. **General Vedic question**: Answer from classical knowledge, cite texts, distinguish Parāśarī vs Jaimini schools. Reference the text hierarchy (AGENTS.md §5).
3. **Compatibility**: Load both charts, perform Aṣṭakūṭa analysis (`docs/domain-playbooks.md`), analyze 7th lords + DK cross-compatibility, D9 cross-analysis, check Maṅgala Doṣa mutual cancellation.
4. **Rectification**: If birth time is uncertain, apply Birth Time Rectification methods (`docs/domain-playbooks.md`). Examine daśā transitions against known life events.
5. **Marriage timing**: Apply Marriage 5-Pillar Framework (`docs/domain-playbooks.md`) with Five-Layer Transit Timing.
6. **Career guidance**: Apply Career Analysis Framework (`docs/domain-playbooks.md`) with current daśā and transit assessment.

---

## 8. Quality Labels (Rule Engine)

When the rule engine (`app/rules/evaluator.py`) is invoked, these are the only permitted quality labels:

| Label | Meaning |
|-------|---------|
| `computed` | Fully derived from Swiss Ephemeris output with classical logic |
| `computed_simplified` | Practical proxy used (e.g., simplified Śaḍbala instead of full classical) |
| `computed_with_conflict` | Two valid formulas disagree; both results preserved |
| `data_gap` | Required calculator not yet implemented |

No other labels are permitted. If a new quality state is needed, it must be added to this table and to the test suite's `ALLOWED_QUALITIES` set.

---

## 9. Test Suite & Regression

**Golden fixtures**: `ajay_kumar`, `sandeep_0700`

```bash
# Verify (must pass before any code merge)
.venv/bin/python tests/run_suite.py --mode verify

# Accept new baseline (explicit opt-in only)
.venv/bin/python tests/run_suite.py --mode accept-baseline
```

**Critical checks enforced**:
- Quality label taxonomy compliance
- RC-013 (Argala) and RC-020 (timing) are not `data_gap`
- Upapada conflict preservation for Ajay and Sandeep
- Combustion integrity (Mercury + Saturn for Ajay)
- Daśā chain stability on date anchor
- Aspect geometry integrity

Baselines are NEVER auto-adjusted. Every baseline change requires explicit `accept-baseline` invocation.

---

## 10. Execution Log — Audit Trail Spec (Step 7, mandatory)

Every profile MUST produce `output/{Name}_Execution_Log.md` alongside its Validation doc and Parts. This is the artifact that proves, on the record, that Steps 0-6 actually happened for THIS person — not just that a process exists in AGENTS.md. The Validation.md and Internal Parts contain evidence scattered across many files; this log collects it into one auditable place, mapped explicitly to each Step.

**Why this exists**: a general process document (AGENTS.md) describes what SHOULD happen. It does not, by itself, prove what DID happen for a specific native. Without this log, an owner cannot audit whether Step 2's confirmation gate was actually honored, whether Step 5's checklist was actually run, or what corrections were caught along the way. Given Cardinal Rule 9 (never sugarcoat) and the stakes of giving people life predictions, this log must be as honest about gaps as the readings are about difficult charts — do not retroactively mark something "done" that wasn't.

**Required sections**:

1. **Header**: name, date generated, engine/ayanāṁśa, session/agent identifier, fixture path.
2. **Step 0 — Input Lock**: exact birth data used, source (birth certificate / stated / estimated), any disambiguation needed.
3. **Step 1 — Dual Computation**: the actual verification table (Lagna, nakṣatra-lord↔dasha match, retrograde eligibility, combustion orbs, dasha-brackets-today, vargottama scan, AK/DK cross-check) with PASS/FAIL per row and where in the deliverables it's recorded.
4. **Step 2 — Validation Document Gate**: link to `{Name}_Validation.md`, and an explicit status — `CONFIRMED (date, by whom)`, `IMPLICITLY CONFIRMED (native reviewed later material built on it, no explicit sign-off recorded)`, or `NOT YET CONFIRMED`. Never mark CONFIRMED without a real basis.
5. **Step 3 — Style Reference**: which prior readings were used as the depth/tone reference.
6. **Step 4 — Parts Generated**: table of every Internal + Shareable file, file size (proxy for depth-parity check), generation date.
7. **Step 5 — Post-Generation Verification**: the full checklist from §4 above, run for real against the actual files (grep evidence cited), each item PASS / FAIL / NOT RE-VERIFIED (this session).
8. **Corrections Log**: every error caught and fixed after initial generation, with what was wrong, how it was caught, and when. This is not an embarrassment to hide — it is the strongest evidence the verification process works.
9. **Open Items**: anything not yet closed out (missing partner chart for Mangal Dosha mutual-cancellation, calculators not yet implemented, confirmation gates still open, etc.)

**Rule**: this log is retroactively backfillable when a genuine gap is found (as happened for the first two profiles under this spec), but the backfill must say so explicitly — label it "Retroactive Execution Log, compiled {date}" rather than pretending it was produced live.
