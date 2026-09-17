"""Compute Itta Madhavi's full chart for the Validation Document + 5-Part reading.

Birth details:
  Name : Itta Madhavi
  DOB  : 9 May 1976
  TOB  : 01:00 IST
  Place: Penukonda, Andhra Pradesh
  Lat  : 14.0829 N
  Lon  : 77.5947 E
"""
from __future__ import annotations
import sys, os, json, yaml
from datetime import date

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.astro.engine import (
    julian_day, all_planets_sidereal, get_nakshatra,
    planet_state, navamsha_d9, is_combust, navamsha_sign, darakaraka,
)
from app.astro.constants import SIGNS, NAKSHATRAS, PLANET_STATES
from app.astro.dashas import (
    compute_dashas, compute_antardashas, compute_pratyantaradashas,
    current_dasha_antar,
)
from app.astro.transits import transit_assessment, transit_chart, relative_sign, sade_sati_phase
from app.derived.factors import (
    build_chart_context, house_lord, is_yoga_karaka, planet_aspects,
    arudha_pada, classical_karakas,
)
from app.derived.doshas import compute_all_doshas
from app.knowledge.interpreter import detect_yogas

with open(os.path.join(os.path.dirname(__file__), '..', 'data', 'charts', 'itta_madhavi.yaml')) as f:
    fixture = yaml.safe_load(f)

TODAY = date(2026, 8, 30)

# ── Pass 1: primary compute via shared engine (build_chart_context) ────────
ctx = build_chart_context(fixture, today=TODAY)
chart = ctx["chart"]
d9 = ctx["d9"]
lagna_sign = ctx["lagna_sign"]


def fmt_deg(d):
    deg = int(d)
    m = (d - deg) * 60
    mins = int(m)
    s = (m - mins) * 60
    return f"{deg:02d}deg{mins:02d}'{s:04.1f}\""


print(f"JD (UT): {ctx['jd']}")
print(f"Ayanamsa (Lahiri): {chart['_ayanamsa']:.6f} deg  ({fmt_deg(chart['_ayanamsa'])})")

planet_order = ["Lagna", "Sun", "Moon", "Mars", "Mercury", "Jupiter",
                "Venus", "Saturn", "Rahu", "Ketu"]

print("\n=== D1 (Rasi) Chart ===")
sun_lon = chart["Sun"]["longitude"]
for p in planet_order:
    info = chart[p]
    sign = SIGNS[info["sign"] - 1]
    nak = get_nakshatra(info["longitude"])
    state = planet_state(p, info["sign"]) if p != "Lagna" else "-"
    rstat = " (R)" if info.get("retrograde") else ""
    combust = ""
    if p not in ("Lagna", "Sun", "Rahu", "Ketu"):
        if is_combust(p, info["longitude"], sun_lon):
            diff = abs(info["longitude"] - sun_lon)
            if diff > 180:
                diff = 360 - diff
            combust = f"  * COMBUST ({diff:.2f} deg)"
    vargottama = (p != "Lagna" and p in d9["planets"] and
                  chart[p]["sign"] == d9["planets"][p]["sign"])
    vg = "  VARGOTTAMA" if vargottama else ""
    print(f"  {p:8s} : {sign['en']:12s} H{info['house']:2d}  "
          f"{fmt_deg(info['deg_in_sign']):>14s}  "
          f"{nak['nakshatra']['en']:14s} P{nak['pada']}  "
          f"lord={nak['nakshatra']['lord']:8s}  state={state}{rstat}{combust}{vg}")

print("\n=== Combustion check (independent re-derivation) ===")
for p in ["Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
    diff = abs(chart[p]["longitude"] - sun_lon)
    if diff > 180:
        diff = 360 - diff
    flag = "COMBUST" if is_combust(p, chart[p]["longitude"], sun_lon) else "-"
    print(f"  {p:8s}: dist from Sun = {diff:6.2f} deg    {flag}")

print("\n=== Retrograde eligibility check (Sun/Moon must NEVER be retrograde) ===")
for p in planet_order:
    if p in ("Lagna",):
        continue
    retro = chart[p].get("retrograde", False)
    illegal = p in ("Sun", "Moon") and retro
    print(f"  {p:8s}: retrograde={retro}  {'*** ILLEGAL ***' if illegal else 'OK'}")

print("\n=== Gandanta check (within 3d20m of water->fire junction) ===")
GANDANTA_ZONES = [
    (4, 30.0, "Cancer->Leo (Aslesha P4 -> Magha P1)"),
    (8, 30.0, "Scorpio->Sagittarius (Jyeshtha P4 -> Moola P1) -- Abhukta Moola"),
    (12, 30.0, "Pisces->Aries (Revati P4 -> Ashwini P1)"),
]
GZ_WIDTH = 10.0 / 3.0
for p in planet_order:
    info = chart[p]
    sign, deg = info["sign"], info["deg_in_sign"]
    flagged = False
    for water_sign, _, label in GANDANTA_ZONES:
        fire_sign = (water_sign % 12) + 1
        if sign == water_sign and deg >= 30.0 - GZ_WIDTH:
            print(f"  {p:8s}: {SIGNS[sign-1]['en']} {deg:.4f} deg -- IN GANDANTA ({label}), "
                  f"{30.0-deg:.4f} deg from junction")
            flagged = True
        elif sign == fire_sign and deg <= GZ_WIDTH:
            print(f"  {p:8s}: {SIGNS[sign-1]['en']} {deg:.4f} deg -- IN GANDANTA ({label}), "
                  f"{deg:.4f} deg past junction")
            flagged = True
    if not flagged:
        pass
print("  (planets not listed above are clear of all 3 gandanta zones)")

print("\n=== D9 (Navamsa) Chart ===")
print(f"D9 Lagna: {d9['lagna_sign_en']} (sign #{d9['lagna_sign']})")
print(f"Darakaraka (Jaimini): {d9['darakaraka']}")
for p in planet_order:
    if p in d9["planets"]:
        info = d9["planets"][p]
        vg = " VARGOTTAMA" if p != "Lagna" and chart[p]["sign"] == info["sign"] else ""
        print(f"  {p:8s}: {info['sign_en']:12s}  H{info['house']:2d}  state={info['state']}{vg}")

print("\n=== Jaimini Karakas (7 classical, by descending degree-in-sign) ===")
classical = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
ranked = sorted(classical, key=lambda p: chart[p]["deg_in_sign"], reverse=True)
karaka_names = ["Atmakaraka (AK)", "Amatyakaraka (AmK)", "Bhratrukaraka (BK)",
                "Matrukaraka (MK)", "Putrakaraka (PK)", "Gnatikaraka (GK)", "Darakaraka (DK)"]
for name, p in zip(karaka_names, ranked):
    print(f"  {name:22s}: {p:8s}  {fmt_deg(chart[p]['deg_in_sign'])}")

print("\n=== Neechabhanga check (any debilitated D1 planet) ===")
for p in classical:
    if planet_state(p, chart[p]["sign"]) == "debilitated":
        debil_sign = chart[p]["sign"]
        debil_sign_lord = SIGNS[debil_sign - 1]["lord"]
        exalt_sign_here = [pl for pl, ps in PLANET_STATES.items() if ps.get("exalt") == debil_sign]
        cond1 = chart[debil_sign_lord]["house"] in (1, 4, 7, 10)
        cond2 = any(chart[pl]["house"] in (1, 4, 7, 10) for pl in exalt_sign_here if pl in chart)
        cond3 = debil_sign_lord in chart and (chart[p]["house"] in planet_aspects(debil_sign_lord, chart[debil_sign_lord]["house"]))
        cond4 = chart[p]["house"] in (1, 4, 7, 10)
        d9_state = d9["planets"].get(p, {}).get("state")  # exalted/own-sign/neutral/debilitated
        cond5 = d9_state == "exalted"
        print(f"  {p} debilitated in {SIGNS[debil_sign-1]['en']}: "
              f"C1(sign-lord {debil_sign_lord} in kendra)={cond1}  "
              f"C2(exalt-lord {exalt_sign_here} in kendra)={cond2}  "
              f"C3(sign-lord aspects it)={cond3}  "
              f"C4(itself in kendra)={cond4}  "
              f"C5(exalted in D9)={cond5}  "
              f"=> {'NEECHABHANGA' if any([cond1,cond2,cond3,cond4,cond5]) else 'debilitation stands'}")
if not any(planet_state(p, chart[p]["sign"]) == "debilitated" for p in classical):
    print("  No classical planet is debilitated in D1 -- no Neechabhanga check applicable.")

print("\n=== House Lordship Matrix ===")
for h in range(1, 13):
    bsign = ((lagna_sign - 1 + h - 1) % 12) + 1
    lord = SIGNS[bsign - 1]["lord"]
    li = chart[lord]
    print(f"  H{h:2d} {SIGNS[bsign-1]['en']:12s} lord={lord:8s} -> {SIGNS[li['sign']-1]['en']:12s} H{li['house']:2d} state={planet_state(lord, li['sign'])}")

print("\n=== Yoga-karaka scan ===")
for p in classical:
    if is_yoga_karaka(lagna_sign, p):
        print(f"  {p}: YOGA-KARAKA for this Lagna")

print("\n=== Vimshottari Dashas (full MD list) ===")
dashas = ctx["dashas"]
for d in dashas:
    print(f"  {d['planet']:8s} : {d['start']} -> {d['end']}  ({d['years']} yrs)")

cur = ctx["current_dasha"]
print(f"\nAnalysis date: {TODAY}")
print(f"  Current MD: {cur['mahadasha']['planet']} ({cur['mahadasha']['start']} -> {cur['mahadasha']['end']})")
print(f"  Current AD: {cur['antardasha']['planet']} ({cur['antardasha']['start']} -> {cur['antardasha']['end']})")
print(f"  Current PD: {cur['pratyantardasha']['planet']} ({cur['pratyantardasha']['start']} -> {cur['pratyantardasha']['end']})")

print(f"\n  All ADs of {cur['mahadasha']['planet']} MD:")
for a in cur['all_antars']:
    print(f"    {a['planet']:8s}: {a['start']} -> {a['end']}  ({a['years']} yrs)")

print("\n=== Sade Sati / Transit Assessment (today) ===")
ta = ctx["transits"]
print(json.dumps({
    "saturn_transit_sign": ta["saturn_assessment"]["transit_sign"],
    "saturn_rel_moon": ta["references"]["from_moon"]["Saturn"],
    "sade_sati": ta["saturn_assessment"]["sade_sati"],
    "jupiter_transit_sign": ta["jupiter_assessment"]["transit_sign"],
    "jupiter_quality": ta["jupiter_assessment"]["quality"],
}, indent=2))

# Historical Sade Sati windows (Moon sign fixed; find approx years Saturn transits 12th/1st/2nd from Moon)
print("\n  Historical/future Sade Sati windows (yearly Jan-1 scan, birth year to age 75):")
moon_sign = chart["Moon"]["sign"]
prev_phase = None
for yr in range(1976, 1976 + 76):
    tc = transit_chart(date(yr, 1, 1))
    phase = sade_sati_phase(moon_sign, tc["Saturn"]["sign"])
    if phase["active"] and phase["phase"] != (prev_phase.get("phase") if prev_phase else None):
        print(f"    ~{yr}: entering {phase['label']} (Saturn in {tc['Saturn']['sign_en']})")
    prev_phase = phase

print("\n=== Doshas (compute_all_doshas) ===")
doshas = compute_all_doshas(ctx)
print(json.dumps(doshas, indent=2, default=str))

print("\n=== Yogas (detect_yogas) ===")
yogas = detect_yogas(chart)
for y in yogas:
    print(f"  {y['name']} ({y.get('strength')}): {y['effect']}")

print("\n=== Arudha Padas (AL, A10, UL + all 12) ===")
for h in [1, 10, 12]:
    ap = arudha_pada(lagna_sign, chart, h)
    label = {1: "AL (Lagna Arudha)", 10: "A10 (Karma Arudha)", 12: "UL (Upapada, canonical arudha formula)"}[h]
    print(f"  {label}: H{h} ({ap['source_sign_en']}) lord={ap['lord']} -> Arudha = {ap['pada_sign_en']}")
print("  Upapada legacy/project-guide formula comparison:")
print(f"    canonical={ctx['upapada']['canonical']['pada_sign_en']}  project_guides={ctx['upapada']['project_guides']['pada_sign_en']}  matches={ctx['upapada']['matches']}")
print("  All 12 Arudhas:")
for h in range(1, 13):
    ap = arudha_pada(lagna_sign, chart, h)
    print(f"    A{h:2d} (from {ap['source_sign_en']:12s} lord {ap['lord']:8s}): {ap['pada_sign_en']}")

print("\n=== Panchanga (Tithi/Vara/Nakshatra/Yoga/Karana) ===")
moon_lon = chart["Moon"]["longitude"]
tithi_num_raw = ((moon_lon - sun_lon) % 360) / 12.0
tithi_index = int(tithi_num_raw)  # 0-29
paksha = "Shukla" if tithi_index < 15 else "Krishna"
tithi_in_paksha = (tithi_index % 15) + 1
TITHI_NAMES = ["Prathama","Dwitiya","Tritiya","Chaturthi","Panchami","Shashti","Saptami",
               "Ashtami","Navami","Dashami","Ekadashi","Dwadashi","Trayodashi","Chaturdashi",
               "Purnima/Amavasya"]
tithi_name = TITHI_NAMES[tithi_in_paksha - 1]
weekday = date(1976, 5, 9).strftime("%A")
moon_nak = get_nakshatra(moon_lon)
yoga_num_raw = ((sun_lon + moon_lon) % 360) / (360.0/27.0)
YOGA_NAMES = ["Vishkambha","Priti","Ayushman","Saubhagya","Shobhana","Atiganda","Sukarma",
              "Dhriti","Shoola","Ganda","Vriddhi","Dhruva","Vyaghata","Harshana","Vajra",
              "Siddhi","Vyatipata","Variyana","Parigha","Shiva","Siddha","Sadhya","Shubha",
              "Shukla","Brahma","Indra","Vaidhriti"]
yoga_name = YOGA_NAMES[int(yoga_num_raw) % 27]
karana_num = int(tithi_num_raw * 2)  # each tithi = 2 karanas
print(f"  Tithi: {paksha} Paksha, {tithi_name} (tithi #{tithi_index+1} overall, {tithi_num_raw:.4f} elapsed)")
print(f"  Vara (weekday): {weekday}")
print(f"  Nakshatra (Moon): {moon_nak['nakshatra']['en']} pada {moon_nak['pada']}")
print(f"  Yoga: {yoga_name}")
print(f"  Karana index (half-tithi #{karana_num}) -- Moon-Sun elongation {((moon_lon-sun_lon)%360):.4f} deg")

print("\n=== Chart Signature (element/modality/dominant) ===")
elements = {}
modalities = {}
for p in classical + ["Rahu", "Ketu"]:
    s = chart[p]["sign"]
    el = SIGNS[s-1]["element"]
    md = SIGNS[s-1]["quality"]
    elements[el] = elements.get(el, 0) + 1
    modalities[md] = modalities.get(md, 0) + 1
print(f"  Elements: {elements}")
print(f"  Modalities: {modalities}")

print("\n=== Cross-check summary (Pass 2 sanity) ===")
print(f"  Lagna sign matches H1 sign: {chart['Lagna']['sign'] == ((lagna_sign-1+0)%12)+1}")
print(f"  Moon nakshatra lord == Dasha starting lord: {moon_nak['nakshatra']['lord']} == {dashas[0]['planet']} -> {moon_nak['nakshatra']['lord'] == dashas[0]['planet']}")
print(f"  Ketu = Rahu+180: Rahu={chart['Rahu']['longitude']}  Ketu={chart['Ketu']['longitude']}  diff={abs((chart['Ketu']['longitude']-chart['Rahu']['longitude'])%360-180)<0.001}")
print(f"  Today {TODAY} within current MD bracket: {cur['mahadasha']['start']} <= {TODAY} <= {cur['mahadasha']['end']} -> {cur['mahadasha']['start'] <= TODAY.isoformat() <= cur['mahadasha']['end']}")
