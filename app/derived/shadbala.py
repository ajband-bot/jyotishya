"""Full classical Shadbala (six-fold planetary strength), BPHS Ch.27 --
build_plan.md Phase 5 ("Full Shadbala -- read OpenJyotish's own
tools/xcheck/TRIAGE.md first... resolve from BPHS text, don't just pick
one").

Per that instruction, `public-git-repos/OpenJyotish-main/tools/xcheck/
TRIAGE.md` was read first (TRIAGE-4 flags Shadbala model variants --
Paksha graded/binary, Tribhaga, Ojha/Drek granularity, Kala Bala split
vs combined, Ayana scale, Drik signed-vs-binned, Chesta declination --
as genuinely CONTESTED, needing primary-text audit, "do not fix by
copying their numbers"). Per that same instruction, the actual primary
text (`Reference books/BPHS - 1 RSanthanam.pdf`, Ch.27) was then read
directly (via `pdftotext -layout`, per AGENTS.md AD-8's "read PDFs
manually" policy) rather than guessing or importing either reference
repo's specific numbers.

Every component below is EITHER (a) computed with full classical
precision, directly transcribed from Ch.27's verses, or (b) an explicit,
disclosed `data_gap` where the primary-text excerpt was itself
insufficient (truncated OCR, or a component TRIAGE.md independently
flags as unresolved even among two well-established open-source
implementations) -- never a silent guess. This is a genuine engine
upgrade over `app.derived.strengths.simplified_shadbala` (a 0-100
practical proxy, left untouched and still used by ishta/kashta and varga
quality) -- this module produces classical Virupa/Rupa units instead.

Disclosed gaps (see individual functions for detail):
  - Varsha (year) lord and Masa (month) lord, 2 of Kala Bala's 6 sub-
    parts: BPHS's own method needs a precise Ahargana (days-since-
    Creation epoch) derivation of the astrological year/month START --
    a genuinely separate, tedious classical calendrical calculation the
    source text itself calls "a very tedious process." Not attempted
    this pass rather than risk a wrong epoch.
  - Chesta Bala for the 5 non-luminary planets (Mars-Saturn): needs an
    8-tier motion-speed classification (Vakra/Anuvakra/Vikala/Manda/
    Mandatara/Sama/Chara/Atichara) whose exact numeric tier BOUNDARIES
    are not given in the extracted excerpt (only the category names and
    point values). Sun/Moon's Chesta Bala IS fully computed (BPHS gives
    them as direct aliases of Ayana Bala / Paksha Bala respectively).
  - Drik Bala (aspectual strength): the extracted excerpt is visibly
    truncated (missing the full per-aspect Drishti Pinda degree table)
    and TRIAGE-4 independently flags this exact component as contested
    ("signed continuous Drik vs 0/15 bins"). Disclosed data_gap.
"""
from __future__ import annotations

from typing import Any

from app.astro.constants import PLANET_STATES, SIGNS
from app.astro.sunrise import day_night_context
from app.astro.vargas import compute_varga
from app.derived.dignities import graha_maitri_report
from app.derived.factors import house_to_sign
from app.derived.reference_tables import MOOLATRIKONA

CLASSICAL_7 = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
MIN_REQUIRED_RUPAS = {"Sun": 6.5, "Moon": 6.0, "Mars": 5.0, "Mercury": 7.0, "Jupiter": 6.5, "Venus": 5.5, "Saturn": 5.0}


# ── Sthana Bala (positional strength) -- 5 sub-components ──────────────
def debilitation_distance(planet: str, longitude: float) -> float:
    """Folded (<=180 deg) angular distance from the planet's deep
    DEBILITATION point -- the shared primitive behind BOTH Uchcha Bala
    (this module, /3 = Virupas) and Uchcha Rasmi (app.derived.ishta_kashta,
    a different Ch.28 scaling of the exact same distance). Factored out
    here rather than duplicated, per DRY -- both chapters start from the
    identical classical measurement."""
    states = PLANET_STATES[planet]
    debil_longitude = (states["debil"] - 1) * 30 + states["exalt_deg"]
    diff = abs(longitude - debil_longitude) % 360
    if diff > 180:
        diff = 360 - diff
    return diff


def uchcha_bala(planet: str, longitude: float) -> float:
    """BPHS Ch.27 v.1: distance from the planet's deep DEBILITATION point
    (folded to <=180 deg), /3 = Virupas (max 60, at exact exaltation)."""
    return round(debilitation_distance(planet, longitude) / 3, 4)


DIGNITY_VIRUPA_POINTS = {"moolatrikona": 45, "own": 30, "adhi_mitra": 20, "mitra": 15, "sama": 10, "shatru": 4, "adhi_shatru": 2}
SAPTAVARGA_FACTORS = (1, 2, 3, 7, 9, 12, 30)


def _saptavarga_tier(planet: str, sign: int, planet_houses: dict[str, int], deg_in_sign: float | None) -> str:
    """BPHS's OWN Ch.27 v.2-4 wording lists Moolatrikona/Own/5-tier-
    Panchadha ONLY -- it does NOT mention exaltation as a separate bonus
    tier here (unlike Vimsopaka Bala's own-or-exalt convention, a
    DIFFERENT Bala with its own, separately-cited rule in
    app.derived.vimsopaka). Deliberately not adding an unstated
    exaltation bonus -- some later commentators/software do; that is a
    disclosed, real variant, not silently adopted here."""
    if deg_in_sign is not None:
        mt = MOOLATRIKONA[planet]
        if sign == mt["sign"] and mt["range"][0] <= deg_in_sign < mt["range"][1]:
            return "moolatrikona"
    if sign in PLANET_STATES[planet]["own"]:
        return "own"
    lord = SIGNS[sign - 1]["lord"]
    if lord == planet:
        return "own"
    relationships = graha_maitri_report(planet_houses)["planets"][planet]["relationships"]
    return relationships.get(lord, {}).get("panchadha", "sama")


def saptavargaja_bala(planet: str, d1_chart: dict[str, Any]) -> dict[str, Any]:
    """BPHS Ch.27 v.2-4: sum of dignity-tier Virupas across 7 vargas
    (Rasi/Hora/Drekkana/Saptamsa/Navamsa/Dvadasamsa/Trimsamsa)."""
    breakdown: dict[str, Any] = {}
    total = 0.0
    for n in SAPTAVARGA_FACTORS:
        if n == 1:
            sign = d1_chart[planet]["sign"]
            deg_in_sign = d1_chart[planet]["deg_in_sign"]
            planet_houses = {p: d1_chart[p]["house"] for p in CLASSICAL_7}
        else:
            varga = compute_varga(d1_chart, n)
            sign = varga["planets"][planet]["sign"]
            deg_in_sign = None
            planet_houses = {p: varga["planets"][p]["house"] for p in CLASSICAL_7 if p in varga["planets"]}
        tier = _saptavarga_tier(planet, sign, planet_houses, deg_in_sign)
        points = DIGNITY_VIRUPA_POINTS[tier]
        breakdown[f"D{n}"] = {"sign": sign, "tier": tier, "points": points}
        total += points
    return {"total": total, "breakdown": breakdown}


_MALE_PLANETS = {"Sun", "Mars", "Jupiter"}
_FEMALE_PLANETS = {"Moon", "Venus"}


def ojhayugma_bala(planet: str, d1_chart: dict[str, Any]) -> float:
    """BPHS Ch.27 v.4 (Ojhayugmarasiamsa Bala): 15 Virupas each for Rasi
    AND Navamsa placement matching the planet's gender-to-sign-parity
    rule (male/neutral planets favor odd signs, female favor even) --
    max 30."""
    d9_sign = compute_varga(d1_chart, 9)["planets"][planet]["sign"]
    total = 0.0
    for sign in (d1_chart[planet]["sign"], d9_sign):
        is_odd = sign % 2 == 1
        if planet in _FEMALE_PLANETS:
            total += 15.0 if not is_odd else 0.0
        else:  # male + neutral (Mercury/Saturn) planets favor odd signs per BPHS's own wording
            total += 15.0 if is_odd else 0.0
    return total


KENDRA_HOUSES, PANAPARA_HOUSES, APOKLIMA_HOUSES = {1, 4, 7, 10}, {2, 5, 8, 11}, {3, 6, 9, 12}


def kendradi_bala(house: int) -> float:
    """BPHS Ch.27 v.5: Kendra=60, Panapara(succedent)=30, Apoklima(cadent)=15 Virupas."""
    if house in KENDRA_HOUSES:
        return 60.0
    if house in PANAPARA_HOUSES:
        return 30.0
    return 15.0


def drekkana_bala(planet: str, d1_chart: dict[str, Any]) -> float:
    """BPHS Ch.27 v.6: 15 Virupas if the planet's own gender matches its
    Drekkana (1st=male, 2nd=female, 3rd=hermaphrodite/neutral)."""
    d3 = compute_varga(d1_chart, 3)
    d1_sign, d3_sign = d1_chart[planet]["sign"], d3["planets"][planet]["sign"]
    drekkana_index = ((d3_sign - d1_sign) % 12) // 4  # 0, 1, or 2 -- which third of the sign
    gender = "male" if planet in _MALE_PLANETS else ("female" if planet in _FEMALE_PLANETS else "neutral")
    required_index = {"male": 0, "female": 1, "neutral": 2}[gender]
    return 15.0 if drekkana_index == required_index else 0.0


def sthana_bala(planet: str, d1_chart: dict[str, Any]) -> dict[str, Any]:
    uchcha = uchcha_bala(planet, d1_chart[planet]["longitude"])
    sapta = saptavargaja_bala(planet, d1_chart)
    ojha = ojhayugma_bala(planet, d1_chart)
    kendra = kendradi_bala(d1_chart[planet]["house"])
    drekkana = drekkana_bala(planet, d1_chart)
    total_virupas = uchcha + sapta["total"] + ojha + kendra + drekkana
    return {
        "uchcha_bala": uchcha, "saptavargaja_bala": sapta["total"], "saptavargaja_breakdown": sapta["breakdown"],
        "ojhayugma_bala": ojha, "kendradi_bala": kendra, "drekkana_bala": drekkana,
        "total_virupas": round(total_virupas, 4), "total_rupas": round(total_virupas / 60, 4),
        "citation": "BPHS Ch.27 v.1-6",
    }


# ── Dig Bala (directional strength) ─────────────────────────────────────
# BPHS Ch.27 v.7-9: Sun/Mars strongest at 10th (MC), Jupiter/Mercury at
# 1st (Asc), Venus/Moon at 4th (IC), Saturn at 7th (Desc) -- the ZERO
# point is always the house exactly OPPOSITE that ideal house.
_DIG_BALA_ZERO_HOUSE = {"Sun": 4, "Mars": 4, "Jupiter": 7, "Mercury": 7, "Venus": 10, "Moon": 10, "Saturn": 1}


def dig_bala(planet: str, d1_chart: dict[str, Any], lagna_sign: int) -> float:
    zero_house = _DIG_BALA_ZERO_HOUSE[planet]
    zero_point_longitude = (house_to_sign(lagna_sign, zero_house) - 1) * 30.0
    diff = abs(d1_chart[planet]["longitude"] - zero_point_longitude) % 360
    if diff > 180:
        diff = 360 - diff
    return round(diff / 3, 4)


# ── Naisargika Bala (natural strength) -- BPHS Ch.27 v.14, fixed table ──
NAISARGIKA_BALA_RUPAS = {"Sun": 1.000, "Moon": 0.857, "Mars": 0.286, "Mercury": 0.429, "Jupiter": 0.571, "Venus": 0.714, "Saturn": 0.143}


# ── Kala Bala (temporal strength) -- sub-components ─────────────────────
def nathonnata_bala(birth_jd_ut: float, lat: float, lon: float) -> dict[str, float]:
    """BPHS Ch.27 v.8-9 (sloka numbering continues across editions --
    Nathonnata is item 1 of Kala Bala). Uses this session's new
    app.astro.sunrise day/night engine for the sunrise/sunset-anchored
    'Unnata'/'Nata' arc, per BPHS's own sunrise-to-sunrise day
    convention -- NOT clock midnight, which would silently misdate the
    day/night arc for any birth before local sunrise."""
    ctx = day_night_context(birth_jd_ut, lat, lon)
    # Unnata = how far birth has progressed into its own day/night arc,
    # in ghatis (1 ghati = 24 minutes = 1/60 of a full day; a half-day
    # arc is scaled to a nominal 30-ghati half-day for this classical
    # ratio, per BPHS's own "deduct Unnata from 30 ghatis" wording).
    unnata_ghatis = ctx["segment_fraction_elapsed"] * 30.0
    nata_ghatis = 30.0 - unnata_ghatis
    moon_group_bala = min(60.0, nata_ghatis * 2.0)  # Moon, Mars, Saturn
    sun_group_bala = 60.0 - moon_group_bala  # Sun, Jupiter, Venus
    return {
        "Sun": sun_group_bala, "Jupiter": sun_group_bala, "Venus": sun_group_bala,
        "Moon": moon_group_bala, "Mars": moon_group_bala, "Saturn": moon_group_bala,
        "Mercury": 60.0,  # always full, day or night, per BPHS's own explicit exception
    }


def paksha_bala(sun_longitude: float, moon_longitude: float) -> dict[str, float]:
    """BPHS Ch.27 v.10-11: benefics get (Moon - Sun) folded to <=180 / 3;
    malefics get 60 minus that. Mercury is treated as a malefic here if
    conjunct one (a documented per-verse exception not modeled --
    Mercury is always scored as benefic-group below, the majority
    convention when not conjunct a malefic)."""
    diff = (moon_longitude - sun_longitude) % 360
    if diff > 180:
        diff = 360 - diff
    benefic_bala = round(diff / 3, 4)
    malefic_bala = round(60.0 - benefic_bala, 4)
    return {
        "Moon": benefic_bala, "Mercury": benefic_bala, "Jupiter": benefic_bala, "Venus": benefic_bala,
        "Sun": malefic_bala, "Mars": malefic_bala, "Saturn": malefic_bala,
    }


_TRIBHAGA_DAY = ["Mercury", "Sun", "Saturn"]
_TRIBHAGA_NIGHT = ["Moon", "Venus", "Mars"]


def tribhaga_bala(birth_jd_ut: float, lat: float, lon: float) -> dict[str, float]:
    """BPHS Ch.27 v.12: day (or night) is split into 3 equal parts; one
    specific planet gets a full 60 Virupas depending on which third birth
    falls in, and Jupiter ALWAYS gets 60 regardless. Every other planet
    gets 0."""
    ctx = day_night_context(birth_jd_ut, lat, lon)
    sequence = _TRIBHAGA_DAY if ctx["is_day_birth"] else _TRIBHAGA_NIGHT
    third = min(2, int(ctx["segment_fraction_elapsed"] * 3))
    winner = sequence[third]
    return {p: (60.0 if p in (winner, "Jupiter") else 0.0) for p in CLASSICAL_7}


_WEEKDAY_LORDS = ["Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Sun"]  # Python weekday(): Mon=0..Sun=6


def dina_bala(birth_jd_ut: float, lat: float, lon: float) -> dict[str, Any]:
    """BPHS Ch.27 v.13: 45 Virupas to the lord of the weekday, sunrise-to-
    sunrise (not clock midnight -- a birth before local sunrise belongs
    to the PREVIOUS civil weekday's ruler)."""
    from datetime import timedelta

    import swisseph as swe

    ctx = day_night_context(birth_jd_ut, lat, lon)
    y, m, d, _h = swe.revjul(ctx["sunrise_jd_ut"])
    from datetime import date as _date
    weekday_index = _date(int(y), int(m), int(d)).weekday()
    lord = _WEEKDAY_LORDS[weekday_index]
    return {"lord": lord, "scores": {p: (45.0 if p == lord else 0.0) for p in CLASSICAL_7}}


def hora_bala(birth_jd_ut: float, lat: float, lon: float) -> dict[str, Any]:
    """BPHS Ch.27 v.13: 60 Virupas to the lord of the planetary hour
    (Hora) at birth -- Chaldean order, first Hora of the sunrise-to-
    sunrise day ruled by that day's own weekday lord."""
    ctx = day_night_context(birth_jd_ut, lat, lon)
    weekday_lord = dina_bala(birth_jd_ut, lat, lon)["lord"]
    chaldean_order = ["Saturn", "Jupiter", "Mars", "Sun", "Venus", "Mercury", "Moon"]
    start_idx = chaldean_order.index(weekday_lord)
    # 24 Horas per full sunrise-to-sunrise day: 12 in the day segment, 12
    # in the night segment, each proportional to that segment's own
    # actual duration (classical Horas are NOT fixed 60-minute hours).
    if ctx["is_day_birth"]:
        hora_index_in_segment = min(11, int(ctx["segment_fraction_elapsed"] * 12))
    else:
        hora_index_in_segment = 12 + min(11, int(ctx["segment_fraction_elapsed"] * 12))
    lord = chaldean_order[(start_idx + hora_index_in_segment) % 7]
    return {"lord": lord, "scores": {p: (60.0 if p == lord else 0.0) for p in CLASSICAL_7}}


def _planet_declinations(jd_ut: float) -> dict[str, float]:
    """True geocentric declination (Kranti) for the 7 classical planets --
    needed by ayana_bala(). A small, self-contained equatorial-coordinate
    call (swe.FLG_EQUATORIAL), kept local to this module since Ayana Bala
    is its only consumer."""
    import swisseph as swe

    se_ids = {
        "Sun": swe.SUN, "Moon": swe.MOON, "Mars": swe.MARS, "Mercury": swe.MERCURY,
        "Jupiter": swe.JUPITER, "Venus": swe.VENUS, "Saturn": swe.SATURN,
    }
    flags = swe.FLG_SWIEPH | swe.FLG_EQUATORIAL
    return {name: swe.calc_ut(jd_ut, se_id, flags)[0][1] for name, se_id in se_ids.items()}


def ayana_bala(planet: str, declination_deg: float) -> float:
    """BPHS Ch.27 v.15-17: (23.45 +/- Kranti/declination) x 1.2793 Virupas.
    Sign convention: Moon/Saturn take + for SOUTHERN declination; Sun/
    Mars/Jupiter/Venus take + for NORTHERN declination; Mercury is
    always +. The Sun's own result is doubled (per the text's explicit
    note)."""
    obliquity = 23.45
    if planet == "Mercury":
        signed_kranti = abs(declination_deg)
    elif planet in ("Moon", "Saturn"):
        signed_kranti = -declination_deg
    else:  # Sun, Mars, Jupiter, Venus
        signed_kranti = declination_deg
    virupas = (obliquity + signed_kranti) * 1.2793
    virupas = max(0.0, min(60.0, virupas))
    if planet == "Sun":
        virupas = min(60.0, virupas * 2.0)
    return round(virupas, 4)


def yuddha_bala_adjustment(shadbala_totals: dict[str, float], graha_yuddha_evidence: dict[str, Any] | None) -> dict[str, float]:
    """BPHS Ch.27 v.20: in planetary war (Graha Yuddha), the difference
    between the two combatants' Shadbala is added to the winner's and
    deducted from the loser's. Reuses app.derived.yogas's own Graha
    Yuddha detection (check_graha_yuddha's 'wars' list, winner-by-higher-
    longitude convention) rather than re-deriving war logic here. Applies
    every war present, in case a chart has more than one simultaneously."""
    adjustments = {p: 0.0 for p in shadbala_totals}
    if not graha_yuddha_evidence or not graha_yuddha_evidence.get("present"):
        return adjustments
    for war in graha_yuddha_evidence.get("wars", []):
        winner, loser = war.get("winner"), war.get("loser")
        if winner in shadbala_totals and loser in shadbala_totals:
            delta = abs(shadbala_totals[winner] - shadbala_totals[loser])
            adjustments[winner] += delta
            adjustments[loser] -= delta
    return adjustments


def full_shadbala(ctx: dict[str, Any]) -> dict[str, Any]:
    """Aggregate Shadbala for all 7 classical planets. Returns each
    computed component in Virupas plus a `computed_total_virupas` that is
    HONESTLY LABELED as a partial sum -- Chesta Bala (5 planets) and Drik
    Bala are disclosed data_gaps, not silently zeroed into the total
    without comment. See module docstring for why."""
    chart = ctx["chart"]
    lagna_sign = ctx["lagna_sign"]
    fixture = ctx["fixture"]
    location = fixture["location"]
    lat, lon = location["latitude"], location["longitude"]
    jd = ctx["jd"]
    declinations = _planet_declinations(jd)

    nathonnata = nathonnata_bala(jd, lat, lon)
    paksha = paksha_bala(chart["Sun"]["longitude"], chart["Moon"]["longitude"])
    tribhaga = tribhaga_bala(jd, lat, lon)
    dina = dina_bala(jd, lat, lon)
    hora = hora_bala(jd, lat, lon)

    graha_yuddha = ctx.get("yogas", {}).get("graha_yuddha")

    planets: dict[str, Any] = {}
    provisional_totals: dict[str, float] = {}
    for planet in CLASSICAL_7:
        sthana = sthana_bala(planet, chart)
        dig = dig_bala(planet, chart, lagna_sign)
        declination = declinations.get(planet)
        ayana = ayana_bala(planet, declination) if declination is not None else None
        kala_components = {
            "nathonnata_bala": nathonnata[planet],
            "paksha_bala": paksha[planet],
            "tribhaga_bala": tribhaga[planet],
            "varsha_bala": None, "masa_bala": None,  # disclosed data_gap
            "dina_bala": dina["scores"][planet],
            "hora_bala": hora["scores"][planet],
            "ayana_bala": ayana,
        }
        kala_total = sum(v for v in kala_components.values() if v is not None)

        if planet == "Sun":
            chesta = ayana
        elif planet == "Moon":
            chesta = paksha[planet]
        else:
            chesta = None  # disclosed data_gap -- see module docstring

        naisargika_virupas = NAISARGIKA_BALA_RUPAS[planet] * 60.0

        known_components = [sthana["total_virupas"], dig, kala_total, naisargika_virupas]
        if chesta is not None:
            known_components.append(chesta)
        provisional_totals[planet] = round(sum(known_components), 4)

        planets[planet] = {
            "sthana_bala": sthana, "dig_bala": dig,
            "kala_bala": {"components": kala_components, "total_virupas": round(kala_total, 4)},
            "chesta_bala": chesta,
            "naisargika_bala_virupas": round(naisargika_virupas, 4),
            "drik_bala": None,  # disclosed data_gap
        }

    yuddha_adjustments = yuddha_bala_adjustment(provisional_totals, graha_yuddha)

    for planet in CLASSICAL_7:
        total_virupas = provisional_totals[planet] + yuddha_adjustments[planet]
        total_rupas = round(total_virupas / 60.0, 4)
        planets[planet]["yuddha_bala_adjustment"] = yuddha_adjustments[planet]
        planets[planet]["computed_total_virupas"] = round(total_virupas, 4)
        planets[planet]["computed_total_rupas"] = total_rupas
        planets[planet]["min_required_rupas"] = MIN_REQUIRED_RUPAS[planet]
        planets[planet]["meets_minimum"] = total_rupas >= MIN_REQUIRED_RUPAS[planet]
        planets[planet]["completeness_note"] = (
            "Excludes Varsha/Masa Bala (Kala Bala) and Drik Bala (both disclosed data_gap); "
            + ("Chesta Bala also excluded (disclosed data_gap for this planet)." if planet not in ("Sun", "Moon") else "Chesta Bala included.")
        )

    return {
        "planets": planets,
        "dina_lord": dina["lord"], "hora_lord": hora["lord"],
        "citation": "BPHS Ch.27 (R. Santhanam translation, Reference books/BPHS - 1 RSanthanam.pdf), read directly per AGENTS.md AD-8",
    }
