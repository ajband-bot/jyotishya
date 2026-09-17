"""Concept registry, part 1 of 2: Foundations, Vargas/Arudha, Strength
engines, and Timing. See app/engine/cheatsheet/concepts.py (the thin
aggregator module) for the full editorial-rule docstring that applies to
every entry across both halves of this registry -- split purely to respect
this project's own 600-line-per-file guideline, not a change in scope or
ownership; both halves are equally authoritative.
"""
from __future__ import annotations

from app.engine.cheatsheet.models import ConceptEntry

CONCEPTS_FOUNDATIONS: list[ConceptEntry] = [
    # ---------------------------------------------------------------- #
    # Foundations
    # ---------------------------------------------------------------- #
    ConceptEntry(
        concept_id="lagna_whole_sign_houses",
        category="foundations",
        sanskrit_term="Lagna / Bhāva",
        english_gloss="Ascendant and the whole-sign house system",
        classical_definition=(
            "The rāśi (sign) rising on the eastern horizon at birth is the Lagna (H1). "
            "This project uses whole-sign houses: the Lagna's entire sign is H1, the next "
            "sign is H2, and so on -- a planet's house is purely a function of which sign "
            "it occupies relative to the Lagna sign, never sub-divided by degree."
        ),
        primary_citation="BPHS Ch.3-4",
        code_ref="app.astro.engine:all_planets_sidereal",
        quality_label="computed",
        caveats=[
            "Whole-sign only -- no Placidus/Koch/Equal-house alternative is implemented; "
            "`house_system: whole_sign` is recorded per-fixture but not yet actually switchable.",
        ],
        cross_check_note="Sign/Lagna placements cross-checked against PyJHora to within 1 arc-second (docs/public-repo-review/03-validation-cross-checks.md Check 1).",
    ),
    ConceptEntry(
        concept_id="karakatva",
        category="foundations",
        sanskrit_term="Kārakatva",
        english_gloss="Planetary significations (what each graha 'is about')",
        classical_definition=(
            "Each of the 9 grahas classically signifies a fixed set of life domains -- "
            "e.g. Jupiter: wisdom/wealth/children/guru; Saturn: longevity/discipline/labor. "
            "This project's KARAKATVA table is the shared vocabulary every domain synthesis "
            "(career, dasha narrative) composes from, rather than re-describing planets ad hoc."
        ),
        primary_citation="BPHS Ch.3, cross-checked against Sarvārtha Cintāmaṇi",
        code_ref="app.knowledge.planets:KARAKATVA",
        quality_label="computed",
        caveats=[],
    ),
    ConceptEntry(
        concept_id="dignity_states",
        category="foundations",
        sanskrit_term="Uccha / Nīcha / Svakṣetra / Mūlatrikoṇa",
        english_gloss="Exaltation, debilitation, own-sign, and moolatrikona dignity",
        classical_definition=(
            "Each planet has one exaltation sign (peak strength), one debilitation sign "
            "(weakest), one or two own signs, and (for most) a moolatrikona sign/degree-range "
            "distinct from its own sign. Dignity feeds almost every downstream calculator: "
            "Shadbala's Sthana Bala, Neechabhanga checks, remedy gemstone gating, yoga detection."
        ),
        primary_citation="BPHS Ch.4",
        code_ref="app.derived.dignities:naisargika_relationship",
        quality_label="computed",
        caveats=[],
    ),
    ConceptEntry(
        concept_id="functional_nature",
        category="foundations",
        sanskrit_term="Kārya-kāraka-tva (functional benefic/malefic)",
        english_gloss="A planet's benefic/malefic role is Lagna-relative, not fixed",
        classical_definition=(
            "AGENTS.md Cardinal Rule 7, the single most important rule in this codebase: a "
            "naturally benefic planet ruling a dusthāna (6/8/12) is FUNCTIONALLY malefic for "
            "that Lagna; a naturally malefic planet ruling a kendra/trikoṇa is FUNCTIONALLY "
            "benefic. Every remedy, every yoga-karaka call, every 'is this placement good' "
            "verdict in this project routes through this classification, never natural nature alone."
        ),
        primary_citation="BPHS Ch.34",
        code_ref="app.derived.functional_nature:functional_nature_report",
        quality_label="computed",
        caveats=[
            "Rahu/Ketu are excluded -- nodes don't own signs in core BPHS doctrine, so "
            "sign-lordship-based functional nature doesn't apply; their functional role via "
            "nakshatra/conjunction lordship is a disclosed data_gap, not guessed.",
        ],
    ),
    ConceptEntry(
        concept_id="graha_drishti",
        category="foundations",
        sanskrit_term="Graha Dṛṣṭi",
        english_gloss="Planetary aspects (special + universal 7th)",
        classical_definition=(
            "Every planet aspects the 7th house from itself; Mars additionally aspects 4th/8th, "
            "Jupiter 5th/9th, Saturn 3rd/10th. This one function is shared by doṣa cancellation "
            "checks, yoga detection, and the full house-network graph -- never re-implemented per caller."
        ),
        primary_citation="BPHS Ch.4",
        code_ref="app.derived.aspects:graha_drishti_houses",
        quality_label="computed",
        caveats=["Rāśi-dṛṣṭi (sign-to-sign, not planet-based) is not implemented -- data_gap."],
    ),
    ConceptEntry(
        concept_id="combustion",
        category="foundations",
        sanskrit_term="Asta / Combustion",
        english_gloss="A planet too close to the Sun loses strength",
        classical_definition=(
            "Planets within a classical orb of the Sun are 'combust' and weakened -- a factor "
            "in Shadbala, remedy gemstone gating (never recommend a gem for a combust planet), "
            "and Ishta/Kashta Phala."
        ),
        primary_citation="BPHS Ch.27 (orb table)",
        code_ref="app.astro.engine:is_combust",
        quality_label="computed",
        caveats=[],
    ),
    # ---------------------------------------------------------------- #
    # Vargas (divisional charts) and pada/arudha family
    # ---------------------------------------------------------------- #
    ConceptEntry(
        concept_id="varga_charts",
        category="vargas",
        sanskrit_term="Varga / Aṁśa",
        english_gloss="Divisional charts D1-D60",
        classical_definition=(
            "Each rāśi is further subdivided (D9 = Navāṁśa for marriage/dharma, D10 for career, "
            "D12 for parents, etc.) -- a planet's varga placement refines the D1 promise. "
            "This project computes the full D1-D60 family."
        ),
        primary_citation="BPHS Ch.6-7",
        code_ref="app.astro.engine:navamsha_d9",
        quality_label="computed",
        caveats=[
            "D10/D7-derived INTERPRETATION layers (career/children synthesis specifically off "
            "those vargas, beyond D1) remain a disclosed data_gap -- the vargas compute fine, "
            "the domain-specific reading of them is what's incomplete.",
        ],
    ),
    ConceptEntry(
        concept_id="vimsopaka_bala",
        category="vargas",
        sanskrit_term="Viṁśopaka Balā",
        english_gloss="20-point varga-quality scoring across 4 classical schemes",
        classical_definition=(
            "Weights a planet's dignity across a fixed set of vargas (Shadvarga/Saptavarga/"
            "Dasavarga/Shodasavarga -- 6/7/10/16 charts respectively) into a single 0-20 score "
            "per scheme, each guaranteed to sum to exactly 20 by construction."
        ),
        primary_citation="BPHS Ch.7",
        code_ref="app.derived.vimsopaka:all_schemes_vimsopaka_bala",
        quality_label="computed",
        caveats=[],
        cross_check_note="Weight tables cross-checked exactly against PyJHora's const.py amsa_vimsopaka tables.",
    ),
    ConceptEntry(
        concept_id="bhavapada_arudha",
        category="vargas",
        sanskrit_term="Bhāva Āruḍha (A1-A12) / Graha Āruḍha",
        english_gloss="Perceptional/manifested image of a house or planet",
        classical_definition=(
            "The Āruḍha Pada is 'how a house appears to the world' -- counted by taking the "
            "distance from a house to its lord's occupied house, then counting the same "
            "distance forward again from the lord (with the 1st/7th exception rule). Extended "
            "here to the full A1-A12 family and to all 7 classical-planet Graha Ārūḍhas."
        ),
        primary_citation="Jaimini Sūtras (Sañjay Rath commentary)",
        code_ref="app.derived.bhavapada:bhavapada_report",
        quality_label="computed",
        caveats=[
            "Upapada (A12) has a KNOWN, DELIBERATELY UNRESOLVED formula conflict -- see the "
            "'upapada_known_conflict' entry in concepts_domains.py. Never silently pick one side.",
        ],
    ),
    # ---------------------------------------------------------------- #
    # Strength engines
    # ---------------------------------------------------------------- #
    ConceptEntry(
        concept_id="shadbala_classical",
        category="strength",
        sanskrit_term="Ṣaḍbalā",
        english_gloss="The 6-fold classical strength system, in Virūpa/Rūpa units",
        classical_definition=(
            "Sthāna Balā (positional) + Dig Balā (directional) + Kāla Balā (temporal, 6 "
            "sub-parts) + Cheṣṭā Balā (motional) + Naisargika Balā (natural) + Dṛik Balā "
            "(aspectual) summed in Virūpas, converted to Rūpas (1 Rūpa = 60 Virūpas)."
        ),
        primary_citation="BPHS Ch.27",
        code_ref="app.derived.shadbala:full_shadbala",
        quality_label="computed_simplified",
        caveats=[
            "Sthāna/Dig/Naisargika/Ayana Balā and 4 of 6 Kāla Balā sub-parts are full classical "
            "precision, built directly from the BPHS PDF text (pdftotext -layout) after "
            "OpenJyotish's own TRIAGE.md flagged real cross-implementation disagreements.",
            "Varsha/Māsa Balā lords (needs a separate Ahargana calendrical derivation), Cheṣṭā "
            "Balā for the 5 non-luminary planets (8-tier motion classification), and Dṛik Balā "
            "are disclosed data_gap -- not fabricated to make the total look complete.",
            "This is a SEPARATE, higher-precision engine from `simplified_shadbala` below -- "
            "not a replacement for it.",
        ],
    ),
    ConceptEntry(
        concept_id="simplified_shadbala",
        category="strength",
        sanskrit_term="Ṣaḍbalā (practical proxy)",
        english_gloss="0-100 practical strength score used by Ishta/Kashta and varga-quality",
        classical_definition=(
            "A pragmatic, non-classical-unit strength proxy (0-100) predating the full "
            "classical engine above -- kept and used deliberately where a bounded, comparable "
            "score is more useful than raw Rupas (e.g. cross-planet comparison at a glance)."
        ),
        primary_citation="Project heuristic, not a direct BPHS formula",
        code_ref="app.derived.strengths:simplified_shadbala",
        quality_label="computed_simplified",
        caveats=["Never conflate with `shadbala_classical` -- different units, different purpose, both kept."],
    ),
    ConceptEntry(
        concept_id="ishta_kashta_phala",
        category="strength",
        sanskrit_term="Iṣṭa / Kaṣṭa Phala",
        english_gloss="Benefic vs malefic potential a planet can deliver, out of 60",
        classical_definition=(
            "Uccha-Raśmi (exaltation-distance strength) and Cheṣṭā-Raśmi (motional strength) "
            "combine so Iṣṭa+Kaṣṭa always sum to exactly 60 -- reconstructed algebraically from "
            "BPHS's own Rāśi-and-doubled-degree wording."
        ),
        primary_citation="BPHS Ch.28",
        code_ref="app.derived.ishta_kashta:classical_ishta_kashta",
        quality_label="computed_simplified",
        caveats=[
            "Sun and Moon get FULL classical precision (BPHS gives their Cheṣṭā Kendra formula "
            "explicitly). Mars/Mercury/Jupiter/Venus/Saturn are honestly `data_gap` for Cheṣṭā "
            "Raśmi specifically -- they need the same 8-tier retrograde-motion data Shadbala "
            "already discloses as incomplete; this reuses that gap rather than inventing a fix.",
        ],
    ),
    ConceptEntry(
        concept_id="ashtakavarga",
        category="strength",
        sanskrit_term="Aṣṭakavarga",
        english_gloss="Bindu (point) system for transit/gochara strength per house",
        classical_definition=(
            "Each of the 7 classical planets contributes bindus to houses from 8 reference "
            "points (7 planets + Lagna); Sarvāṣṭakavarga (SAV) sums all 8 individual charts, "
            "used to grade how favorable a transited house currently is."
        ),
        primary_citation="BPHS Ch.66-71",
        code_ref="app.derived.ashtakavarga:classical_ashtakavarga",
        quality_label="computed",
        caveats=["Rahu/Ketu have no classical Ashtakavarga contribution -- inherited as a disclosed gap by the Gochara engine, not silently zero-filled."],
        cross_check_note="SAV/BAV threshold conventions cross-checked against OpenJyotish's calc/gochara.py.",
    ),
    # ---------------------------------------------------------------- #
    # Timing
    # ---------------------------------------------------------------- #
    ConceptEntry(
        concept_id="vimshottari_dasha",
        category="timing",
        sanskrit_term="Viṁśottarī Daśā",
        english_gloss="The 120-year planetary-period timing system",
        classical_definition=(
            "Moon's nakshatra at birth fixes the starting Mahādaśā lord and how much of its "
            "period is already elapsed; each Mahādaśā (MD) subdivides into Antardaśā (AD), each "
            "AD into Pratyantardaśā (PD), by the same proportional-division rule."
        ),
        primary_citation="BPHS Ch.46",
        code_ref="app.astro.dashas:compute_dashas",
        quality_label="computed",
        caveats=[
            "A real day-truncation bug (stacked int() truncation losing up to ~1 day per "
            "period, compounding across MD->AD->PD) was found and fixed 2026-09-16 -- see "
            "docs/dasha-precision-fix.md. If a reading predates that fix, its exact "
            "day-level PD boundaries may be off by a few days; sign/house-level conclusions are unaffected.",
        ],
    ),
    ConceptEntry(
        concept_id="gochara_transits",
        category="timing",
        sanskrit_term="Gochara",
        english_gloss="Transit assessment -- current planetary positions vs. natal",
        classical_definition=(
            "Combines the simple 'good house counted from Moon' heuristic with the Aṣṭakavarga "
            "bindu verdict for the same house, surfacing agreement/disagreement between the two "
            "classical methods explicitly rather than picking one silently."
        ),
        primary_citation="BPHS Ch.41-42, Sarvārtha Cintāmaṇi (primary transit-methodology authority)",
        code_ref="app.derived.gochara:gochara_report",
        quality_label="computed_simplified",
        caveats=["Vedha (obstruction) between transiting planets is not yet implemented -- data_gap (v1's TR-003 stub)."],
    ),
    ConceptEntry(
        concept_id="sade_sati",
        category="timing",
        sanskrit_term="Sāḍe Sātī",
        english_gloss="Saturn's 7.5-year transit window around natal Moon",
        classical_definition="Saturn transiting the 12th, 1st, and 2nd houses counted from natal Moon sign.",
        primary_citation="Classical transit doctrine, cross-checked against multiple sources per docs/dosha-registry.md",
        code_ref="app.astro.transits:transit_assessment",
        quality_label="computed",
        caveats=[],
    ),
]
