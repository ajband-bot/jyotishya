from __future__ import annotations

from datetime import date
from typing import Any

from app.astro.constants import SIGNS
from app.astro.dashas import compute_dashas, current_dasha_antar
from app.astro.engine import all_planets_sidereal, is_combust, julian_day, navamsha_d9
from app.astro.panchanga import compute_panchanga
from app.astro.transits import transit_assessment
from app.derived.ashtakavarga import classical_ashtakavarga
from app.derived.aspects import full_aspect_report, graha_drishti_houses, planet_houses_from_d1_chart
from app.derived.bhava_bala import avastha_report, bhava_bala_report
from app.derived.dasha_synthesis import dasha_stack_synthesis
from app.derived.dignities import graha_maitri_report
from app.derived.nakshatra_analysis import nakshatra_analysis_report
from app.derived.dispositors import dispositor_report
from app.derived.functional_nature import functional_nature_report
from app.derived.gochara import gochara_report
from app.derived.house_graph import build_house_connection_graph
from app.derived.interventions import practical_argala
from app.derived.interventions import practical_argala

KENDRA = {1, 4, 7, 10}
TRIKONA = {1, 5, 9}


def sign_name(sign_no: int) -> str:
    return SIGNS[sign_no - 1]["en"]


def house_lord(lagna_sign: int, house_no: int) -> str:
    sign_no = ((lagna_sign - 1 + (house_no - 1)) % 12) + 1
    return SIGNS[sign_no - 1]["lord"]


def rel_house(from_house: int, to_house: int) -> int:
    return ((to_house - from_house) % 12) + 1


def house_to_sign(lagna_sign: int, house_no: int) -> int:
    return ((lagna_sign - 1 + (house_no - 1)) % 12) + 1


def planet_aspects(planet: str, from_house: int) -> list[int]:
    """Graha drishti for one planet -- delegates to app.derived.aspects so
    the special-aspect rules (Mars 4th/8th, Jupiter 5th/9th, Saturn
    3rd/10th) live in exactly one place, shared by the full aspects/drishti
    engine used elsewhere (build_chart_context's context["aspects"])."""
    return graha_drishti_houses(planet, from_house)


def maraka_lords(lagna_sign: int) -> dict[str, str]:
    return {
        "house_2_lord": house_lord(lagna_sign, 2),
        "house_7_lord": house_lord(lagna_sign, 7),
    }


def is_yoga_karaka(lagna_sign: int, planet: str) -> bool:
    """Classical yoga-karaka test (BPHS Ch.34): a planet that owns BOTH a
    kendra (4/7/10) and a trikona (5/9) house for this Lagna, via its two
    DIFFERENT owned signs.

    H1 is deliberately excluded from both sides of this check. H1 is
    simultaneously a kendra AND a trikona by definition, so any lagna lord
    who also owns one additional kendra house would otherwise be
    mis-flagged as a yoga-karaka purely by virtue of ruling H1 -- that is
    NOT the classical doctrine (a lagna lord is simply strong by default,
    never itself called 'yoga-karaka'). This bug was found independently in
    two narrative readings (Pisces/Jupiter and Gemini/Mercury lagna-lord
    cases) before being fixed here at the source.

    Verified against the standard classical yoga-karaka table:
    Taurus/Libra -> Saturn, Cancer/Leo -> Mars, Capricorn/Aquarius -> Venus.
    Aries/Scorpio (Mars), Gemini/Virgo (Mercury), Sagittarius/Pisces
    (Jupiter) correctly have NO yoga-karaka -- the dual-owned lagna lord's
    only trikona/kendra membership is the trivial H1.
    """
    owned = [house for house in range(1, 13) if house_lord(lagna_sign, house) == planet]
    owns_non_trivial_kendra = any(h in {4, 7, 10} for h in owned)
    owns_non_trivial_trikona = any(h in {5, 9} for h in owned)
    return owns_non_trivial_kendra and owns_non_trivial_trikona


def classical_karakas(chart: dict[str, Any]) -> dict[str, str]:
    classical = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
    atmakaraka = max(classical, key=lambda p: chart[p]["deg_in_sign"])
    darakaraka = min(classical, key=lambda p: chart[p]["deg_in_sign"])
    return {"atmakaraka": atmakaraka, "darakaraka": darakaraka}


def arudha_pada(lagna_sign: int, chart: dict[str, Any], source_house: int) -> dict[str, Any]:
    """Compute generic Arudha Pada for a house in whole-sign context.

    Rule used:
    - Determine source house sign and its lord.
    - Count distance from source house to lord's occupied house.
    - Count the same distance forward from the lord's house.
    - Exception: if lord is in the same house or the 7th from the source house,
      take the Arudha as the 10th from the lord's house.
    """
    source_sign = house_to_sign(lagna_sign, source_house)
    lord = house_lord(lagna_sign, source_house)
    lord_house = chart[lord]["house"]
    distance = rel_house(source_house, lord_house)

    if distance in {1, 7}:
        pada_house = ((lord_house - 1 + 9) % 12) + 1
        exception_used = True
    else:
        pada_house = ((lord_house - 1 + distance - 1) % 12) + 1
        exception_used = False

    pada_sign = house_to_sign(lagna_sign, pada_house)
    return {
        "source_house": source_house,
        "source_sign": source_sign,
        "source_sign_en": sign_name(source_sign),
        "lord": lord,
        "lord_house": lord_house,
        "distance": distance,
        "pada_house": pada_house,
        "pada_sign": pada_sign,
        "pada_sign_en": sign_name(pada_sign),
        "exception_used": exception_used,
    }


def lagna_pada(lagna_sign: int, chart: dict[str, Any]) -> dict[str, Any]:
    return arudha_pada(lagna_sign, chart, 1)


def upapada_lagna(lagna_sign: int, chart: dict[str, Any]) -> dict[str, Any]:
    return arudha_pada(lagna_sign, chart, 12)


def upapada_lagna_project_legacy(lagna_sign: int, chart: dict[str, Any]) -> dict[str, Any]:
    """Legacy project formula preserved for reconciliation with existing guides.

    Several markdown guides in this corpus compute UL as:
    - find the H12 lord's occupied house number from Lagna
    - count that many houses inclusively from H12

    This is not the same as the standard Arudha distance formula, but it is
    retained here so corpus disagreements remain visible rather than hidden.
    """
    source_house = 12
    source_sign = house_to_sign(lagna_sign, source_house)
    lord = house_lord(lagna_sign, source_house)
    lord_house = chart[lord]["house"]
    distance = lord_house
    pada_house = ((source_house - 1 + distance - 1) % 12) + 1
    pada_sign = house_to_sign(lagna_sign, pada_house)
    return {
        "source_house": source_house,
        "source_sign": source_sign,
        "source_sign_en": sign_name(source_sign),
        "lord": lord,
        "lord_house": lord_house,
        "distance": distance,
        "pada_house": pada_house,
        "pada_sign": pada_sign,
        "pada_sign_en": sign_name(pada_sign),
        "exception_used": False,
        "formula_mode": "project_guides_inclusive",
    }


def build_chart_context(fixture: dict[str, Any], today: date | None = None) -> dict[str, Any]:
    today = today or date.today()
    dob = date.fromisoformat(str(fixture["dob"]))
    hour, minute, second = [int(part) for part in fixture["time_local"].split(":")]
    hour_decimal = hour + minute / 60 + second / 3600

    settings = fixture.get("settings", {})
    node_type = settings.get("node_type", "mean")
    location = fixture["location"]
    jd = julian_day(dob.year, dob.month, dob.day, hour_decimal, fixture["utc_offset"])
    chart = all_planets_sidereal(jd, location["latitude"], location["longitude"], node_type=node_type)
    d9 = navamsha_d9(chart)
    dashas = compute_dashas(dob, chart["Moon"]["longitude"])
    current = current_dasha_antar(dashas, today=today)
    sun_lon = chart["Sun"]["longitude"]
    combustion = {
        planet: {
            "combust": is_combust(planet, chart[planet]["longitude"], sun_lon),
            "diff": round(min(abs(chart[planet]["longitude"] - sun_lon) % 360, 360 - (abs(chart[planet]["longitude"] - sun_lon) % 360)), 4),
        }
        for planet in ["Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
    }
    lagna_sign = chart["Lagna"]["sign"]
    karakas = classical_karakas(chart)
    lagna_pada_data = lagna_pada(lagna_sign, chart)
    upapada_data = upapada_lagna(lagna_sign, chart)
    upapada_legacy = upapada_lagna_project_legacy(lagna_sign, chart)
    transits = transit_assessment(chart, today, node_type=node_type)
    from app.derived.strengths import simplified_ishta_kashta, simplified_shadbala, simplified_varga_quality

    aspect_map = {planet: planet_aspects(planet, chart[planet]["house"]) for planet in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]}

    shadbala = simplified_shadbala({
        "fixture": fixture,
        "chart": chart,
        "d9": d9,
        "combustion": combustion,
        "aspect_map": aspect_map,
    })
    varga_quality = simplified_varga_quality({"chart": chart, "d9": d9})
    ishta_kashta = simplified_ishta_kashta({
        "chart": chart,
        "d9": d9,
        "combustion": combustion,
        "aspect_map": aspect_map,
        "fixture": fixture,
    }, shadbala=shadbala)
    argala = practical_argala({
        "chart": chart,
        "shadbala": shadbala,
        "yoga_karakas": [planet for planet in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"] if is_yoga_karaka(lagna_sign, planet)],
        "lagna_pada": lagna_pada_data,
    }, shadbala=shadbala)
    ashtakavarga = classical_ashtakavarga({"chart": chart, "transits": transits})
    panchanga = compute_panchanga(sun_lon, chart["Moon"]["longitude"], dob)
    planet_houses_d1 = planet_houses_from_d1_chart(chart)
    aspects = full_aspect_report(planet_houses_d1)
    graha_maitri = graha_maitri_report(planet_houses_d1)
    yoga_karakas = [planet for planet in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"] if is_yoga_karaka(lagna_sign, planet)]
    house_lords_map = {house: house_lord(lagna_sign, house) for house in range(1, 13)}
    house_graph = build_house_connection_graph(house_lords_map, planet_houses_d1)
    functional_nature = functional_nature_report(lagna_sign, house_lord)
    dispositors = dispositor_report(chart)
    lord_placements = {
        house: {"lord": house_lords_map[house], "occupies_house": chart[house_lords_map[house]]["house"]}
        for house in range(1, 13)
    }
    from app.derived.doshas import compute_all_doshas
    doshas_ctx = {"chart": chart, "lagna_sign": lagna_sign, "aspect_map": aspect_map}
    doshas = compute_all_doshas(doshas_ctx)
    avasthas = avastha_report(chart)
    bhava_bala = bhava_bala_report(house_lords_map, chart, shadbala, aspect_map)
    from app.derived.yogas import compute_all_yogas
    yogas = compute_all_yogas({
        "chart": chart,
        "lagna_sign": lagna_sign,
        "functional_nature": functional_nature,
    })
    nakshatra_analysis = nakshatra_analysis_report(chart)
    from app.derived.bhavapada import bhavapada_report
    bhavapada = bhavapada_report(lagna_sign, chart)
    dasha_synthesis = dasha_stack_synthesis({
        "current_dasha": current,
        "functional_nature": functional_nature,
        "avasthas": avasthas,
        "dispositors": dispositors,
        "bhava_bala": bhava_bala,
        "transits": transits,
    })
    gochara = gochara_report({"chart": chart, "transits": transits, "ashtakavarga": ashtakavarga})
    from app.derived.vimsopaka import all_schemes_vimsopaka_bala
    vimsopaka = all_schemes_vimsopaka_bala(chart)
    from app.derived.shadbala import full_shadbala
    shadbala_classical = full_shadbala({
        "chart": chart, "lagna_sign": lagna_sign, "fixture": fixture, "jd": jd, "yogas": yogas,
    })
    from app.derived.ishta_kashta import classical_ishta_kashta
    ishta_kashta_classical = classical_ishta_kashta({"chart": chart})
    context = {
        "fixture": fixture,
        "settings": settings,
        "jd": jd,
        "chart": chart,
        "d9": d9,
        "dashas": dashas,
        "current_dasha": current,
        "combustion": combustion,
        "lagna_sign": lagna_sign,
        "house_lords": {house: house_lord(lagna_sign, house) for house in range(1, 13)},
        "maraka_lords": maraka_lords(lagna_sign),
        "karakas": karakas,
        "lagna_pada": lagna_pada_data,
        "upapada": {
            "canonical": upapada_data,
            "project_guides": upapada_legacy,
            "matches": upapada_data["pada_sign"] == upapada_legacy["pada_sign"],
            "recommended_formula": "canonical_standard_arudha",
        },
        "transits": transits,
        "shadbala": shadbala,
        "varga_quality": varga_quality,
        "ishta_kashta": ishta_kashta,
        "argala": argala,
        "ashtakavarga": ashtakavarga,
        "panchanga": panchanga,
        "aspects": aspects,
        "graha_maitri": graha_maitri,
        "yoga_karakas": yoga_karakas,
        "aspect_map": aspect_map,
        "house_graph": house_graph,
        "functional_nature": functional_nature,
        "dispositors": dispositors,
        "lord_placements": lord_placements,
        "doshas": doshas,
        "avasthas": avasthas,
        "bhava_bala": bhava_bala,
        "yogas": yogas,
        "nakshatra_analysis": nakshatra_analysis,
        "bhavapada": bhavapada,
        "dasha_synthesis": dasha_synthesis,
        "gochara": gochara,
        "vimsopaka": vimsopaka,
        "shadbala_classical": shadbala_classical,
        "ishta_kashta_classical": ishta_kashta_classical,
    }

    from app.derived.marriage_analysis import five_pillar_marriage_report
    from app.derived.career_analysis import career_analysis_report
    from app.derived.remedies import remedy_report
    context["marriage_analysis"] = five_pillar_marriage_report(context)
    context["career_analysis"] = career_analysis_report(context)
    context["remedies"] = remedy_report(context)
    return context
