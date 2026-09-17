"""Single-chart Married-Life Synthesis -- domain-playbooks.md's Five-Pillar
Marriage Analysis Framework (build_plan.md Phase 6: "Marriage rules (40) --
beyond Phase 4a's compatibility module, this is the narrative/interpretation
layer for married-life readings").

Phase 4a already built INTER-chart marriage machinery (Ashtakuta matching,
synastry, Dasha/Transit/D9 timing) -- this module is the missing SINGLE-
chart piece: "what does THIS person's own chart say about their married
life," independent of any partner's chart. It composes primitives that
already exist and are already tested (house occupants, graha drishti,
dignity, functional nature, D9, Bhavapada) into the 5 named pillars, per
docs/domain-playbooks.md:

  1. 7th House        -- sign, occupants, aspecting planets
  2. 7th Lord         -- house placement, dignity, functional nature
  3. Marriage Karaka  -- Venus (male native) / Jupiter (female native).
     Both are always computed (never gender-gated at context-build time,
     matching this codebase's existing "preserve both, label clearly"
     convention for other formula ambiguities) -- the caller/narrative
     picks the one matching the native's gender.
  4. Darakaraka (DK)  -- D1 dignity + D9 sign/house/dignity
  5. Upapada Lagna    -- delegates to the already-built, already-verified
     app.derived.bhavapada Bhava-Arudha family (zero new Arudha math)

Every field here is a direct, already-computed primitive lookup --
computation_model is "practical_proxy" only where a genuinely NEW
compositional judgment is made (the benefic/malefic dominant-influence
verdict for the 7th house), and "classical" where a field is a raw
already-cited fact (dignity, house placement) passed through unchanged.
"""
from __future__ import annotations

from typing import Any

from app.astro.engine import planet_state

BENEFICS = {"Moon", "Mercury", "Jupiter", "Venus"}
MALEFICS = {"Sun", "Mars", "Saturn", "Rahu", "Ketu"}

FUNCTIONAL_BENEFIC_CLASSIFICATIONS = {"yoga_karaka", "functional_benefic", "functional_benefic_with_dusthana_mitigation"}
STRONG_DIGNITIES = {"exalted", "own-sign"}


def _dominant_influence(occupants: list[str], aspecting: list[str]) -> str:
    influencers = occupants + aspecting
    if not influencers:
        return "neutral"
    benefic_count = sum(1 for p in influencers if p in BENEFICS)
    malefic_count = sum(1 for p in influencers if p in MALEFICS)
    if benefic_count and not malefic_count:
        return "benefic"
    if malefic_count and not benefic_count:
        return "malefic"
    if benefic_count and malefic_count:
        return "mixed"
    return "neutral"


def seventh_house_report(ctx: dict[str, Any]) -> dict[str, Any]:
    """Pillar 1: docs/domain-playbooks.md's 7th House row."""
    chart = ctx["chart"]
    lagna_sign = ctx["lagna_sign"]
    sign = ((lagna_sign - 1 + 6) % 12) + 1
    occupants = [p for p in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"] if chart[p]["house"] == 7]
    aspecting = ctx["aspects"]["aspected_by"].get(7, [])
    return {
        "sign": sign,
        "occupants": occupants,
        "aspected_by": aspecting,
        "dominant_influence": _dominant_influence(occupants, aspecting),
        "citation": "docs/domain-playbooks.md Marriage Five-Pillar Framework, Pillar 1; BPHS Ch.11",
    }


def seventh_lord_report(ctx: dict[str, Any]) -> dict[str, Any]:
    """Pillar 2: docs/domain-playbooks.md's 7th Lord row -- reuses
    already-computed lord_placements/functional_nature, zero new math."""
    chart = ctx["chart"]
    lord = ctx["house_lords"][7]
    placement = ctx["lord_placements"][7]
    dignity_state = planet_state(lord, chart[lord]["sign"])
    functional = ctx["functional_nature"]["planets"].get(lord, {})
    return {
        "planet": lord,
        "occupies_house": placement["occupies_house"],
        "dignity_state": dignity_state,
        "functional_classification": functional.get("classification"),
        "is_maraka": functional.get("is_maraka", False),
        "citation": "docs/domain-playbooks.md Marriage Five-Pillar Framework, Pillar 2",
    }


def _karaka_report(ctx: dict[str, Any], planet: str, applies_to: str) -> dict[str, Any]:
    chart = ctx["chart"]
    return {
        "planet": planet,
        "applies_to_native_gender": applies_to,
        "house": chart[planet]["house"],
        "dignity_state": planet_state(planet, chart[planet]["sign"]),
        "combust": ctx["combustion"].get(planet, {}).get("combust", False),
        "citation": "docs/domain-playbooks.md Marriage Five-Pillar Framework, Pillar 3; BPHS Ch.32 (natural karakas)",
    }


def darakaraka_report(ctx: dict[str, Any]) -> dict[str, Any]:
    """Pillar 4: DK's D1 dignity plus its D9 sign/house/dignity (already
    computed by app.astro.engine.navamsha_d9 -- reused verbatim)."""
    chart = ctx["chart"]
    d9 = ctx["d9"]
    dk = ctx["karakas"]["darakaraka"]
    return {
        "planet": dk,
        "d1_house": chart[dk]["house"],
        "d1_dignity_state": planet_state(dk, chart[dk]["sign"]),
        "d9_sign_en": d9["dk_d9_sign_en"],
        "d9_house": d9["dk_d9_house"],
        "d9_dignity_state": d9["dk_d9_state"],
        "citation": "docs/domain-playbooks.md Marriage Five-Pillar Framework, Pillar 4 (Jaimini Darakaraka)",
    }


def upapada_report(ctx: dict[str, Any]) -> dict[str, Any]:
    """Pillar 5: delegates entirely to the already-built, already-verified
    Upapada/Bhavapada machinery -- no new Arudha math here."""
    upapada = ctx["upapada"]["canonical"]
    ul_sign = upapada["pada_sign"]
    ul_lord = upapada["lord"]
    return {
        "sign": ul_sign,
        "sign_en": upapada["pada_sign_en"],
        "lord": ul_lord,
        "lord_house": ctx["chart"][ul_lord]["house"],
        "formula_note": ctx["upapada"]["recommended_formula"],
        "citation": "docs/domain-playbooks.md Marriage Five-Pillar Framework, Pillar 5 (Jaimini Upapada)",
    }


def five_pillar_marriage_report(ctx: dict[str, Any]) -> dict[str, Any]:
    seventh_house = seventh_house_report(ctx)
    seventh_lord = seventh_lord_report(ctx)
    darakaraka = darakaraka_report(ctx)
    upapada = upapada_report(ctx)
    venus_karaka = _karaka_report(ctx, "Venus", "male")
    jupiter_karaka = _karaka_report(ctx, "Jupiter", "female")

    return {
        "seventh_house": seventh_house,
        "seventh_lord": seventh_lord,
        "venus_karaka": venus_karaka,
        "jupiter_karaka": jupiter_karaka,
        "darakaraka": darakaraka,
        "upapada": upapada,
        "model": "five_pillar_synthesis",
        "citation": "docs/domain-playbooks.md Marriage Analysis -- Five-Pillar Framework",
    }


def married_life_status(ctx: dict[str, Any]) -> dict[str, Any]:
    """Already-married native: STRENGTHS / CAUTIONS synthesis, per the
    Marriage Compatibility screen's own ask (build_plan.md Phase 8 UX
    follow-up). This is a PRESENTATION-layer composition, not new
    astrology math -- every fact quoted is already computed and already
    tested elsewhere: five_pillar_marriage_report (this module), the dosha
    register (app.derived.doshas), current running Vimshottari dasha
    (app.astro.dashas.current_dasha_antar, already in ctx['current_dasha']),
    and Sade Sati (app.astro.transits, surfaced at ctx['gochara']['sade_sati']).

    Deliberately does NOT attempt "will this marriage last / divorce risk"
    verdicts -- no classical framework in this project's source hierarchy
    (AGENTS.md 7) gives a computable formula for that; naming strengths and
    named, dated cautions is the honest scope (Cardinal Rule 9).
    """
    pillars = five_pillar_marriage_report(ctx)
    functional = ctx.get("functional_nature", {}).get("planets", {})
    doshas = ctx.get("doshas", {})
    current = ctx.get("current_dasha") or {}
    sade_sati = ctx.get("gochara", {}).get("sade_sati")

    strengths: list[dict[str, str]] = []
    cautions: list[dict[str, str]] = []

    influence = pillars["seventh_house"]["dominant_influence"]
    if influence == "benefic":
        strengths.append({"area": "7th House", "note": "7th house is occupied/aspected only by benefics -- a supportive foundation for domestic life.", "citation": pillars["seventh_house"]["citation"]})
    elif influence == "malefic":
        cautions.append({"area": "7th House", "note": "7th house is occupied/aspected only by malefics -- watch for friction or health/temperament strain on the marriage house.", "citation": pillars["seventh_house"]["citation"]})
    elif influence == "mixed":
        cautions.append({"area": "7th House", "note": "7th house carries a mixed benefic+malefic influence -- both support and strain are present; specifics depend on which planets and their own dignity.", "citation": pillars["seventh_house"]["citation"]})

    lord_classification = pillars["seventh_lord"]["functional_classification"]
    if lord_classification in FUNCTIONAL_BENEFIC_CLASSIFICATIONS:
        strengths.append({"area": "7th Lord", "note": f"7th lord {pillars['seventh_lord']['planet']} is a functional benefic ({lord_classification}) -- structurally favorable for the marriage house (BPHS Ch.34).", "citation": pillars["seventh_lord"]["citation"]})
    elif lord_classification == "functional_malefic":
        cautions.append({"area": "7th Lord", "note": f"7th lord {pillars['seventh_lord']['planet']} is functionally malefic for this Lagna -- its dasha/antardasha periods deserve extra care in the marriage (BPHS Ch.34).", "citation": pillars["seventh_lord"]["citation"]})
    if pillars["seventh_lord"]["is_maraka"]:
        cautions.append({"area": "7th Lord (Maraka)", "note": f"{pillars['seventh_lord']['planet']} also carries Maraka (2nd/7th lord) status -- its periods warrant caution for the spouse's health/vitality, not just relationship dynamics.", "citation": "Maraka doctrine, BPHS Ch.44"})

    mangal = doshas.get("mangal_dosha", {})
    if mangal.get("present"):
        if mangal.get("severity") == "cancelled":
            strengths.append({"area": "Mangal Dosha", "note": "Mangal Dosha is present but classically cancelled (Jupiter/Venus aspect-or-conjunction, or Mars own-sign/exalted) -- not an active concern.", "citation": mangal.get("citation", "BPHS Ch.77")})
        else:
            cautions.append({"area": "Mangal Dosha", "note": f"Mangal Dosha is active ({mangal.get('severity')}) and uncancelled in this single chart -- classically a caution for marital harmony/temperament, independent of the partner's chart.", "citation": mangal.get("citation", "BPHS Ch.77")})

    for level_key, level_label in (("mahadasha", "Mahadasha"), ("antardasha", "Antardasha")):
        planet = (current.get(level_key) or {}).get("planet")
        if not planet:
            continue
        classification = functional.get(planet, {}).get("classification")
        if classification in FUNCTIONAL_BENEFIC_CLASSIFICATIONS:
            strengths.append({"area": f"Current {level_label}", "note": f"Running {level_label} lord {planet} is a functional benefic -- a generally supportive period for domestic life right now.", "citation": "app.derived.functional_nature (BPHS Ch.34) x current_dasha"})
        elif classification == "functional_malefic":
            cautions.append({"area": f"Current {level_label}", "note": f"Running {level_label} lord {planet} is a functional malefic -- a period to actively manage friction rather than assume it will resolve itself.", "citation": "app.derived.functional_nature (BPHS Ch.34) x current_dasha"})

    if sade_sati and sade_sati.get("active"):
        cautions.append({"area": "Sade Sati", "note": f"Sade Sati is currently active ({sade_sati.get('label', 'unspecified phase')}) -- classically a household-stress/responsibility-load window; pairs well with deliberate Saturn remedies (see docs/domain-playbooks.md), not a fatalistic warning.", "citation": "Saturn-from-Moon doctrine, app.astro.transits.sade_sati_phase"})

    dk = pillars["darakaraka"]
    if dk["d1_dignity_state"] in STRONG_DIGNITIES or dk["d9_dignity_state"] in STRONG_DIGNITIES:
        strengths.append({"area": "Darakaraka", "note": f"Darakaraka {dk['planet']} (the spouse-significator) is strongly placed (D1 {dk['d1_dignity_state']} / D9 {dk['d9_dignity_state']}) -- a classically favorable signal for the marriage itself.", "citation": dk["citation"]})

    return {
        "strengths": strengths,
        "cautions": cautions,
        "five_pillar_summary": pillars,
        "active_doshas": {k: v for k, v in doshas.items() if isinstance(v, dict) and v.get("present")},
        "current_dasha": {
            "mahadasha": (current.get("mahadasha") or {}).get("planet"),
            "antardasha": (current.get("antardasha") or {}).get("planet"),
        },
        "sade_sati": sade_sati,
        "model": "married_life_synthesis",
        "citation": "Composed from docs/domain-playbooks.md Five-Pillar Framework + docs/dosha-registry.md, presentation-layer only",
    }
