"""Concept registry, part 2 of 2: Doshas, Yogas, Nakshatras, Interventions,
Domain syntheses, and Meta entries. See
app/engine/cheatsheet/concepts.py (the thin aggregator module) for the
full editorial-rule docstring shared by both halves of this registry.
"""
from __future__ import annotations

from app.engine.cheatsheet.models import ConceptEntry

CONCEPTS_DOMAINS: list[ConceptEntry] = [
    # ---------------------------------------------------------------- #
    # Doshas (afflictions) -- every one of the 8 this codebase checks
    # ---------------------------------------------------------------- #
    ConceptEntry(
        concept_id="mangal_dosha",
        category="dosha",
        sanskrit_term="Maṅgala / Kuja Doṣa",
        english_gloss="Mars afflicting marriage houses from Lagna, Moon, or Venus",
        classical_definition=(
            "Mars in specific houses (1/2/4/7/8/12, varying by reference point) from Lagna, "
            "Moon, and Venus independently signals marital friction -- but is heavily "
            "cancellation-gated: Mars in own sign/exaltation in the doṣa house, Jupiter/Venus "
            "aspect or conjunction, and per-Lagna dignity exceptions can all cancel or reduce it."
        ),
        primary_citation="BPHS Ch.77",
        code_ref="app.derived.doshas:check_mangal_dosha",
        quality_label="computed",
        caveats=[
            "A real bug (missing the 'Mars own-sign/exalted in the dosha house' cancellation "
            "condition) was found via the Phase 3 composer-vs-LLM diff and fixed -- see "
            "docs/phase3-composer-vs-llm-diff.md. Mutual cancellation via a PARTNER's chart "
            "cannot be checked from a single chart -- explicit data_gap on that specific condition.",
        ],
        cross_check_note="Present/absent AND the specific cancellation reasons matched exactly against PyJHora's independent manglik() implementation (docs/public-repo-review/03-validation-cross-checks.md Check 2).",
    ),
    ConceptEntry(
        concept_id="kala_sarpa_dosha",
        category="dosha",
        sanskrit_term="Kāla Sarpa Doṣa",
        english_gloss="All 7 classical planets hemmed between Rahu and Ketu",
        classical_definition="All 7 classical grahas fall on one side of the Rahu-Ketu axis, with no planet crossing to the other side.",
        primary_citation="Widely-cited Parāśarī-tradition convention",
        code_ref="app.derived.doshas:check_kala_sarpa",
        quality_label="computed",
        caveats=["citation_status: pending_audit -- not yet chapter/verse-confirmed against a primary BPHS passage."],
    ),
    ConceptEntry(
        concept_id="pitru_dosha",
        category="dosha",
        sanskrit_term="Pitṛ Doṣa",
        english_gloss="Ancestral-karma affliction, typically Sun-Rahu/Saturn combinations",
        classical_definition="Sun afflicted by Rahu or Saturn (conjunction/close aspect), especially in 9th house or from 9th lord.",
        primary_citation="docs/dosha-registry.md",
        code_ref="app.derived.doshas:check_pitru_dosha",
        quality_label="computed",
        caveats=[],
    ),
    ConceptEntry(
        concept_id="guru_chandala_yoga",
        category="dosha",
        sanskrit_term="Guru Cāṇḍāla Yoga",
        english_gloss="Jupiter afflicted by Rahu conjunction",
        classical_definition="Jupiter and Rahu conjunct within orb -- clouds Jupiter's wisdom/dharma significations.",
        primary_citation="docs/dosha-registry.md",
        code_ref="app.derived.doshas:check_guru_chandala",
        quality_label="computed_with_conflict",
        caveats=["The exact orb threshold for this conjunction is a deliberately unresolved methodology question (flagged during Phase 3, Cardinal Rule 3) -- not silently picked."],
    ),
    ConceptEntry(
        concept_id="kemadruma_dosha",
        category="dosha",
        sanskrit_term="Kemadruma Doṣa",
        english_gloss="Moon isolated -- no planets in houses 2/12 from Moon, nor conjunct",
        classical_definition="Moon with no planets (other than Sun) in the 2nd or 12th from it, and none conjunct -- signals emotional isolation, mitigated by several classical exceptions.",
        primary_citation="BPHS (lunar yoga chapter)",
        code_ref="app.derived.doshas:check_kemadruma",
        quality_label="computed",
        caveats=[],
    ),
    ConceptEntry(
        concept_id="papakartari_yoga",
        category="dosha",
        sanskrit_term="Pāpakartarī Yoga",
        english_gloss="A house hemmed between two malefics on either side",
        classical_definition="A house flanked (2nd-from and 12th-from) by natural or functional malefics with no benefic relief -- a 'scissor' affliction.",
        primary_citation="General Parashari principle",
        code_ref="app.derived.doshas:check_papakartari",
        quality_label="computed",
        caveats=["The Phase 3 composer-vs-LLM diff caught a genuine H12 Papakartari affliction the original LLM narrative's narrower manual check had missed -- documented in docs/phase3-composer-vs-llm-diff.md as a real positive finding for the rule-engine approach."],
    ),
    ConceptEntry(
        concept_id="ghata_dosha",
        category="dosha",
        sanskrit_term="Ghāta Doṣa",
        english_gloss="Mars-Saturn conjunction affliction",
        classical_definition="Mars and Saturn conjunct within orb -- a widely-cited but not chapter/verse-pinned combination.",
        primary_citation="Widely-cited Parāśarī-tradition convention",
        code_ref="app.derived.doshas:check_ghata_dosha",
        quality_label="computed",
        caveats=["citation_status: pending_audit -- shape-only cross-check against PyJHora's dosha.py::ghata(), no code copied per AD-4."],
    ),
    ConceptEntry(
        concept_id="shrapit_dosha",
        category="dosha",
        sanskrit_term="Śrāpit Doṣa",
        english_gloss="Rahu-Saturn conjunction affliction",
        classical_definition="Rahu and Saturn conjunct within orb -- the 'cursed' combination convention.",
        primary_citation="Widely-cited Parāśarī-tradition convention",
        code_ref="app.derived.doshas:check_shrapit_dosha",
        quality_label="computed",
        caveats=["citation_status: pending_audit -- same disclosed treatment as Ghata/Kala Sarpa."],
    ),
    # ---------------------------------------------------------------- #
    # Yogas -- the compiled ~20-yoga tranche (of 269 named yogas total)
    # ---------------------------------------------------------------- #
    ConceptEntry(
        concept_id="pancha_mahapurusha_yogas",
        category="yoga",
        sanskrit_term="Pañca Mahāpuruṣa Yoga",
        english_gloss="Ruchaka/Bhadra/Hansa/Malavya/Sasa -- 5 'great person' yogas",
        classical_definition="Mars/Mercury/Jupiter/Venus/Saturn respectively, in own sign or exaltation, AND occupying a kendra (1/4/7/10) from Lagna.",
        primary_citation="BPHS Ch.75",
        code_ref="app.derived.yogas:check_pancha_mahapurusha_yogas",
        quality_label="computed",
        caveats=[],
    ),
    ConceptEntry(
        concept_id="raja_yoga_family",
        category="yoga",
        sanskrit_term="Rāja Yoga / Nīcabhaṅga Rāja Yoga",
        english_gloss="Kendra-trikona lord combinations, and cancelled-debility elevation",
        classical_definition=(
            "A kendra lord (1/4/7/10) combining with a trikoṇa lord (1/5/9) classically produces "
            "Rāja Yoga. Nīcabhaṅga specifically cancels a planet's debility when the sign lord "
            "of its debilitation sign occupies a kendra from Lagna, often elevating rather than "
            "merely neutralizing the placement."
        ),
        primary_citation="BPHS Ch.34, Ch.75-76",
        code_ref="app.derived.yogas:check_neechabhanga_raja_yoga",
        quality_label="computed",
        caveats=["Full generic Raja Yoga detection (RC-018 in the v1 corpus) remains genuinely unimplemented in both v1 and v2 -- honestly `data_gap`, not silently assumed covered by Neechabhanga alone."],
    ),
    ConceptEntry(
        concept_id="yoga_karaka_doctrine",
        category="yoga",
        sanskrit_term="Yoga-Kāraka",
        english_gloss="A planet owning BOTH a kendra and a trikona (excluding H1's trivial overlap)",
        classical_definition=(
            "For 6 Lagnas (Taurus/Libra->Saturn, Cancer/Leo->Mars, Capricorn/Aquarius->Venus) one "
            "planet owns both a kendra and a trikoṇa via two DIFFERENT signs, making it "
            "exceptionally auspicious. H1 is excluded from both sides of the test by design -- "
            "otherwise every dual-owning lagna lord would be mis-flagged."
        ),
        primary_citation="BPHS Ch.34",
        code_ref="app.derived.factors:is_yoga_karaka",
        quality_label="computed",
        caveats=["This exact H1-exclusion bug was independently found in two separate narrative readings (Pisces/Jupiter, Gemini/Mercury lagna) before being fixed at the source -- see the function's own docstring."],
    ),
    ConceptEntry(
        concept_id="lunar_and_wealth_yogas",
        category="yoga",
        sanskrit_term="Sunapha / Anapha / Durudhāra / Gajakesarī / Kahala / Śaṅkha / Lakṣmī / Vāsumatī / Amala / Budha-Āditya / Cāndra-Māṅgala",
        english_gloss="Moon-relative and named wealth/intelligence yogas",
        classical_definition="A family of yogas defined by planets in specific houses relative to the Moon or Lagna (2nd/12th from Moon, Jupiter-Moon kendra relationships, Mercury-Sun conjunction, etc.).",
        primary_citation="BPHS + Saravali (multiple chapters, per-yoga)",
        code_ref="app.derived.yogas:compute_all_yogas",
        quality_label="computed_simplified",
        caveats=[
            "This project compiles ~20 classically central yogas out of 269 distinct named "
            "yogas identified in PyJHora's yoga.py -- the remaining ~249 (mostly niche, e.g. "
            "specific-affliction yogas) are an explicitly tracked backlog, not silently dropped. "
            "See docs/yoga-compilation-backlog.md.",
        ],
    ),
    ConceptEntry(
        concept_id="viparita_raja_yoga",
        category="yoga",
        sanskrit_term="Viparīta Rāja Yoga",
        english_gloss="Dusthana lords in mutual exchange/combination reverse into a positive",
        classical_definition="Lords of the 6th/8th/12th houses combining with each other (rather than with kendra/trikona lords) paradoxically produce a favorable result.",
        primary_citation="BPHS Ch.76",
        code_ref="app.derived.yogas:check_viparita_raja_yoga",
        quality_label="computed",
        caveats=[],
    ),
    # ---------------------------------------------------------------- #
    # Nakshatras
    # ---------------------------------------------------------------- #
    ConceptEntry(
        concept_id="nakshatra_profiles",
        category="nakshatra",
        sanskrit_term="Nakṣatra",
        english_gloss="The 27 lunar mansions -- id, lord, deity, gaṇa, tattva, yoni, motivation, pada",
        classical_definition="Each planet's sidereal longitude falls in one of 27 nakshatras (13°20' each), each with its own ruling planet, deity, temperament (gaṇa), and pada (quarter) that bridges to the D9 chart.",
        primary_citation="BPHS + Nakṣatra Cintāmaṇi",
        code_ref="app.derived.nakshatra_analysis:nakshatra_analysis_report",
        quality_label="computed",
        caveats=[],
    ),
    ConceptEntry(
        concept_id="gandanta_abhukta_mula",
        category="nakshatra",
        sanskrit_term="Gaṇḍānta / Abhukta Mūla",
        english_gloss="Sensitive water-fire sign junctions, and the tighter Jyeshtha-Mula sub-case",
        classical_definition=(
            "The three junctions between a water sign's last nakshatra and the next fire sign's "
            "first (Cancer-Leo, Scorpio-Sagittarius, Pisces-Aries) carry a 3°20' orb of "
            "heightened sensitivity. The Jyeshtha-Mula junction additionally has a much tighter "
            "48-arcminute 'Abhukta Mula' sub-zone considered especially inauspicious classically."
        ),
        primary_citation="docs/nakshatra-framework.md §5",
        code_ref="app.derived.nakshatra_analysis:check_gandanta",
        quality_label="computed",
        caveats=[],
    ),
    # ---------------------------------------------------------------- #
    # Interventions
    # ---------------------------------------------------------------- #
    ConceptEntry(
        concept_id="argala",
        category="intervention",
        sanskrit_term="Argala / Vipārīta Argala",
        english_gloss="Support/obstruction channels acting on a house from 2nd/4th/11th/5th (and their opposites)",
        classical_definition=(
            "Planets in the 2nd, 4th, 11th, and 5th houses from a reference point create Argala "
            "(intervention/support); planets in the 12th, 10th, 3rd, and 9th (the counter-houses) "
            "create obstruction (Virodhargala). 3+ malefics in the 3rd-from counter-house reverses "
            "obstruction into a favorable Vipārīta Argala signal."
        ),
        primary_citation="BPHS Ch.31",
        code_ref="app.derived.interventions:practical_argala",
        quality_label="computed_simplified",
        caveats=[
            "Built directly from BPHS Ch.31 text via pdftotext -layout -- NO reference repo "
            "(PyJHora, OpenJyotish, or the earlier VedAstro) has ANY Argala implementation to "
            "cross-check against (confirmed by grep across all three, docs/public-repo-review/"
            "02-feature-comparison.md). A real gap was found and fixed while building this: the "
            "pre-existing engine only checked 3 of the 4 named support/obstruction channels "
            "(missing 5th/9th) -- same category of fix as the Mangal Dosha cancellation bug.",
            "Quarter-based (7°30') fine-grained nullification (also named in BPHS v.4-5) is "
            "disclosed as not attempted -- a further-precision candidate, not silently covered.",
        ],
        cross_check_note="No reference repo has this feature at all -- text-only build, extra review pass per build_plan.md Phase 6's own instruction.",
    ),
    # ---------------------------------------------------------------- #
    # Domain syntheses (marriage / career / remedies)
    # ---------------------------------------------------------------- #
    ConceptEntry(
        concept_id="marriage_five_pillar",
        category="domain",
        sanskrit_term="Pañca-Stambha (Five-Pillar synthesis, project term)",
        english_gloss="7th House + 7th Lord + Venus/Jupiter Karaka + Darakaraka + Upapada, read together",
        classical_definition=(
            "No single classical factor decides marriage outcomes -- this project's synthesis "
            "composes the 7th house/lord placement, the natural marriage karaka (Venus for a "
            "male chart, Jupiter for a female -- both ALWAYS computed, gender-agnostic at "
            "context-build time), the Jaimini Darakaraka (D1+D9), and the Upapada, into one report."
        ),
        primary_citation="docs/domain-playbooks.md, Marriage_Guide_Part1-4.md",
        code_ref="app.derived.marriage_analysis:five_pillar_marriage_report",
        quality_label="computed_simplified",
        caveats=["Zero new astrology math -- composed entirely from already-verified primitives (lord_placements, functional_nature, D9, bhavapada)."],
    ),
    ConceptEntry(
        concept_id="marriage_compatibility",
        category="domain",
        sanskrit_term="Aṣṭakūṭa Milāpa + Synastry + D9 Triple Agreement",
        english_gloss="36-point guna matching, inter-chart aspects, and D9 cross-checks for two charts",
        classical_definition=(
            "Aṣṭakūṭa scores 8 kūtas (Varna/Vasya/Tara/Yoni/Graha-Maitri/Gana/Bhakut/Nadi) out of "
            "36; synastry checks 7 inter-chart Venus/Jupiter/7th-lord indicators; D9 "
            "cross-compatibility applies 5 rules across both charts' Navamsha."
        ),
        primary_citation="Marriage_Guide_Part2-4.md",
        code_ref="app.derived.compatibility:ashtakuta_report",
        quality_label="computed",
        caveats=[
            "Found and fixed a real, repeated D9-computation bug in 3 existing corpus documents "
            "for Ajay Kumar during this build (guide claimed D9 Lagna=Pisces; independently "
            "re-derived twice, engine computes Virgo -- corpus was wrong, engine is trusted). "
            "See docs/marriage-compatibility-notes.md.",
        ],
    ),
    ConceptEntry(
        concept_id="marriage_timing_triple_agreement",
        category="domain",
        sanskrit_term="Daśā / Gochara / D9 Triple Agreement",
        english_gloss="Ranked significators scanned across dasha windows, transit windows, and D9 confirmation",
        classical_definition="Marriage timing is judged 'possible/confirmed/certain' by how many of the three independent methods agree on the same window, never by any single method alone.",
        primary_citation="Marriage_Guide_Part3.md §9.1",
        code_ref="app.derived.marriage_timing:marriage_timing_report",
        quality_label="computed_simplified",
        caveats=[],
    ),
    ConceptEntry(
        concept_id="career_synthesis",
        category="domain",
        english_gloss="10th House / 10th Lord synthesis reusing Karakatva's professions list",
        classical_definition="10th house occupants classify into profession-types by classical convention; the 10th lord's placement and identity (via its own Karakatva professions) both contribute; Yoga-Karaka and Kendradhipati-Dosha flags wrap the existing functional-nature engine verbatim.",
        primary_citation="docs/domain-playbooks.md",
        code_ref="app.derived.career_analysis:career_analysis_report",
        quality_label="computed_simplified",
        caveats=["A10 (Arudha of the 10th) and D10-derived interpretation layers remain the pre-existing disclosed data_gap -- not claimed closed by this synthesis."],
    ),
    ConceptEntry(
        concept_id="remedy_safety_rules",
        category="domain",
        sanskrit_term="Upāya (remedy) Safety Rules",
        english_gloss="Every gemstone recommendation is gated through functional nature, never natural nature alone",
        classical_definition=(
            "A gemstone is only appropriate for a genuinely functional-benefic, weak/afflicted, "
            "non-combust planet. Saturn additionally needs to be a genuine yoga-karaka (not "
            "merely functional-benefic) before a blue sapphire is ever indicated; Rahu needs to "
            "be well-placed with a strong dispositor. A functional malefic NEVER gets a gemstone "
            "-- dāna (charity) of that planet's significations is prescribed instead."
        ),
        primary_citation="docs/domain-playbooks.md Remedy Safety Rules",
        code_ref="app.derived.remedies:remedy_report",
        quality_label="computed",
        caveats=[
            "Safety-critical: a dedicated cross-check test guards 'never gemstone a functional "
            "malefic' across every fixture -- this is the one place in the codebase where a bug "
            "would translate into genuinely harmful advice, treated with matching rigor.",
        ],
    ),
    # ---------------------------------------------------------------- #
    # Meta -- how to read this project's own honesty machinery
    # ---------------------------------------------------------------- #
    ConceptEntry(
        concept_id="upapada_known_conflict",
        category="meta",
        sanskrit_term="Upapada Lagna (UL)",
        english_gloss="Two different, both-preserved formulas for the same classical concept",
        classical_definition=(
            "The canonical Āruḍha-distance formula (12th-house Āruḍha, standard exception rule) "
            "and this project's corpus guides' own inclusive-count formula disagree on Upapada "
            "for at least two people (Ajay: Aries vs Sagittarius; Sandeep: same class of "
            "disagreement). AGENTS.md Cardinal Rule 3 forbids silently resolving this."
        ),
        primary_citation="AGENTS.md §6 Known Conflicts",
        code_ref="app.derived.factors:upapada_lagna_project_legacy",
        quality_label="computed_with_conflict",
        caveats=["The canonical formula is the recommended default, but BOTH values are always computed and surfaced side by side -- never pick one and discard the other."],
    ),
    ConceptEntry(
        concept_id="quality_label_vocabulary",
        category="meta",
        english_gloss="The 4 permitted honesty labels every rule/calculator output carries",
        classical_definition=(
            "`computed` = full classical-precision derivation. `computed_simplified` = a "
            "practical proxy or compositional synthesis, honestly downgraded even when every "
            "input resolves cleanly. `computed_with_conflict` = two source formulas disagree and "
            "both are preserved. `data_gap` = genuinely not implemented -- never guessed. No "
            "other label is permitted anywhere in this codebase's rule engine."
        ),
        primary_citation="docs/validation-document-spec.md §8-9",
        code_ref="app.rules.schema:RuleEvaluation",
        quality_label="computed",
        caveats=[],
    ),
    ConceptEntry(
        concept_id="classical_text_hierarchy",
        category="meta",
        english_gloss="The order used to resolve disagreements between classical texts",
        classical_definition=(
            "BPHS (primary Parasari authority) > Brihat Jataka > Phaladipika > Saravali > "
            "Sarvartha Cintamani (primary transit-methodology authority) > Jataka Parijata > "
            "Uttara Kalamrita > Nakshatra Cintamani. Jaimini-specific topics (karakas, chara "
            "dasha, karakamsha) instead defer to the Jaimini Sutras (Sanjay Rath commentary)."
        ),
        primary_citation="AGENTS.md §7",
        code_ref=None,
        quality_label="data_gap",
        caveats=["Not itself a calculator -- a documentation/process rule; code_ref is intentionally None, not a mismatch."],
    ),
]
