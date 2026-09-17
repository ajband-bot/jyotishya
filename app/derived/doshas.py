"""Dosha (affliction) calculators -- BPHS Ch.77/80/24 + Saravali.

This fills a REAL gap: docs/dosha-registry.md mandates 8 doshas be checked
for every chart (Mangala, Kala Sarpa, Pitru, Guru Chandala, Kemadruma,
Papakartari, Ghata, Shrapit) plus Sade Sati. Before this module, only Sade
Sati existed as code (app/astro/transits.py) -- the rest existed ONLY as
prose (or not at all) in the registry, meaning every narrative reading had
to re-derive them by hand each time. Ghata and Shrapit were added during
build_plan.md Phase 4's registry recheck against PyJHora's dosha.py
coverage (see docs/dosha-registry.md's own disclosure note on both -- they
are widely-cited Parashari conventions, not yet chapter/verse-confirmed
against a primary BPHS passage, same honesty standard already applied to
Kala Sarpa). This is exactly the kind of corpus/engine gap the Cheat-Sheet
Validation Console is meant to surface and then close.

Every function returns a dict with "present", "citation", and enough
"evidence" fields to trace the verdict -- no bare booleans.
"""
from __future__ import annotations

from typing import Any

from app.derived.factors import house_lord, rel_house
from app.astro.constants import PLANET_STATES

MANGAL_DOSHA_HOUSES = {1, 2, 4, 7, 8, 12}

# BPHS Ch.77 house-specific full-cancellation table: Mars in this house is
# NOT a dosha at all if the Lagna sign matches (Mars there is dignified).
MANGAL_HOUSE_CANCELLATION_LAGNAS = {
    1: {1, 5, 11},   # Aries, Leo, Aquarius
    2: {3, 6},       # Gemini, Virgo
    4: {1, 8},       # Aries, Scorpio
    7: {4, 10},      # Cancer, Capricorn
    8: {9, 12},      # Sagittarius, Pisces
    12: {2, 7},      # Taurus, Libra
}

MALEFICS = {"Sun", "Mars", "Saturn", "Rahu", "Ketu"}
CLASSICAL_7 = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]


def _house_of(chart: dict[str, Any], planet: str) -> int:
    return chart[planet]["house"]


def check_mangal_dosha(ctx: dict[str, Any]) -> dict[str, Any]:
    """BPHS Ch.77. Checked from Lagna, Moon, and Venus independently."""
    chart = ctx["chart"]
    lagna_sign = ctx["lagna_sign"]
    mars_house = _house_of(chart, "Mars")

    references = {}
    for ref_name, ref_house in [
        ("lagna", 1),
        ("moon", chart["Moon"]["house"]),
        ("venus", chart["Venus"]["house"]),
    ]:
        rel = rel_house(ref_house, mars_house)
        present = rel in MANGAL_DOSHA_HOUSES
        house_cancelled = (
            present and ref_name == "lagna" and
            lagna_sign in MANGAL_HOUSE_CANCELLATION_LAGNAS.get(rel, set())
        )
        references[ref_name] = {
            "mars_house_from_ref": rel,
            "present": present and not house_cancelled,
            "house_dignity_cancellation": house_cancelled,
        }

    aspected_by_jupiter_or_venus = any(
        mars_house in ctx["aspect_map"].get(p, []) for p in ("Jupiter", "Venus")
    )
    conjunct_jupiter = chart["Jupiter"]["house"] == mars_house
    conjunct_moon = chart["Moon"]["house"] == mars_house  # Chandra-Mangala Yoga
    # docs/dosha-registry.md cancellation condition #1: "Mars in own sign
    # (Aries, Scorpio) or exalted (Capricorn) in the dosha house" -- this is
    # a GENERAL dignity check (any Lagna), distinct from the specific
    # per-Lagna table above (MANGAL_HOUSE_CANCELLATION_LAGNAS, conditions
    # #5-10). Found missing during build_plan.md Phase 3's composer-vs-LLM
    # diff exercise: the LLM narrative for ajay_kumar correctly applied this
    # condition ("Mars IS in own sign Scorpio in H1 -- CANCELLATION MET")
    # but this function did not check it at all before this fix.
    mars_sign = chart["Mars"]["sign"]
    mars_states = PLANET_STATES["Mars"]
    mars_own_or_exalted = mars_sign in mars_states["own"] or mars_sign == mars_states["exalt"]

    hits = [r for r in references.values() if r["present"]]
    mitigated = aspected_by_jupiter_or_venus or conjunct_jupiter or mars_own_or_exalted
    if not hits:
        severity = "not_present"
    elif mitigated and len(hits) < 3:
        severity = "cancelled"
    elif len(hits) == 3:
        severity = "severe"
    else:
        severity = "moderate"

    return {
        "present": len(hits) > 0,
        "severity": severity,
        "references": references,
        "jupiter_venus_aspect_or_conjunction": aspected_by_jupiter_or_venus or conjunct_jupiter,
        "mars_own_or_exalted_in_occupied_sign": mars_own_or_exalted,
        "chandra_mangala_yoga_present": conjunct_moon,
        "note": "Mutual dosha-cancellation via partner's chart cannot be checked from a single chart -- data_gap for that specific condition.",
        "citation": "BPHS Ch.77",
    }


def check_kala_sarpa(ctx: dict[str, Any]) -> dict[str, Any]:
    """All 7 classical planets hemmed on one side of the Rahu-Ketu axis (whole-sign)."""
    chart = ctx["chart"]
    rahu_sign = chart["Rahu"]["sign"]
    ketu_sign = chart["Ketu"]["sign"]

    def signs_from_rahu(sign: int) -> int:
        return ((sign - rahu_sign) % 12)

    positions = {p: signs_from_rahu(chart[p]["sign"]) for p in CLASSICAL_7}
    rahu_to_ketu_arc = signs_from_rahu(ketu_sign)  # always 6 (opposite sign)
    all_between = all(0 < pos < rahu_to_ketu_arc for pos in positions.values())
    all_other_side = all(pos > rahu_to_ketu_arc for pos in positions.values())
    full = all_between or all_other_side

    conjunct_node = any(
        chart[p]["sign"] in (rahu_sign, ketu_sign) for p in CLASSICAL_7
    )
    return {
        "present": full,
        "type": "full" if full and not conjunct_node else ("partial" if full else "not_present"),
        "planet_positions_from_rahu_signs": positions,
        "citation": "Classical Kala Sarpa doctrine (not in core BPHS; widely-used convention)",
        "citation_status": "pending_audit",
    }


def check_pitru_dosha(ctx: dict[str, Any]) -> dict[str, Any]:
    """BPHS Ch.80: Sun afflicted by Rahu/Saturn in H9, OR 9th lord afflicted."""
    chart = ctx["chart"]
    lagna_sign = ctx["lagna_sign"]
    ninth_lord = house_lord(lagna_sign, 9)
    sun_house = chart["Sun"]["house"]

    sun_conjunct_affliction = any(
        chart[p]["house"] == sun_house for p in ("Rahu", "Saturn")
    ) and sun_house == 9
    sun_aspected_by_affliction = sun_house == 9 and any(
        sun_house in ctx["aspect_map"].get(p, []) for p in ("Rahu", "Saturn")
    )
    ninth_lord_house = chart[ninth_lord]["house"]
    ninth_lord_afflicted = any(
        (chart[p]["house"] == ninth_lord_house or ninth_lord_house in ctx["aspect_map"].get(p, []))
        for p in ("Rahu", "Saturn")
        if p != ninth_lord  # a planet cannot 'afflict' itself via self-conjunction
    )
    present = sun_conjunct_affliction or sun_aspected_by_affliction or ninth_lord_afflicted
    return {
        "present": present,
        "sun_in_h9_afflicted": sun_conjunct_affliction or sun_aspected_by_affliction,
        "ninth_lord": ninth_lord,
        "ninth_lord_afflicted": ninth_lord_afflicted,
        "citation": "BPHS Ch.80",
    }


def _conjunction_within_orb(chart: dict[str, Any], planet_a: str, planet_b: str, orb_deg: float = 15.0) -> dict[str, Any]:
    """Shared same-sign + degree-orb conjunction test, reused by
    Guru Chandala, Ghata, and Shrapit doshas below -- all three are
    structurally the SAME check (two specific planets conjunct within an
    orb), just with different planet pairs and different classical labels.
    Keeping one implementation avoids the three checks silently drifting
    on orb convention over time."""
    same_sign = chart[planet_a]["sign"] == chart[planet_b]["sign"]
    diff = abs(chart[planet_a]["longitude"] - chart[planet_b]["longitude"]) % 360
    diff = min(diff, 360 - diff)
    present = same_sign and diff <= orb_deg
    return {"present": present, "orb_deg": round(diff, 4) if same_sign else None}


def check_guru_chandala(ctx: dict[str, Any]) -> dict[str, Any]:
    """Jupiter conjunct Rahu within 15 degrees, same sign."""
    chart = ctx["chart"]
    result = _conjunction_within_orb(chart, "Jupiter", "Rahu")
    return {
        "present": result["present"],
        "orb_deg": result["orb_deg"],
        "citation": "Saravali / common Parashari convention",
    }


def check_ghata_dosha(ctx: dict[str, Any]) -> dict[str, Any]:
    """Mars conjunct Saturn within 15 degrees, same sign. Cross-checked
    (AD-4, data-only formula shape, no code copied) against PyJHora's
    horoscope/chart/dosha.py::ghata() -- their convention is bare
    same-sign equality with no orb; this codebase applies the same 15-deg
    orb already used for Guru Chandala for internal consistency (a
    disclosed harmonization choice, not a silent invention)."""
    chart = ctx["chart"]
    result = _conjunction_within_orb(chart, "Mars", "Saturn")
    return {
        "present": result["present"],
        "orb_deg": result["orb_deg"],
        "citation": "Widely-cited Parashari convention (Mars/Saturn 'collision' dosha); cross-checked against PyJHora dosha.py::ghata() for formula shape only",
        "citation_status": "pending_audit",
    }


def check_shrapit_dosha(ctx: dict[str, Any]) -> dict[str, Any]:
    """Rahu conjunct Saturn within 15 degrees, same sign ('cursed' dosha).
    Cross-checked (AD-4, data-only) against PyJHora's
    horoscope/chart/dosha.py::shrapit(); same disclosed 15-deg-orb
    harmonization as check_ghata_dosha."""
    chart = ctx["chart"]
    result = _conjunction_within_orb(chart, "Rahu", "Saturn")
    return {
        "present": result["present"],
        "orb_deg": result["orb_deg"],
        "citation": "Widely-cited Parashari convention (Rahu/Saturn 'Shrapit'/cursed dosha); cross-checked against PyJHora dosha.py::shrapit() for formula shape only",
        "citation_status": "pending_audit",
    }


def check_kemadruma(ctx: dict[str, Any]) -> dict[str, Any]:
    """BPHS Ch.24: no planet in 2nd or 12th from Moon, with kendra cancellations."""
    chart = ctx["chart"]
    moon_house = chart["Moon"]["house"]
    second_from_moon = ((moon_house) % 12) + 1
    twelfth_from_moon = ((moon_house - 2) % 12) + 1
    others = [p for p in CLASSICAL_7 if p != "Moon"]
    occupied = any(chart[p]["house"] in (second_from_moon, twelfth_from_moon) for p in others)

    moon_in_kendra = moon_house in {1, 4, 7, 10}
    any_in_kendra_from_lagna = any(chart[p]["house"] in {1, 4, 7, 10} for p in others)
    benefic_aspects_moon = any(
        moon_house in ctx["aspect_map"].get(p, []) for p in ("Jupiter", "Venus")
    )
    raw_present = not occupied
    cancelled = raw_present and (moon_in_kendra or any_in_kendra_from_lagna or benefic_aspects_moon)
    return {
        "present": raw_present and not cancelled,
        "raw_condition_met": raw_present,
        "cancelled": cancelled,
        "moon_in_kendra": moon_in_kendra,
        "citation": "BPHS Ch.24",
    }


def check_papakartari(ctx: dict[str, Any]) -> dict[str, list[int]]:
    """A house hemmed between two malefics (one before, one after), any of 12 houses."""
    chart = ctx["chart"]
    afflicted_houses = []
    for house_no in range(1, 13):
        before = ((house_no - 2) % 12) + 1
        after = (house_no % 12) + 1
        before_malefic = any(chart[p]["house"] == before for p in MALEFICS if p in chart)
        after_malefic = any(chart[p]["house"] == after for p in MALEFICS if p in chart)
        if before_malefic and after_malefic:
            afflicted_houses.append(house_no)
    return {
        "afflicted_houses": afflicted_houses,
        "present": len(afflicted_houses) > 0,
        "citation": "General Parashari principle (papa-kartari-yoga)",
    }


def compute_all_doshas(ctx: dict[str, Any]) -> dict[str, Any]:
    """Full doṣa register per docs/dosha-registry.md -- the 8 mandatory
    checks (Sade Sati is computed separately in app/astro/transits.py and
    already surfaced via ctx['transits']['sade_sati']). Ghata and Shrapit
    were added in build_plan.md Phase 4's dosha-registry recheck (they
    weren't in the original 6-item registry) -- both are honestly labeled
    citation_status: pending_audit, same disclosed treatment as Kala Sarpa
    (a widely-cited convention, not chapter/verse-confirmed against a
    primary BPHS passage yet), per Cardinal Rule 5."""
    return {
        "mangal_dosha": check_mangal_dosha(ctx),
        "kala_sarpa": check_kala_sarpa(ctx),
        "pitru_dosha": check_pitru_dosha(ctx),
        "guru_chandala": check_guru_chandala(ctx),
        "kemadruma": check_kemadruma(ctx),
        "papakartari": check_papakartari(ctx),
        "ghata_dosha": check_ghata_dosha(ctx),
        "shrapit_dosha": check_shrapit_dosha(ctx),
    }
