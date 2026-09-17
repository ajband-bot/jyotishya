"""Yoga detection engine (build_plan.md Phase 4).

**Re-baselined scope** (build_plan.md \u00a75a's own instruction: "read yoga.py's
full function list before finalizing scope, don't guess a number now"):
PyJHora's `horoscope/chart/yoga.py` implements **269 distinct named
yogas** (1034 raw functions including per-yoga `_from_jd_place` /
`_from_planet_positions` / `_calculation` wrapper variants) -- vastly more
than the original `LLM_ZERO_BRAINSTORM.md` estimate of "~50+". Compiling
all 269 with proper chapter/verse citations is a multi-week research task
this session does not have budget for, and many of the 269 are extremely
niche (e.g. specific-body-deformity yogas like `sirachcheda_yoga`,
`guhyaroga_yoga`) rather than central to a typical reading.

This module instead compiles the ~20 classically CENTRAL yogas that are
(a) already informally present in this codebase's v1 knowledge
(`app.knowledge.interpreter.detect_yogas`, `app.knowledge.houses
.RAJ_YOGA_COMBOS`) and/or (b) already scaffolded with real activation
conditions in `app/rules/bphs_top20_rule_cards_v1.yaml`'s YL-series cards
(Parivartana, Kendradhipati Dosha, named wealth yogas, Viparita Raja Yoga,
Graha Yuddha). The remaining ~249 are an explicitly tracked backlog, not
silently dropped -- see `docs/yoga-compilation-backlog.md`.

Every function returns a dict with "present"/"citation" (matching
`app.derived.doshas`'s established honesty pattern) -- no bare booleans.
"""
from __future__ import annotations

from typing import Any

from app.astro.constants import PLANET_STATES
from app.derived.aspects import KENDRA, TRIKONA, DUSHTHANA
from app.derived.dispositors import detect_mutual_receptions
from app.derived.factors import house_lord, rel_house

CLASSICAL_7 = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
NATURAL_BENEFICS = {"Moon", "Mercury", "Jupiter", "Venus"}
MAHAPURUSHA_PLANETS = {"Mars": "Ruchaka", "Mercury": "Bhadra", "Jupiter": "Hansa", "Venus": "Malavya", "Saturn": "Sasa"}


def _house_of(chart: dict[str, Any], planet: str) -> int:
    return chart[planet]["house"]


def _is_own_or_exalted(planet: str, sign: int) -> bool:
    ps = PLANET_STATES[planet]
    return sign in ps["own"] or sign == ps["exalt"]


# ── Chandra-based (lunar) yogas ─────────────────────────────────────────
def check_gajakesari_yoga(ctx: dict[str, Any]) -> dict[str, Any]:
    """BPHS Ch.36. Jupiter in a kendra (1/4/7/10) from Moon."""
    chart = ctx["chart"]
    distance = rel_house(_house_of(chart, "Moon"), _house_of(chart, "Jupiter"))
    return {"present": distance in KENDRA, "distance_from_moon": distance, "citation": "BPHS Ch.36"}


def check_sunapha_yoga(ctx: dict[str, Any]) -> dict[str, Any]:
    """BPHS Ch.37. A planet (other than Sun) in the 2nd house from Moon."""
    chart = ctx["chart"]
    moon_house = _house_of(chart, "Moon")
    second = ((moon_house) % 12) + 1
    occupants = [p for p in CLASSICAL_7 if p not in ("Moon", "Sun") and _house_of(chart, p) == second]
    return {"present": bool(occupants), "occupants": occupants, "citation": "BPHS Ch.37"}


def check_anapha_yoga(ctx: dict[str, Any]) -> dict[str, Any]:
    """BPHS Ch.37. A planet (other than Sun) in the 12th house from Moon."""
    chart = ctx["chart"]
    moon_house = _house_of(chart, "Moon")
    twelfth = ((moon_house - 2) % 12) + 1
    occupants = [p for p in CLASSICAL_7 if p not in ("Moon", "Sun") and _house_of(chart, p) == twelfth]
    return {"present": bool(occupants), "occupants": occupants, "citation": "BPHS Ch.37"}


def check_durudhara_yoga(ctx: dict[str, Any]) -> dict[str, Any]:
    """BPHS Ch.37. Planets occupy BOTH the 2nd and 12th from Moon simultaneously."""
    sunapha = check_sunapha_yoga(ctx)
    anapha = check_anapha_yoga(ctx)
    return {
        "present": sunapha["present"] and anapha["present"],
        "second_house_occupants": sunapha["occupants"],
        "twelfth_house_occupants": anapha["occupants"],
        "citation": "BPHS Ch.37",
    }


def check_chandra_mangala_yoga(ctx: dict[str, Any]) -> dict[str, Any]:
    """Saravali. Moon and Mars conjunct (same house)."""
    chart = ctx["chart"]
    present = _house_of(chart, "Moon") == _house_of(chart, "Mars")
    return {"present": present, "citation": "Saravali"}


def check_adhi_yoga(ctx: dict[str, Any]) -> dict[str, Any]:
    """BPHS/Saravali. Natural benefics (Mercury/Jupiter/Venus) occupy the
    6th, 7th, and/or 8th houses FROM MOON."""
    chart = ctx["chart"]
    moon_house = _house_of(chart, "Moon")
    target_houses = {((moon_house - 1 + offset) % 12) + 1 for offset in (5, 6, 7)}
    benefics_present = [p for p in ("Mercury", "Jupiter", "Venus") if _house_of(chart, p) in target_houses]
    return {"present": len(benefics_present) > 0, "benefics_in_6_7_8_from_moon": benefics_present, "citation": "BPHS/Saravali (common Adhi Yoga formulation)"}


# ── Sun-based yoga ──────────────────────────────────────────────────────
def check_budha_aditya_yoga(ctx: dict[str, Any]) -> dict[str, Any]:
    """Saravali. Mercury and Sun conjunct within 14 degrees (same sign)."""
    chart = ctx["chart"]
    same_sign = chart["Sun"]["sign"] == chart["Mercury"]["sign"]
    orb = abs(chart["Sun"]["deg_in_sign"] - chart["Mercury"]["deg_in_sign"]) if same_sign else None
    present = same_sign and orb is not None and orb < 14
    return {"present": present, "orb_deg": round(orb, 4) if orb is not None else None, "citation": "Saravali"}


# ── Pancha Mahapurusha Yogas (5) ────────────────────────────────────────
def check_pancha_mahapurusha_yogas(ctx: dict[str, Any]) -> dict[str, Any]:
    """BPHS Ch.75. Mars/Mercury/Jupiter/Venus/Saturn in own sign or
    exaltation, occupying a kendra (1/4/7/10) from Lagna."""
    chart = ctx["chart"]
    results = {}
    for planet, name in MAHAPURUSHA_PLANETS.items():
        house = _house_of(chart, planet)
        dignified = _is_own_or_exalted(planet, chart[planet]["sign"])
        present = dignified and house in KENDRA
        results[planet] = {"present": present, "yoga_name": name, "house": house, "dignified": dignified}
    return {"planets": results, "any_present": any(r["present"] for r in results.values()), "citation": "BPHS Ch.75"}


# ── Neechabhanga Raja Yoga ───────────────────────────────────────────────
def check_neechabhanga_raja_yoga(ctx: dict[str, Any]) -> dict[str, Any]:
    """BPHS. A debilitated planet's debility is cancelled when the sign
    lord of its debilitation sign occupies a kendra (from Lagna) --
    formalizes the check already informally present in
    app.knowledge.interpreter.detect_yogas."""
    chart = ctx["chart"]
    cancellations = []
    for planet in CLASSICAL_7:
        ps = PLANET_STATES[planet]
        if chart[planet]["sign"] != ps["debil"]:
            continue
        from app.astro.constants import SIGNS
        debil_sign_lord = SIGNS[ps["debil"] - 1]["lord"]
        dispositor_house = _house_of(chart, debil_sign_lord)
        if dispositor_house in KENDRA:
            cancellations.append({"planet": planet, "debilitation_sign_lord": debil_sign_lord, "dispositor_house": dispositor_house})
    return {"present": bool(cancellations), "cancellations": cancellations, "citation": "BPHS (Neechabhanga doctrine)"}


# ── Parivartana Yoga (formal classification, promoted from raw evidence) ─
def check_parivartana_yoga(ctx: dict[str, Any]) -> dict[str, Any]:
    """build_plan.md YL-001. Promotes app.derived.dispositors's raw mutual-
    reception evidence to a classified yoga: Maha (both houses kendra/
    trikona), Dainya/Kashta (either house a dusthana), or a plain/neutral
    exchange otherwise -- per Cardinal Rule 3, the raw structural fact and
    this formal classification are computed by two distinct, separately-
    testable functions, never silently merged into one."""
    chart = ctx["chart"]
    pairs = detect_mutual_receptions(chart)
    classified = []
    for pair in pairs:
        planet_a, planet_b = pair["planets"]
        house_a, house_b = _house_of(chart, planet_a), _house_of(chart, planet_b)
        if house_a in DUSHTHANA or house_b in DUSHTHANA:
            kind = "dainya_kashta"  # dusthana-involved exchange -- inauspicious
        elif (house_a in KENDRA or house_a in TRIKONA) and (house_b in KENDRA or house_b in TRIKONA):
            kind = "maha_parivartana"  # both kendra/trikona -- highly auspicious
        else:
            kind = "neutral_exchange"
        classified.append({"planets": [planet_a, planet_b], "houses": [house_a, house_b], "kind": kind})
    return {"present": bool(classified), "exchanges": classified, "citation": "build_plan.md YL-001 (Parivartana classification, applied to app.derived.dispositors's raw evidence)"}


# ── Kendradhipati Dosha (yoga-view wrapper over functional_nature) ──────
def check_kendradhipati_dosha(ctx: dict[str, Any]) -> dict[str, Any]:
    """build_plan.md YL-003 (also BPHS Ch.34). DRY wrapper: reuses the
    classification already computed in app.derived.functional_nature --
    does not recompute the dusthana/kendra/trikona logic a second time."""
    functional_nature = ctx["functional_nature"]["planets"]
    afflicted = [planet for planet, data in functional_nature.items() if data["classification"] == "kendradhipati_dosha"]
    return {"present": bool(afflicted), "planets": afflicted, "citation": "BPHS Ch.34 (via app.derived.functional_nature)"}


# ── Viparita Raja Yoga (3 subtypes) ──────────────────────────────────────
def check_viparita_raja_yoga(ctx: dict[str, Any]) -> dict[str, Any]:
    """build_plan.md YL-005. Harsha (6th lord in 6/8/12), Sarala (8th lord
    in 6/8/12), Vimala (12th lord in 6/8/12) -- the dusthana lord's
    placement in another dusthana neutralizes its own house's affliction."""
    chart = ctx["chart"]
    lagna_sign = ctx["lagna_sign"]
    subtypes = {"harsha": 6, "sarala": 8, "vimala": 12}
    results = {}
    for name, source_house in subtypes.items():
        lord = house_lord(lagna_sign, source_house)
        lord_house = _house_of(chart, lord)
        present = lord_house in DUSHTHANA
        results[name] = {"present": present, "source_house": source_house, "lord": lord, "lord_house": lord_house}
    return {"subtypes": results, "any_present": any(r["present"] for r in results.values()), "citation": "build_plan.md YL-005 (Harsha/Sarala/Vimala Viparita Raja Yoga)"}


# ── Graha Yuddha (planetary war) ─────────────────────────────────────────
def check_graha_yuddha(ctx: dict[str, Any]) -> dict[str, Any]:
    """build_plan.md YL-006. Two planets (excluding Sun/Moon/nodes) within
    1 degree of longitude. Winner-by-higher-longitude convention as stated
    in the YL-006 stub -- source_tier reflects this is an OCR-signal-only
    citation, not yet BPHS-chapter-pinned."""
    chart = ctx["chart"]
    combatants = [p for p in CLASSICAL_7 if p not in ("Sun", "Moon")]
    wars = []
    for i, planet_a in enumerate(combatants):
        for planet_b in combatants[i + 1:]:
            if chart[planet_a]["sign"] != chart[planet_b]["sign"]:
                continue
            diff = abs(chart[planet_a]["longitude"] - chart[planet_b]["longitude"])
            diff = min(diff, 360 - diff)
            if diff <= 1.0:
                winner = planet_a if chart[planet_a]["longitude"] > chart[planet_b]["longitude"] else planet_b
                loser = planet_b if winner == planet_a else planet_a
                wars.append({"planets": [planet_a, planet_b], "orb_deg": round(diff, 4), "winner": winner, "loser": loser})
    return {"present": bool(wars), "wars": wars, "citation": "build_plan.md YL-006 (stub_pending_translation -- winner-by-higher-longitude convention)"}


# ── Named wealth yogas (YL-004 partial: Kahala, Shankha; Chandra-Mangala above) ─
def check_kahala_yoga(ctx: dict[str, Any]) -> dict[str, Any]:
    """build_plan.md YL-004. 4th and 9th lords in mutual kendra from each other."""
    chart = ctx["chart"]
    lagna_sign = ctx["lagna_sign"]
    lord4, lord9 = house_lord(lagna_sign, 4), house_lord(lagna_sign, 9)
    mutual_kendra = rel_house(_house_of(chart, lord4), _house_of(chart, lord9)) in KENDRA
    return {"present": mutual_kendra, "lord4": lord4, "lord9": lord9, "citation": "build_plan.md YL-004 (stub_pending_translation)"}


def check_shankha_yoga(ctx: dict[str, Any]) -> dict[str, Any]:
    """build_plan.md YL-004. 5th and 6th lords in mutual kendra from each other."""
    chart = ctx["chart"]
    lagna_sign = ctx["lagna_sign"]
    lord5, lord6 = house_lord(lagna_sign, 5), house_lord(lagna_sign, 6)
    mutual_kendra = rel_house(_house_of(chart, lord5), _house_of(chart, lord6)) in KENDRA
    return {"present": mutual_kendra, "lord5": lord5, "lord6": lord6, "citation": "build_plan.md YL-004 (stub_pending_translation)"}


# ── Lakshmi Yoga (from app.knowledge.houses.RAJ_YOGA_COMBOS) ─────────────
def check_lakshmi_yoga(ctx: dict[str, Any]) -> dict[str, Any]:
    """9th lord in a kendra, in its own sign or exaltation."""
    chart = ctx["chart"]
    lagna_sign = ctx["lagna_sign"]
    lord9 = house_lord(lagna_sign, 9)
    house9_lord_house = _house_of(chart, lord9)
    present = house9_lord_house in KENDRA and _is_own_or_exalted(lord9, chart[lord9]["sign"])
    return {"present": present, "lord9": lord9, "lord9_house": house9_lord_house, "citation": "Common Parashari convention (app.knowledge.houses.RAJ_YOGA_COMBOS)"}


# ── Vasumati Yoga ─────────────────────────────────────────────────────────
def check_vasumati_yoga(ctx: dict[str, Any]) -> dict[str, Any]:
    """Common convention. Benefics occupy upachaya houses (3/6/10/11) from Lagna."""
    chart = ctx["chart"]
    upachaya = {3, 6, 10, 11}
    benefics_in_upachaya = [p for p in NATURAL_BENEFICS if _house_of(chart, p) in upachaya]
    return {"present": len(benefics_in_upachaya) >= 2, "benefics_in_upachaya": benefics_in_upachaya, "citation": "Common Parashari convention"}


# ── Amala Yoga ────────────────────────────────────────────────────────────
def check_amala_yoga(ctx: dict[str, Any]) -> dict[str, Any]:
    """Common convention. A benefic occupies the 10th house from Lagna OR from Moon."""
    chart = ctx["chart"]
    lagna_10th = 10
    moon_10th = ((_house_of(chart, "Moon") - 1 + 9) % 12) + 1
    from_lagna = [p for p in NATURAL_BENEFICS if _house_of(chart, p) == lagna_10th]
    from_moon = [p for p in NATURAL_BENEFICS if _house_of(chart, p) == moon_10th]
    return {"present": bool(from_lagna or from_moon), "benefics_10th_from_lagna": from_lagna, "benefics_10th_from_moon": from_moon, "citation": "Common Parashari convention"}


def compute_all_yogas(ctx: dict[str, Any]) -> dict[str, Any]:
    """Full yoga register -- the ~20-yoga Phase 4 tranche. See module
    docstring for the re-baselined scope disclosure (269 known, ~20 here,
    rest tracked in docs/yoga-compilation-backlog.md)."""
    return {
        "gajakesari": check_gajakesari_yoga(ctx),
        "sunapha": check_sunapha_yoga(ctx),
        "anapha": check_anapha_yoga(ctx),
        "durudhara": check_durudhara_yoga(ctx),
        "chandra_mangala": check_chandra_mangala_yoga(ctx),
        "adhi_yoga": check_adhi_yoga(ctx),
        "budha_aditya": check_budha_aditya_yoga(ctx),
        "pancha_mahapurusha": check_pancha_mahapurusha_yogas(ctx),
        "neechabhanga_raja_yoga": check_neechabhanga_raja_yoga(ctx),
        "parivartana": check_parivartana_yoga(ctx),
        "kendradhipati_dosha": check_kendradhipati_dosha(ctx),
        "viparita_raja_yoga": check_viparita_raja_yoga(ctx),
        "graha_yuddha": check_graha_yuddha(ctx),
        "kahala": check_kahala_yoga(ctx),
        "shankha": check_shankha_yoga(ctx),
        "lakshmi": check_lakshmi_yoga(ctx),
        "vasumati": check_vasumati_yoga(ctx),
        "amala": check_amala_yoga(ctx),
    }
