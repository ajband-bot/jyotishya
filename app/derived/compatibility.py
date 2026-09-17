"""Ashtakuta (eight-fold Guna Milan) marriage compatibility engine + Mangal
Dosha matching -- build_plan.md Phase 4a items 1-2.

Primary source: Marriage_Guide_Part2.md (itself citing Muhurta Chintamani
Vivaha Prakarana, BPHS Ch.78, Jyotish Ratnakar, Vivaha Vrindavana,
Daivagna Vallabha). Every table below was cross-checked (AD-4, data/formula
comparison only -- no code imported) against PyJHora's independent
`horoscope/match/compatibility.py`. Where the two sources agreed, the
richer/more-precise one was kept; where they genuinely disagreed, the
disagreement is disclosed in the docstring of the relevant function rather
than silently resolved (Cardinal Rule 3). Full writeup:
docs/marriage-compatibility-notes.md.

Kuta functions take plain primitives (sign numbers, nakshatra ids, chart
dicts) rather than full ctx objects, so each is independently unit
testable; `ashtakuta_report()` is the orchestrator that pulls those
primitives from two `build_chart_context()` outputs.
"""
from __future__ import annotations

from typing import Any

from app.astro.constants import NAKSHATRAS, PLANET_STATES, SIGNS
from app.derived.dignities import naisargika_relationship
from app.knowledge.nakshatras import NAKSHATRA_PROFILES

MAX_SCORES = {
    "varna": 1, "vasya": 2, "tara": 3, "yoni": 4,
    "graha_maitri": 5, "gana": 6, "bhakut": 7, "nadi": 8,
}

# ── Kuta 1: Varna ────────────────────────────────────────────────────────
# Varna is classically derived from the Moon's RASHI ELEMENT (not a
# per-nakshatra lookup) -- cross-checked exactly against PyJHora's
# `vasiya_raasi_list`/`VarnaArray` (their comment: "0=>Brahmin 1=>Kshatriya
# 2=>Vaishya 3=>Sudra", water signs=0, fire=1, air=2, earth=3). This
# resolves an ambiguity in Marriage_Guide_Part2.md's own quick-reference
# table, which lists Varna per-nakshatra and breaks for junction nakshatras
# that straddle two rashis with different elements (e.g. Krittika spans
# Aries/Taurus). Deriving from the native's actual Moon rashi sidesteps
# that ambiguity entirely and is the textually cleaner method.
ELEMENT_TO_VARNA = {"Water": "Brahmin", "Fire": "Kshatriya", "Air": "Vaishya", "Earth": "Shudra"}
VARNA_RANK = {"Brahmin": 0, "Kshatriya": 1, "Vaishya": 2, "Shudra": 3}


def varna_of_sign(sign: int) -> str:
    return ELEMENT_TO_VARNA[SIGNS[sign - 1]["element"]]


def varna_kuta(groom_moon_sign: int, bride_moon_sign: int) -> dict[str, Any]:
    groom_varna = varna_of_sign(groom_moon_sign)
    bride_varna = varna_of_sign(bride_moon_sign)
    score = 1.0 if VARNA_RANK[groom_varna] <= VARNA_RANK[bride_varna] else 0.0
    return {
        "groom_varna": groom_varna, "bride_varna": bride_varna,
        "raw_score": score, "effective_score": score, "max_score": MAX_SCORES["varna"],
        "citation": "Muhurta Chintamani Varna Kuta; rashi-element method cross-checked against PyJHora vasiya_raasi_list",
    }


# ── Kuta 2: Vasya ────────────────────────────────────────────────────────
# 5-group Vasya scheme + scoring matrix cross-checked (AD-4) against
# PyJHora's `VasiyaArray` (their own comment: "From Saravali.de"). This
# resolves TWO self-contradictions in Marriage_Guide_Part2.md's own prose:
# (a) it lists Leo under "Chatushpada" in one bullet but then separately
# flags "Vanachara (Forest): Leo (some schools)" -- PyJHora's independent
# table puts Leo in its own Vanachara group exclusively, which is the
# convention adopted here; (b) it lists all of Capricorn under Chatushpada
# AND "1st half of Capricorn" under Jalachara in the same list --
# PyJHora resolves this cleanly via a degree-based split (<15 deg /
# >=15 deg within the sign), also adopted here, matching PyJHora's own
# docstring admission that the pada-based approximation is secondary to
# the degree-based method.
VASYA_GROUPS = ["Chatushpada", "Manava", "Jalachara", "Vanachara", "Keeta"]
VASYA_MATRIX = [
    [2.0, 0.5, 1.0, 0.0, 2.0],
    [0.5, 2.0, 0.0, 0.0, 0.0],
    [1.0, 0.0, 2.0, 2.0, 2.0],
    [0.0, 0.0, 2.0, 2.0, 0.0],
    [1.0, 0.0, 1.0, 0.0, 2.0],
]


def vasya_group(sign: int, deg_in_sign: float) -> str:
    if sign in (1, 2):
        return "Chatushpada"
    if sign in (3, 6, 7, 11):
        return "Manava"
    if sign in (4, 12):
        return "Jalachara"
    if sign == 5:
        return "Vanachara"
    if sign == 8:
        return "Keeta"
    if sign == 9:
        return "Manava" if deg_in_sign < 15.0 else "Chatushpada"
    if sign == 10:
        return "Chatushpada" if deg_in_sign < 15.0 else "Jalachara"
    raise ValueError(f"invalid sign number {sign}")


def vasya_kuta(groom_sign: int, groom_deg: float, bride_sign: int, bride_deg: float) -> dict[str, Any]:
    groom_group = vasya_group(groom_sign, groom_deg)
    bride_group = vasya_group(bride_sign, bride_deg)
    score = VASYA_MATRIX[VASYA_GROUPS.index(bride_group)][VASYA_GROUPS.index(groom_group)]
    return {
        "groom_group": groom_group, "bride_group": bride_group,
        "raw_score": score, "effective_score": score, "max_score": MAX_SCORES["vasya"],
        "citation": "Muhurta Chintamani Vasya Kuta; matrix cross-checked against PyJHora VasiyaArray (source: Saravali)",
    }


# ── Kuta 3: Tara ─────────────────────────────────────────────────────────
# Well-established universal convention (Marriage_Guide_Part2.md's worked
# example is internally consistent and self-verifying: Krittika(3) to
# Uttara Ashadha(21), count=19, 19 mod 9 = 1 = Janma = auspicious). PyJHora
# implements the same 3.0-max / 1.5-per-direction structure but its
# specific auspicious/inauspicious index mapping could not be confidently
# reverse-engineered from ambiguous variable naming without risking a
# misreading of someone else's code (AD-4 forbids importing code, so this
# was deliberately NOT force-fit) -- implemented independently here from
# the textually explicit, self-consistent classical formula instead.
TARA_AUSPICIOUS_REMAINDERS = {0, 1, 2, 4, 6, 8}  # Janma/Sampat/Kshema/Sadhana/Mitra/Parama-Mitra


def _tara_remainder(from_nak: int, to_nak: int) -> int:
    count = ((to_nak - from_nak) % 27) + 1
    return count % 9


def tara_kuta(groom_nak_id: int, bride_nak_id: int) -> dict[str, Any]:
    groom_to_bride = _tara_remainder(groom_nak_id, bride_nak_id)
    bride_to_groom = _tara_remainder(bride_nak_id, groom_nak_id)
    aus_gb = groom_to_bride in TARA_AUSPICIOUS_REMAINDERS
    aus_bg = bride_to_groom in TARA_AUSPICIOUS_REMAINDERS
    score = 3.0 if (aus_gb and aus_bg) else (1.5 if (aus_gb or aus_bg) else 0.0)
    return {
        "groom_to_bride_remainder": groom_to_bride, "bride_to_groom_remainder": bride_to_groom,
        "groom_to_bride_auspicious": aus_gb, "bride_to_groom_auspicious": aus_bg,
        "raw_score": score, "effective_score": score, "max_score": MAX_SCORES["tara"],
        "citation": "Muhurta Chintamani Tara Kuta (Marriage_Guide_Part2.md worked formula)",
    }


# ── Kuta 4: Yoni ─────────────────────────────────────────────────────────
# Reuses app.knowledge.nakshatras.NAKSHATRA_PROFILES's own "yoni" field
# (already cited to BPHS Ch.86 / Nakshatra Cintamani, already unit-tested)
# rather than importing a second, independently-sourced yoni table --
# avoids the two tables silently disagreeing. Cross-checked (AD-4):
# NAKSHATRA_PROFILES's animal-per-nakshatra assignment matches PyJHora's
# `yoni_mappings` exactly for all 27 nakshatras; Marriage_Guide_Part2.md's
# OWN yoni table drifts from both starting around Mrigashira (it lists
# "Female Deer" where both NAKSHATRA_PROFILES and PyJHora agree on
# "Serpent") -- treated as a transcription error in that document, not
# adopted. The 14x14 compatibility matrix itself is the classical
# yoni-pair scoring table (same structure independently implemented by
# PyJHora as `YoniArray`); values cross-checked to match.
YONI_CATEGORIES = ["Horse", "Elephant", "Goat", "Serpent", "Dog", "Cat", "Rat",
                    "Cow", "Buffalo", "Tiger", "Deer", "Monkey", "Mongoose", "Lion"]
YONI_MATRIX = [
    [4, 2, 2, 3, 2, 2, 2, 1, 0, 1, 1, 3, 2, 1],
    [2, 4, 3, 3, 2, 2, 2, 2, 3, 1, 2, 3, 2, 0],
    [2, 3, 4, 2, 1, 2, 1, 3, 3, 1, 2, 0, 3, 1],
    [3, 3, 2, 4, 2, 1, 1, 1, 1, 2, 2, 2, 0, 2],
    [2, 2, 1, 2, 4, 2, 1, 2, 2, 1, 0, 2, 1, 1],
    [2, 2, 2, 1, 2, 4, 0, 2, 2, 1, 3, 3, 2, 1],
    [2, 2, 1, 1, 1, 0, 4, 2, 2, 2, 2, 2, 1, 2],
    [1, 2, 3, 1, 2, 2, 2, 4, 3, 0, 3, 2, 2, 1],
    [0, 3, 3, 1, 2, 2, 2, 3, 4, 1, 2, 2, 2, 1],
    [1, 1, 1, 2, 1, 1, 2, 0, 1, 4, 1, 1, 2, 1],
    [1, 2, 2, 2, 0, 3, 2, 3, 2, 1, 4, 2, 2, 1],
    [3, 3, 0, 2, 2, 3, 2, 2, 2, 1, 2, 4, 3, 2],
    [2, 2, 3, 0, 1, 2, 1, 2, 2, 2, 2, 3, 4, 2],
    [1, 0, 1, 2, 1, 1, 2, 1, 1, 1, 1, 2, 2, 4],
]


def _yoni_animal(nak_id: int) -> str:
    return NAKSHATRA_PROFILES[nak_id]["yoni"].split(" ")[0]


def yoni_kuta(groom_nak_id: int, bride_nak_id: int) -> dict[str, Any]:
    groom_animal = _yoni_animal(groom_nak_id)
    bride_animal = _yoni_animal(bride_nak_id)
    score = float(YONI_MATRIX[YONI_CATEGORIES.index(groom_animal)][YONI_CATEGORIES.index(bride_animal)])
    return {
        "groom_animal": groom_animal, "bride_animal": bride_animal,
        "raw_score": score, "effective_score": score, "max_score": MAX_SCORES["yoni"],
        "citation": "Daivagna Vallabha Yoni Kuta; animal-per-nakshatra reused from app.knowledge.nakshatras (BPHS Ch.86), matrix cross-checked against PyJHora YoniArray",
    }


# ── Kuta 5: Graha Maitri ─────────────────────────────────────────────────
# Reuses app.derived.dignities.naisargika_relationship() -- already
# verified against PyJHora's planet_relations matrix during Phase 1
# (dignities.py's own docstring). Zero new relationship data introduced.
GRAHA_MAITRI_SCORE = {
    ("friend", "friend"): 5.0,
    ("friend", "neutral"): 4.0, ("neutral", "friend"): 4.0,
    ("neutral", "neutral"): 3.0,
    ("friend", "enemy"): 1.0, ("enemy", "friend"): 1.0,
    ("neutral", "enemy"): 0.5, ("enemy", "neutral"): 0.5,
    ("enemy", "enemy"): 0.0,
}


def graha_maitri_kuta(groom_moon_sign: int, bride_moon_sign: int) -> dict[str, Any]:
    groom_lord = SIGNS[groom_moon_sign - 1]["lord"]
    bride_lord = SIGNS[bride_moon_sign - 1]["lord"]
    if groom_lord == bride_lord:
        score = 5.0
        rel_gb = rel_bg = "same_planet"
    else:
        rel_gb = naisargika_relationship(groom_lord, bride_lord)
        rel_bg = naisargika_relationship(bride_lord, groom_lord)
        score = GRAHA_MAITRI_SCORE[(rel_gb, rel_bg)]
    return {
        "groom_moon_lord": groom_lord, "bride_moon_lord": bride_lord,
        "groom_to_bride_relationship": rel_gb, "bride_to_groom_relationship": rel_bg,
        "raw_score": score, "effective_score": score, "max_score": MAX_SCORES["graha_maitri"],
        "citation": "BPHS Ch.3/4 Naisargika Maitri via Muhurta Chintamani Graha Maitri Kuta -- single most important kuta per source",
    }


# ── Kuta 6: Gana ─────────────────────────────────────────────────────────
# Reuses NAKSHATRA_PROFILES's "gana" field (DRY, already cited/tested).
# The scoring MATRIX below is the asymmetric Saravali-sourced table
# cross-checked against PyJHora's `gana_array` (their comment: "Based on
# saravali.de (Maitri)") -- richer than Marriage_Guide_Part2.md's own
# symmetric summary table, which collapses Deva+Manushya and Manushya+Deva
# to the same score (5) when the two independently-implemented sources
# (PyJHora + the classical Saravali table it cites) actually give 6 vs 5
# depending on which partner holds which gana. The richer, cross-checked
# table is adopted; the guide's simplification is disclosed as such.
GANA_ORDER = ["Deva", "Manusya", "Rakshasa"]
GANA_MATRIX = [
    [6, 6, 0],
    [5, 6, 0],
    [1, 0, 6],
]  # row = bride gana, col = groom gana


def gana_kuta(groom_nak_id: int, bride_nak_id: int) -> dict[str, Any]:
    groom_gana = NAKSHATRA_PROFILES[groom_nak_id]["gana"]
    bride_gana = NAKSHATRA_PROFILES[bride_nak_id]["gana"]
    score = float(GANA_MATRIX[GANA_ORDER.index(bride_gana)][GANA_ORDER.index(groom_gana)])
    return {
        "groom_gana": groom_gana, "bride_gana": bride_gana,
        "raw_score": score, "effective_score": score, "max_score": MAX_SCORES["gana"],
        "citation": "Muhurta Chintamani Gana Kuta; asymmetric matrix cross-checked against PyJHora gana_array (source: Saravali)",
        "mitigation_note": "Per Jyotish Ratnakar: full Graha Maitri (5/5) substantially compensates a low Gana score -- check jointly with graha_maitri_kuta, never in isolation (Cardinal Rule 8).",
    }


# ── Kuta 7: Bhakut ───────────────────────────────────────────────────────
# Marriage_Guide_Part2.md's 7/5/0 point scale is kept (richer than
# PyJHora's simpler pass/fail raasi_array), but the set of DOSHA axes
# ({2/12, 5/9, 6/8}) was cross-checked (AD-4) against PyJHora's own
# raasi_array -- exact agreement on which axes are zero.
DIST_TO_AXIS = {1: "1/1", 7: "1/7", 3: "3/11", 11: "3/11", 4: "4/10", 10: "4/10",
                2: "2/12", 12: "2/12", 5: "5/9", 9: "5/9", 6: "6/8", 8: "6/8"}
AXIS_RAW_SCORE = {"1/1": 7.0, "1/7": 7.0, "3/11": 5.0, "4/10": 5.0, "2/12": 0.0, "5/9": 0.0, "6/8": 0.0}
SIMPLE_CANCEL_AXES = {"2/12", "5/9"}


def mutual_friends(planet_a: str, planet_b: str) -> bool:
    if planet_a == planet_b:
        return True
    return naisargika_relationship(planet_a, planet_b) == "friend" and naisargika_relationship(planet_b, planet_a) == "friend"


def _is_exalted(chart: dict[str, Any], planet: str) -> bool:
    return chart[planet]["sign"] == PLANET_STATES[planet]["exalt"]


def bhakut_kuta(groom_sign: int, bride_sign: int, groom_chart: dict[str, Any], bride_chart: dict[str, Any]) -> dict[str, Any]:
    dist = ((bride_sign - groom_sign) % 12) + 1
    axis = DIST_TO_AXIS[dist]
    raw = AXIS_RAW_SCORE[axis]
    groom_lord = SIGNS[groom_sign - 1]["lord"]
    bride_lord = SIGNS[bride_sign - 1]["lord"]
    lords_friends = mutual_friends(groom_lord, bride_lord)

    cancelled = False
    effective = raw
    cancellation_basis = None
    if raw == 0.0 and axis in SIMPLE_CANCEL_AXES and lords_friends:
        cancelled, effective, cancellation_basis = True, 7.0, "sign_lords_mutual_friends"
    elif raw == 0.0 and axis == "6/8":
        # Guide's stated 6/8 cancellation needs mutual-friend lords AND at
        # least one exalted -- "whose chart" is not fully explicit in the
        # source text; interpreted here (disclosed, editorial) as each
        # lord's dignity within its OWN native's D1, since that is the
        # only per-lord dignity fact directly available from two single
        # charts without a full inter-chart D9 comparison.
        one_exalted = _is_exalted(groom_chart, groom_lord) or _is_exalted(bride_chart, bride_lord)
        if lords_friends and one_exalted:
            cancelled, effective, cancellation_basis = True, 7.0, "lords_mutual_friends_and_one_exalted"

    return {
        "distance_groom_to_bride": dist, "axis": axis,
        "groom_lord": groom_lord, "bride_lord": bride_lord, "lords_mutual_friends": lords_friends,
        "raw_score": raw, "effective_score": effective, "max_score": MAX_SCORES["bhakut"],
        "dosha_present_raw": raw == 0.0, "cancelled": cancelled, "cancellation_basis": cancellation_basis,
        "citation": "Muhurta Chintamani Bhakut Kuta + Bhakut Dosha Bhanga, Jyotish Ratnakar Ch.7; dosha-axis set cross-checked against PyJHora raasi_array",
    }


# ── Kuta 8: Nadi ─────────────────────────────────────────────────────────
def nadi_kuta(
    groom_nak_id: int, groom_pada: int, bride_nak_id: int, bride_pada: int,
    groom_sign: int, bride_sign: int, groom_chart: dict[str, Any], bride_chart: dict[str, Any],
) -> dict[str, Any]:
    groom_nadi = NAKSHATRA_PROFILES[groom_nak_id]["nadi"]
    bride_nadi = NAKSHATRA_PROFILES[bride_nak_id]["nadi"]
    same_nadi = groom_nadi == bride_nadi
    if not same_nadi:
        return {
            "groom_nadi": groom_nadi, "bride_nadi": bride_nadi, "dosha_present_raw": False,
            "raw_score": 8.0, "effective_score": 8.0, "max_score": MAX_SCORES["nadi"],
            "citation": "Muhurta Chintamani Nadi Dosha Adhyaya; grouping cross-checked exactly against PyJHora naadi_porutham() bvk/gvk array",
        }

    groom_nak_lord = NAKSHATRAS[groom_nak_id - 1]["lord"]
    bride_nak_lord = NAKSHATRAS[bride_nak_id - 1]["lord"]
    conditions = {
        "different_rashi": groom_sign != bride_sign,
        "different_nakshatra": groom_nak_id != bride_nak_id,
        "same_nakshatra_lord_different_nakshatra": groom_nak_id != bride_nak_id and groom_nak_lord == bride_nak_lord,
        "different_pada": groom_pada != bride_pada,
        "strong_jupiter_either_chart": _is_own_or_exalted(groom_chart, "Jupiter") or _is_own_or_exalted(bride_chart, "Jupiter"),
    }
    conditions_met = sum(conditions.values())
    # Marriage_Guide_Part3's own worked example treats "conditions met" as
    # a direct point count (4 of 5 met -> 4/8 effective), not a fraction of
    # the max -- a disclosed, source-demonstrated heuristic, not a fixed
    # universal formula (other texts treat any 2 conditions as a full
    # cancellation). Kept exactly as the source demonstrates it, per
    # Cardinal Rule 5.
    effective = float(min(8, conditions_met))
    return {
        "groom_nadi": groom_nadi, "bride_nadi": bride_nadi, "dosha_present_raw": True,
        "conditions": conditions, "conditions_met": conditions_met,
        "raw_score": 0.0, "effective_score": effective, "max_score": MAX_SCORES["nadi"],
        "citation": "Muhurta Chintamani Nadi Dosha Adhyaya + Nadi Bhanga Sl.3-4, Jyotish Ratnakar Ch.7 Sl.12 (cancellation conditions); mitigated-score heuristic per Marriage_Guide_Part3.md's own worked example",
    }


def _is_own_or_exalted(chart: dict[str, Any], planet: str) -> bool:
    states = PLANET_STATES[planet]
    sign = chart[planet]["sign"]
    return sign in states["own"] or sign == states["exalt"]


# ── Mangal Dosha matching ────────────────────────────────────────────────
def mangal_dosha_match(groom_ctx: dict[str, Any], bride_ctx: dict[str, Any]) -> dict[str, Any]:
    """Reuses app.derived.doshas.check_mangal_dosha's already-computed
    verdict for each chart (via ctx['doshas']['mangal_dosha']) rather than
    recomputing -- both-manglik mutual cancellation is already documented
    in docs/dosha-registry.md's exceptions table."""
    groom_md = groom_ctx["doshas"]["mangal_dosha"]
    bride_md = bride_ctx["doshas"]["mangal_dosha"]
    both_present = groom_md["present"] and bride_md["present"]
    either_present = groom_md["present"] or bride_md["present"]
    if both_present:
        verdict = "mutually_cancelled"
    elif either_present:
        verdict = "one_sided_concern"
    else:
        verdict = "not_applicable"
    return {
        "groom": groom_md, "bride": bride_md,
        "both_manglik": both_present, "verdict": verdict,
        "citation": "Jyotish Ratnakar Ch.5 Sl.8 + Vivaha Vrindavana Ch.3 (both-manglik mutual cancellation)",
    }


def _interpretation_band(effective_total: float) -> str:
    if effective_total >= 36:
        return "perfect"
    if effective_total >= 30:
        return "excellent"
    if effective_total >= 25:
        return "good"
    if effective_total >= 18:
        return "average"
    if effective_total >= 14:
        return "challenging"
    return "requires_strong_overriding_factors"


def ashtakuta_report(groom_ctx: dict[str, Any], bride_ctx: dict[str, Any]) -> dict[str, Any]:
    """Full 8-kuta Ashtakuta report + Mangal Dosha matching for two
    build_chart_context() outputs. See module docstring for cross-check
    provenance of every kuta's data table."""
    g_chart, b_chart = groom_ctx["chart"], bride_ctx["chart"]
    g_moon, b_moon = g_chart["Moon"], b_chart["Moon"]
    g_nak = groom_ctx["nakshatra_analysis"]["Moon"]
    b_nak = bride_ctx["nakshatra_analysis"]["Moon"]

    kutas = {
        "varna": varna_kuta(g_moon["sign"], b_moon["sign"]),
        "vasya": vasya_kuta(g_moon["sign"], g_moon["deg_in_sign"], b_moon["sign"], b_moon["deg_in_sign"]),
        "tara": tara_kuta(g_nak["nakshatra_id"], b_nak["nakshatra_id"]),
        "yoni": yoni_kuta(g_nak["nakshatra_id"], b_nak["nakshatra_id"]),
        "graha_maitri": graha_maitri_kuta(g_moon["sign"], b_moon["sign"]),
        "gana": gana_kuta(g_nak["nakshatra_id"], b_nak["nakshatra_id"]),
        "bhakut": bhakut_kuta(g_moon["sign"], b_moon["sign"], g_chart, b_chart),
        "nadi": nadi_kuta(
            g_nak["nakshatra_id"], g_nak["pada"], b_nak["nakshatra_id"], b_nak["pada"],
            g_moon["sign"], b_moon["sign"], g_chart, b_chart,
        ),
    }
    raw_total = round(sum(k["raw_score"] for k in kutas.values()), 2)
    effective_total = round(sum(k["effective_score"] for k in kutas.values()), 2)
    return {
        "kutas": kutas,
        "raw_total": raw_total, "effective_total": effective_total, "max_total": 36,
        "interpretation": _interpretation_band(effective_total),
        "mangal_dosha": mangal_dosha_match(groom_ctx, bride_ctx),
        "citation": "Muhurta Chintamani Vivaha Prakarana Sloka 1 (docs/marriage-compatibility-notes.md has the full per-kuta cross-check log)",
    }
