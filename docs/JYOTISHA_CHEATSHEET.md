# Jyotisha Learning Cheat Sheet

> **Generated 2026-09-17 by `scripts/generate_cheatsheet.py` from `app/engine/cheatsheet/concepts.py` -- never hand-edit this file, it will be overwritten. This is the Phase 7 'learning platform' artifact: read it top to bottom and you should come away understanding both the classical Jyotisha concept AND exactly how (and how completely, and with what caveats) this project computes it.**

For deeper prose than this summary provides, follow each entry's **Primary citation** to the referenced `docs/*.md` file or classical text. For live, per-chart validation of every claim below, see the Cheat-Sheet Cross-Validation Console (`GET /api/v2/cheatsheet/claims`, `cheatsheet_claims` DB table) -- this document describes what SHOULD be true; that console confirms whether it currently IS true.

**40 concepts** across **10 categories**, spanning every layer of `AGENTS.md`'s Process (Truth -> Derived -> Rules -> Engine) and every classical topic this codebase claims to implement.

## Quality label legend

| Label | Meaning |
|---|---|
| `computed` | Full classical-precision derivation, cross-checked where a reference exists. |
| `computed_simplified` | A practical proxy or compositional synthesis -- honestly downgraded even when every input resolves cleanly. |
| `computed_with_conflict` | Two source formulas disagree; both are preserved, never silently reconciled. |
| `data_gap` | Genuinely not implemented (or, for a handful of process/meta entries, not a calculator at all) -- never guessed or faked. |

## Classical text hierarchy

When texts conflict: **BPHS** (primary Parasari authority) > Brihat Jataka > Phaladipika > Saravali > Sarvartha Cintamani (primary transit-methodology authority) > Jataka Parijata > Uttara Kalamrita > Nakshatra Cintamani. Jaimini-specific topics (karakas, chara dasha, karakamsha) defer to the Jaimini Sutras (Sanjay Rath commentary primary). See `AGENTS.md` §7.

## Foundations -- Lagna, Karakatva, Dignity, Functional Nature, Aspects, Combustion

### Ascendant and the whole-sign house system (Lagna / Bhāva)

- **Classical definition:** The rāśi (sign) rising on the eastern horizon at birth is the Lagna (H1). This project uses whole-sign houses: the Lagna's entire sign is H1, the next sign is H2, and so on -- a planet's house is purely a function of which sign it occupies relative to the Lagna sign, never sub-divided by degree.
- **Primary citation:** BPHS Ch.3-4
- **Quality label:** `computed`
- **Implemented at:** `app.astro.engine:all_planets_sidereal`
- **Caveats:**
  - Whole-sign only -- no Placidus/Koch/Equal-house alternative is implemented; `house_system: whole_sign` is recorded per-fixture but not yet actually switchable.
- **Cross-check status:** Sign/Lagna placements cross-checked against PyJHora to within 1 arc-second (docs/public-repo-review/03-validation-cross-checks.md Check 1).

### Planetary significations (what each graha 'is about') (Kārakatva)

- **Classical definition:** Each of the 9 grahas classically signifies a fixed set of life domains -- e.g. Jupiter: wisdom/wealth/children/guru; Saturn: longevity/discipline/labor. This project's KARAKATVA table is the shared vocabulary every domain synthesis (career, dasha narrative) composes from, rather than re-describing planets ad hoc.
- **Primary citation:** BPHS Ch.3, cross-checked against Sarvārtha Cintāmaṇi
- **Quality label:** `computed`
- **Implemented at:** `app.knowledge.planets:KARAKATVA`

### Exaltation, debilitation, own-sign, and moolatrikona dignity (Uccha / Nīcha / Svakṣetra / Mūlatrikoṇa)

- **Classical definition:** Each planet has one exaltation sign (peak strength), one debilitation sign (weakest), one or two own signs, and (for most) a moolatrikona sign/degree-range distinct from its own sign. Dignity feeds almost every downstream calculator: Shadbala's Sthana Bala, Neechabhanga checks, remedy gemstone gating, yoga detection.
- **Primary citation:** BPHS Ch.4
- **Quality label:** `computed`
- **Implemented at:** `app.derived.dignities:naisargika_relationship`

### A planet's benefic/malefic role is Lagna-relative, not fixed (Kārya-kāraka-tva (functional benefic/malefic))

- **Classical definition:** AGENTS.md Cardinal Rule 7, the single most important rule in this codebase: a naturally benefic planet ruling a dusthāna (6/8/12) is FUNCTIONALLY malefic for that Lagna; a naturally malefic planet ruling a kendra/trikoṇa is FUNCTIONALLY benefic. Every remedy, every yoga-karaka call, every 'is this placement good' verdict in this project routes through this classification, never natural nature alone.
- **Primary citation:** BPHS Ch.34
- **Quality label:** `computed`
- **Implemented at:** `app.derived.functional_nature:functional_nature_report`
- **Caveats:**
  - Rahu/Ketu are excluded -- nodes don't own signs in core BPHS doctrine, so sign-lordship-based functional nature doesn't apply; their functional role via nakshatra/conjunction lordship is a disclosed data_gap, not guessed.

### Planetary aspects (special + universal 7th) (Graha Dṛṣṭi)

- **Classical definition:** Every planet aspects the 7th house from itself; Mars additionally aspects 4th/8th, Jupiter 5th/9th, Saturn 3rd/10th. This one function is shared by doṣa cancellation checks, yoga detection, and the full house-network graph -- never re-implemented per caller.
- **Primary citation:** BPHS Ch.4
- **Quality label:** `computed`
- **Implemented at:** `app.derived.aspects:graha_drishti_houses`
- **Caveats:**
  - Rāśi-dṛṣṭi (sign-to-sign, not planet-based) is not implemented -- data_gap.

### A planet too close to the Sun loses strength (Asta / Combustion)

- **Classical definition:** Planets within a classical orb of the Sun are 'combust' and weakened -- a factor in Shadbala, remedy gemstone gating (never recommend a gem for a combust planet), and Ishta/Kashta Phala.
- **Primary citation:** BPHS Ch.27 (orb table)
- **Quality label:** `computed`
- **Implemented at:** `app.astro.engine:is_combust`

## Divisional Charts & Arudha -- Vargas, Vimsopaka Bala, Bhavapada

### Divisional charts D1-D60 (Varga / Aṁśa)

- **Classical definition:** Each rāśi is further subdivided (D9 = Navāṁśa for marriage/dharma, D10 for career, D12 for parents, etc.) -- a planet's varga placement refines the D1 promise. This project computes the full D1-D60 family.
- **Primary citation:** BPHS Ch.6-7
- **Quality label:** `computed`
- **Implemented at:** `app.astro.engine:navamsha_d9`
- **Caveats:**
  - D10/D7-derived INTERPRETATION layers (career/children synthesis specifically off those vargas, beyond D1) remain a disclosed data_gap -- the vargas compute fine, the domain-specific reading of them is what's incomplete.

### 20-point varga-quality scoring across 4 classical schemes (Viṁśopaka Balā)

- **Classical definition:** Weights a planet's dignity across a fixed set of vargas (Shadvarga/Saptavarga/Dasavarga/Shodasavarga -- 6/7/10/16 charts respectively) into a single 0-20 score per scheme, each guaranteed to sum to exactly 20 by construction.
- **Primary citation:** BPHS Ch.7
- **Quality label:** `computed`
- **Implemented at:** `app.derived.vimsopaka:all_schemes_vimsopaka_bala`
- **Cross-check status:** Weight tables cross-checked exactly against PyJHora's const.py amsa_vimsopaka tables.

### Perceptional/manifested image of a house or planet (Bhāva Āruḍha (A1-A12) / Graha Āruḍha)

- **Classical definition:** The Āruḍha Pada is 'how a house appears to the world' -- counted by taking the distance from a house to its lord's occupied house, then counting the same distance forward again from the lord (with the 1st/7th exception rule). Extended here to the full A1-A12 family and to all 7 classical-planet Graha Ārūḍhas.
- **Primary citation:** Jaimini Sūtras (Sañjay Rath commentary)
- **Quality label:** `computed`
- **Implemented at:** `app.derived.bhavapada:bhavapada_report`
- **Caveats:**
  - Upapada (A12) has a KNOWN, DELIBERATELY UNRESOLVED formula conflict -- see the 'upapada_known_conflict' entry in concepts_domains.py. Never silently pick one side.

## Strength Engines -- Shadbala, Ishta/Kashta Phala, Ashtakavarga

### The 6-fold classical strength system, in Virūpa/Rūpa units (Ṣaḍbalā)

- **Classical definition:** Sthāna Balā (positional) + Dig Balā (directional) + Kāla Balā (temporal, 6 sub-parts) + Cheṣṭā Balā (motional) + Naisargika Balā (natural) + Dṛik Balā (aspectual) summed in Virūpas, converted to Rūpas (1 Rūpa = 60 Virūpas).
- **Primary citation:** BPHS Ch.27
- **Quality label:** `computed_simplified`
- **Implemented at:** `app.derived.shadbala:full_shadbala`
- **Caveats:**
  - Sthāna/Dig/Naisargika/Ayana Balā and 4 of 6 Kāla Balā sub-parts are full classical precision, built directly from the BPHS PDF text (pdftotext -layout) after OpenJyotish's own TRIAGE.md flagged real cross-implementation disagreements.
  - Varsha/Māsa Balā lords (needs a separate Ahargana calendrical derivation), Cheṣṭā Balā for the 5 non-luminary planets (8-tier motion classification), and Dṛik Balā are disclosed data_gap -- not fabricated to make the total look complete.
  - This is a SEPARATE, higher-precision engine from `simplified_shadbala` below -- not a replacement for it.

### 0-100 practical strength score used by Ishta/Kashta and varga-quality (Ṣaḍbalā (practical proxy))

- **Classical definition:** A pragmatic, non-classical-unit strength proxy (0-100) predating the full classical engine above -- kept and used deliberately where a bounded, comparable score is more useful than raw Rupas (e.g. cross-planet comparison at a glance).
- **Primary citation:** Project heuristic, not a direct BPHS formula
- **Quality label:** `computed_simplified`
- **Implemented at:** `app.derived.strengths:simplified_shadbala`
- **Caveats:**
  - Never conflate with `shadbala_classical` -- different units, different purpose, both kept.

### Benefic vs malefic potential a planet can deliver, out of 60 (Iṣṭa / Kaṣṭa Phala)

- **Classical definition:** Uccha-Raśmi (exaltation-distance strength) and Cheṣṭā-Raśmi (motional strength) combine so Iṣṭa+Kaṣṭa always sum to exactly 60 -- reconstructed algebraically from BPHS's own Rāśi-and-doubled-degree wording.
- **Primary citation:** BPHS Ch.28
- **Quality label:** `computed_simplified`
- **Implemented at:** `app.derived.ishta_kashta:classical_ishta_kashta`
- **Caveats:**
  - Sun and Moon get FULL classical precision (BPHS gives their Cheṣṭā Kendra formula explicitly). Mars/Mercury/Jupiter/Venus/Saturn are honestly `data_gap` for Cheṣṭā Raśmi specifically -- they need the same 8-tier retrograde-motion data Shadbala already discloses as incomplete; this reuses that gap rather than inventing a fix.

### Bindu (point) system for transit/gochara strength per house (Aṣṭakavarga)

- **Classical definition:** Each of the 7 classical planets contributes bindus to houses from 8 reference points (7 planets + Lagna); Sarvāṣṭakavarga (SAV) sums all 8 individual charts, used to grade how favorable a transited house currently is.
- **Primary citation:** BPHS Ch.66-71
- **Quality label:** `computed`
- **Implemented at:** `app.derived.ashtakavarga:classical_ashtakavarga`
- **Caveats:**
  - Rahu/Ketu have no classical Ashtakavarga contribution -- inherited as a disclosed gap by the Gochara engine, not silently zero-filled.
- **Cross-check status:** SAV/BAV threshold conventions cross-checked against OpenJyotish's calc/gochara.py.

## Timing -- Vimshottari Dasha, Gochara, Sade Sati

### The 120-year planetary-period timing system (Viṁśottarī Daśā)

- **Classical definition:** Moon's nakshatra at birth fixes the starting Mahādaśā lord and how much of its period is already elapsed; each Mahādaśā (MD) subdivides into Antardaśā (AD), each AD into Pratyantardaśā (PD), by the same proportional-division rule.
- **Primary citation:** BPHS Ch.46
- **Quality label:** `computed`
- **Implemented at:** `app.astro.dashas:compute_dashas`
- **Caveats:**
  - A real day-truncation bug (stacked int() truncation losing up to ~1 day per period, compounding across MD->AD->PD) was found and fixed 2026-09-16 -- see docs/dasha-precision-fix.md. If a reading predates that fix, its exact day-level PD boundaries may be off by a few days; sign/house-level conclusions are unaffected.

### Transit assessment -- current planetary positions vs. natal (Gochara)

- **Classical definition:** Combines the simple 'good house counted from Moon' heuristic with the Aṣṭakavarga bindu verdict for the same house, surfacing agreement/disagreement between the two classical methods explicitly rather than picking one silently.
- **Primary citation:** BPHS Ch.41-42, Sarvārtha Cintāmaṇi (primary transit-methodology authority)
- **Quality label:** `computed_simplified`
- **Implemented at:** `app.derived.gochara:gochara_report`
- **Caveats:**
  - Vedha (obstruction) between transiting planets is not yet implemented -- data_gap (v1's TR-003 stub).

### Saturn's 7.5-year transit window around natal Moon (Sāḍe Sātī)

- **Classical definition:** Saturn transiting the 12th, 1st, and 2nd houses counted from natal Moon sign.
- **Primary citation:** Classical transit doctrine, cross-checked against multiple sources per docs/dosha-registry.md
- **Quality label:** `computed`
- **Implemented at:** `app.astro.transits:transit_assessment`

## Doshas -- the 8 mandatory afflictions checked every reading

### Mars afflicting marriage houses from Lagna, Moon, or Venus (Maṅgala / Kuja Doṣa)

- **Classical definition:** Mars in specific houses (1/2/4/7/8/12, varying by reference point) from Lagna, Moon, and Venus independently signals marital friction -- but is heavily cancellation-gated: Mars in own sign/exaltation in the doṣa house, Jupiter/Venus aspect or conjunction, and per-Lagna dignity exceptions can all cancel or reduce it.
- **Primary citation:** BPHS Ch.77
- **Quality label:** `computed`
- **Implemented at:** `app.derived.doshas:check_mangal_dosha`
- **Caveats:**
  - A real bug (missing the 'Mars own-sign/exalted in the dosha house' cancellation condition) was found via the Phase 3 composer-vs-LLM diff and fixed -- see docs/phase3-composer-vs-llm-diff.md. Mutual cancellation via a PARTNER's chart cannot be checked from a single chart -- explicit data_gap on that specific condition.
- **Cross-check status:** Present/absent AND the specific cancellation reasons matched exactly against PyJHora's independent manglik() implementation (docs/public-repo-review/03-validation-cross-checks.md Check 2).

### All 7 classical planets hemmed between Rahu and Ketu (Kāla Sarpa Doṣa)

- **Classical definition:** All 7 classical grahas fall on one side of the Rahu-Ketu axis, with no planet crossing to the other side.
- **Primary citation:** Widely-cited Parāśarī-tradition convention
- **Quality label:** `computed`
- **Implemented at:** `app.derived.doshas:check_kala_sarpa`
- **Caveats:**
  - citation_status: pending_audit -- not yet chapter/verse-confirmed against a primary BPHS passage.

### Ancestral-karma affliction, typically Sun-Rahu/Saturn combinations (Pitṛ Doṣa)

- **Classical definition:** Sun afflicted by Rahu or Saturn (conjunction/close aspect), especially in 9th house or from 9th lord.
- **Primary citation:** docs/dosha-registry.md
- **Quality label:** `computed`
- **Implemented at:** `app.derived.doshas:check_pitru_dosha`

### Jupiter afflicted by Rahu conjunction (Guru Cāṇḍāla Yoga)

- **Classical definition:** Jupiter and Rahu conjunct within orb -- clouds Jupiter's wisdom/dharma significations.
- **Primary citation:** docs/dosha-registry.md
- **Quality label:** `computed_with_conflict`
- **Implemented at:** `app.derived.doshas:check_guru_chandala`
- **Caveats:**
  - The exact orb threshold for this conjunction is a deliberately unresolved methodology question (flagged during Phase 3, Cardinal Rule 3) -- not silently picked.

### Moon isolated -- no planets in houses 2/12 from Moon, nor conjunct (Kemadruma Doṣa)

- **Classical definition:** Moon with no planets (other than Sun) in the 2nd or 12th from it, and none conjunct -- signals emotional isolation, mitigated by several classical exceptions.
- **Primary citation:** BPHS (lunar yoga chapter)
- **Quality label:** `computed`
- **Implemented at:** `app.derived.doshas:check_kemadruma`

### A house hemmed between two malefics on either side (Pāpakartarī Yoga)

- **Classical definition:** A house flanked (2nd-from and 12th-from) by natural or functional malefics with no benefic relief -- a 'scissor' affliction.
- **Primary citation:** General Parashari principle
- **Quality label:** `computed`
- **Implemented at:** `app.derived.doshas:check_papakartari`
- **Caveats:**
  - The Phase 3 composer-vs-LLM diff caught a genuine H12 Papakartari affliction the original LLM narrative's narrower manual check had missed -- documented in docs/phase3-composer-vs-llm-diff.md as a real positive finding for the rule-engine approach.

### Mars-Saturn conjunction affliction (Ghāta Doṣa)

- **Classical definition:** Mars and Saturn conjunct within orb -- a widely-cited but not chapter/verse-pinned combination.
- **Primary citation:** Widely-cited Parāśarī-tradition convention
- **Quality label:** `computed`
- **Implemented at:** `app.derived.doshas:check_ghata_dosha`
- **Caveats:**
  - citation_status: pending_audit -- shape-only cross-check against PyJHora's dosha.py::ghata(), no code copied per AD-4.

### Rahu-Saturn conjunction affliction (Śrāpit Doṣa)

- **Classical definition:** Rahu and Saturn conjunct within orb -- the 'cursed' combination convention.
- **Primary citation:** Widely-cited Parāśarī-tradition convention
- **Quality label:** `computed`
- **Implemented at:** `app.derived.doshas:check_shrapit_dosha`
- **Caveats:**
  - citation_status: pending_audit -- same disclosed treatment as Ghata/Kala Sarpa.

## Yogas -- the compiled central tranche (of 269 named yogas total)

### Ruchaka/Bhadra/Hansa/Malavya/Sasa -- 5 'great person' yogas (Pañca Mahāpuruṣa Yoga)

- **Classical definition:** Mars/Mercury/Jupiter/Venus/Saturn respectively, in own sign or exaltation, AND occupying a kendra (1/4/7/10) from Lagna.
- **Primary citation:** BPHS Ch.75
- **Quality label:** `computed`
- **Implemented at:** `app.derived.yogas:check_pancha_mahapurusha_yogas`

### Kendra-trikona lord combinations, and cancelled-debility elevation (Rāja Yoga / Nīcabhaṅga Rāja Yoga)

- **Classical definition:** A kendra lord (1/4/7/10) combining with a trikoṇa lord (1/5/9) classically produces Rāja Yoga. Nīcabhaṅga specifically cancels a planet's debility when the sign lord of its debilitation sign occupies a kendra from Lagna, often elevating rather than merely neutralizing the placement.
- **Primary citation:** BPHS Ch.34, Ch.75-76
- **Quality label:** `computed`
- **Implemented at:** `app.derived.yogas:check_neechabhanga_raja_yoga`
- **Caveats:**
  - Full generic Raja Yoga detection (RC-018 in the v1 corpus) remains genuinely unimplemented in both v1 and v2 -- honestly `data_gap`, not silently assumed covered by Neechabhanga alone.

### A planet owning BOTH a kendra and a trikona (excluding H1's trivial overlap) (Yoga-Kāraka)

- **Classical definition:** For 6 Lagnas (Taurus/Libra->Saturn, Cancer/Leo->Mars, Capricorn/Aquarius->Venus) one planet owns both a kendra and a trikoṇa via two DIFFERENT signs, making it exceptionally auspicious. H1 is excluded from both sides of the test by design -- otherwise every dual-owning lagna lord would be mis-flagged.
- **Primary citation:** BPHS Ch.34
- **Quality label:** `computed`
- **Implemented at:** `app.derived.factors:is_yoga_karaka`
- **Caveats:**
  - This exact H1-exclusion bug was independently found in two separate narrative readings (Pisces/Jupiter, Gemini/Mercury lagna) before being fixed at the source -- see the function's own docstring.

### Moon-relative and named wealth/intelligence yogas (Sunapha / Anapha / Durudhāra / Gajakesarī / Kahala / Śaṅkha / Lakṣmī / Vāsumatī / Amala / Budha-Āditya / Cāndra-Māṅgala)

- **Classical definition:** A family of yogas defined by planets in specific houses relative to the Moon or Lagna (2nd/12th from Moon, Jupiter-Moon kendra relationships, Mercury-Sun conjunction, etc.).
- **Primary citation:** BPHS + Saravali (multiple chapters, per-yoga)
- **Quality label:** `computed_simplified`
- **Implemented at:** `app.derived.yogas:compute_all_yogas`
- **Caveats:**
  - This project compiles ~20 classically central yogas out of 269 distinct named yogas identified in PyJHora's yoga.py -- the remaining ~249 (mostly niche, e.g. specific-affliction yogas) are an explicitly tracked backlog, not silently dropped. See docs/yoga-compilation-backlog.md.

### Dusthana lords in mutual exchange/combination reverse into a positive (Viparīta Rāja Yoga)

- **Classical definition:** Lords of the 6th/8th/12th houses combining with each other (rather than with kendra/trikona lords) paradoxically produce a favorable result.
- **Primary citation:** BPHS Ch.76
- **Quality label:** `computed`
- **Implemented at:** `app.derived.yogas:check_viparita_raja_yoga`

## Nakshatras -- 27 lunar mansions, Gandanta/Abhukta Mula

### The 27 lunar mansions -- id, lord, deity, gaṇa, tattva, yoni, motivation, pada (Nakṣatra)

- **Classical definition:** Each planet's sidereal longitude falls in one of 27 nakshatras (13°20' each), each with its own ruling planet, deity, temperament (gaṇa), and pada (quarter) that bridges to the D9 chart.
- **Primary citation:** BPHS + Nakṣatra Cintāmaṇi
- **Quality label:** `computed`
- **Implemented at:** `app.derived.nakshatra_analysis:nakshatra_analysis_report`

### Sensitive water-fire sign junctions, and the tighter Jyeshtha-Mula sub-case (Gaṇḍānta / Abhukta Mūla)

- **Classical definition:** The three junctions between a water sign's last nakshatra and the next fire sign's first (Cancer-Leo, Scorpio-Sagittarius, Pisces-Aries) carry a 3°20' orb of heightened sensitivity. The Jyeshtha-Mula junction additionally has a much tighter 48-arcminute 'Abhukta Mula' sub-zone considered especially inauspicious classically.
- **Primary citation:** docs/nakshatra-framework.md §5
- **Quality label:** `computed`
- **Implemented at:** `app.derived.nakshatra_analysis:check_gandanta`

## Interventions -- Argala

### Support/obstruction channels acting on a house from 2nd/4th/11th/5th (and their opposites) (Argala / Vipārīta Argala)

- **Classical definition:** Planets in the 2nd, 4th, 11th, and 5th houses from a reference point create Argala (intervention/support); planets in the 12th, 10th, 3rd, and 9th (the counter-houses) create obstruction (Virodhargala). 3+ malefics in the 3rd-from counter-house reverses obstruction into a favorable Vipārīta Argala signal.
- **Primary citation:** BPHS Ch.31
- **Quality label:** `computed_simplified`
- **Implemented at:** `app.derived.interventions:practical_argala`
- **Caveats:**
  - Built directly from BPHS Ch.31 text via pdftotext -layout -- NO reference repo (PyJHora, OpenJyotish, or the earlier VedAstro) has ANY Argala implementation to cross-check against (confirmed by grep across all three, docs/public-repo-review/02-feature-comparison.md). A real gap was found and fixed while building this: the pre-existing engine only checked 3 of the 4 named support/obstruction channels (missing 5th/9th) -- same category of fix as the Mangal Dosha cancellation bug.
  - Quarter-based (7°30') fine-grained nullification (also named in BPHS v.4-5) is disclosed as not attempted -- a further-precision candidate, not silently covered.
- **Cross-check status:** No reference repo has this feature at all -- text-only build, extra review pass per build_plan.md Phase 6's own instruction.

## Domain Syntheses -- Marriage, Career, Remedies

### 7th House + 7th Lord + Venus/Jupiter Karaka + Darakaraka + Upapada, read together (Pañca-Stambha (Five-Pillar synthesis, project term))

- **Classical definition:** No single classical factor decides marriage outcomes -- this project's synthesis composes the 7th house/lord placement, the natural marriage karaka (Venus for a male chart, Jupiter for a female -- both ALWAYS computed, gender-agnostic at context-build time), the Jaimini Darakaraka (D1+D9), and the Upapada, into one report.
- **Primary citation:** docs/domain-playbooks.md, Marriage_Guide_Part1-4.md
- **Quality label:** `computed_simplified`
- **Implemented at:** `app.derived.marriage_analysis:five_pillar_marriage_report`
- **Caveats:**
  - Zero new astrology math -- composed entirely from already-verified primitives (lord_placements, functional_nature, D9, bhavapada).

### 36-point guna matching, inter-chart aspects, and D9 cross-checks for two charts (Aṣṭakūṭa Milāpa + Synastry + D9 Triple Agreement)

- **Classical definition:** Aṣṭakūṭa scores 8 kūtas (Varna/Vasya/Tara/Yoni/Graha-Maitri/Gana/Bhakut/Nadi) out of 36; synastry checks 7 inter-chart Venus/Jupiter/7th-lord indicators; D9 cross-compatibility applies 5 rules across both charts' Navamsha.
- **Primary citation:** Marriage_Guide_Part2-4.md
- **Quality label:** `computed`
- **Implemented at:** `app.derived.compatibility:ashtakuta_report`
- **Caveats:**
  - Found and fixed a real, repeated D9-computation bug in 3 existing corpus documents for Ajay Kumar during this build (guide claimed D9 Lagna=Pisces; independently re-derived twice, engine computes Virgo -- corpus was wrong, engine is trusted). See docs/marriage-compatibility-notes.md.

### Ranked significators scanned across dasha windows, transit windows, and D9 confirmation (Daśā / Gochara / D9 Triple Agreement)

- **Classical definition:** Marriage timing is judged 'possible/confirmed/certain' by how many of the three independent methods agree on the same window, never by any single method alone.
- **Primary citation:** Marriage_Guide_Part3.md §9.1
- **Quality label:** `computed_simplified`
- **Implemented at:** `app.derived.marriage_timing:marriage_timing_report`

### 10th House / 10th Lord synthesis reusing Karakatva's professions list

- **Classical definition:** 10th house occupants classify into profession-types by classical convention; the 10th lord's placement and identity (via its own Karakatva professions) both contribute; Yoga-Karaka and Kendradhipati-Dosha flags wrap the existing functional-nature engine verbatim.
- **Primary citation:** docs/domain-playbooks.md
- **Quality label:** `computed_simplified`
- **Implemented at:** `app.derived.career_analysis:career_analysis_report`
- **Caveats:**
  - A10 (Arudha of the 10th) and D10-derived interpretation layers remain the pre-existing disclosed data_gap -- not claimed closed by this synthesis.

### Every gemstone recommendation is gated through functional nature, never natural nature alone (Upāya (remedy) Safety Rules)

- **Classical definition:** A gemstone is only appropriate for a genuinely functional-benefic, weak/afflicted, non-combust planet. Saturn additionally needs to be a genuine yoga-karaka (not merely functional-benefic) before a blue sapphire is ever indicated; Rahu needs to be well-placed with a strong dispositor. A functional malefic NEVER gets a gemstone -- dāna (charity) of that planet's significations is prescribed instead.
- **Primary citation:** docs/domain-playbooks.md Remedy Safety Rules
- **Quality label:** `computed`
- **Implemented at:** `app.derived.remedies:remedy_report`
- **Caveats:**
  - Safety-critical: a dedicated cross-check test guards 'never gemstone a functional malefic' across every fixture -- this is the one place in the codebase where a bug would translate into genuinely harmful advice, treated with matching rigor.

## Meta -- how to read this project's own honesty machinery

### Two different, both-preserved formulas for the same classical concept (Upapada Lagna (UL))

- **Classical definition:** The canonical Āruḍha-distance formula (12th-house Āruḍha, standard exception rule) and this project's corpus guides' own inclusive-count formula disagree on Upapada for at least two people (Ajay: Aries vs Sagittarius; Sandeep: same class of disagreement). AGENTS.md Cardinal Rule 3 forbids silently resolving this.
- **Primary citation:** AGENTS.md §6 Known Conflicts
- **Quality label:** `computed_with_conflict`
- **Implemented at:** `app.derived.factors:upapada_lagna_project_legacy`
- **Caveats:**
  - The canonical formula is the recommended default, but BOTH values are always computed and surfaced side by side -- never pick one and discard the other.

### The 4 permitted honesty labels every rule/calculator output carries

- **Classical definition:** `computed` = full classical-precision derivation. `computed_simplified` = a practical proxy or compositional synthesis, honestly downgraded even when every input resolves cleanly. `computed_with_conflict` = two source formulas disagree and both are preserved. `data_gap` = genuinely not implemented -- never guessed. No other label is permitted anywhere in this codebase's rule engine.
- **Primary citation:** docs/validation-document-spec.md §8-9
- **Quality label:** `computed`
- **Implemented at:** `app.rules.schema:RuleEvaluation`

### The order used to resolve disagreements between classical texts

- **Classical definition:** BPHS (primary Parasari authority) > Brihat Jataka > Phaladipika > Saravali > Sarvartha Cintamani (primary transit-methodology authority) > Jataka Parijata > Uttara Kalamrita > Nakshatra Cintamani. Jaimini-specific topics (karakas, chara dasha, karakamsha) instead defer to the Jaimini Sutras (Sanjay Rath commentary).
- **Primary citation:** AGENTS.md §7
- **Quality label:** `data_gap`
- **Implemented at:** _(documentation/process concept, not a calculator)_
- **Caveats:**
  - Not itself a calculator -- a documentation/process rule; code_ref is intentionally None, not a mismatch.

---

*This document is generated, not authored -- it can never silently drift from the code it describes the way hand-written prose can. Re-run `scripts/generate_cheatsheet.py` after any change to `app/engine/cheatsheet/concepts.py`, and `scripts/sync_db.py` to refresh the DB-backed `cheatsheet_concepts` table alongside it.*