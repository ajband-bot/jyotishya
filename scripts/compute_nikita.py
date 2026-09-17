"""Compute Itta Sai Nikita's full chart for the 5-part Jyotish forecast.

Birth details:
  Name: Itta Sai Nikita
  DOB : 20 December 1997
  TOB : 12:15 IST (noon)
  Place: Kadiri, Andhra Pradesh
  Lat : 14.12 N
  Lon : 78.16 E
"""
from __future__ import annotations
import sys, os, json
from datetime import date

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.astro.engine import (
    julian_day, all_planets_sidereal, get_nakshatra,
    planet_state, navamsha_d9, is_combust, navamsha_sign,
)
from app.astro.constants import SIGNS, NAKSHATRAS, PLANET_STATES
from app.astro.dashas import (
    compute_dashas, compute_antardashas, compute_pratyantaradashas,
    current_dasha_antar,
)

# Birth Data
YEAR, MONTH, DAY = 1997, 12, 20
HOUR_LOCAL = 12 + 15/60.0     # 12:15 IST (decimal hours)
UTC_OFFSET = 5.5
LAT = 14.12
LON = 78.16

JD = julian_day(YEAR, MONTH, DAY, HOUR_LOCAL, UTC_OFFSET)
print(f"JD (UT): {JD}")

chart = all_planets_sidereal(JD, LAT, LON)


def fmt_deg(d):
    deg = int(d)
    m = (d - deg) * 60
    mins = int(m)
    s = (m - mins) * 60
    return f"{deg:02d}deg{mins:02d}'{s:04.1f}\""


print("\n=== D1 (Rasi) Chart ===")
print(f"Ayanamsa (Lahiri): {chart['_ayanamsa']:.6f} deg  ({fmt_deg(chart['_ayanamsa'])})")

planet_order = ["Lagna", "Sun", "Moon", "Mars", "Mercury", "Jupiter",
                "Venus", "Saturn", "Rahu", "Ketu"]

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
    print(f"  {p:8s} : {sign['en']:12s} H{info['house']:2d}  "
          f"{fmt_deg(info['deg_in_sign']):>14s}  "
          f"{nak['nakshatra']['en']:14s} P{nak['pada']}  "
          f"lord={nak['nakshatra']['lord']:8s}  state={state}{rstat}{combust}")

print("\n=== Combustion check ===")
for p in ["Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
    diff = abs(chart[p]["longitude"] - sun_lon)
    if diff > 180:
        diff = 360 - diff
    flag = "COMBUST" if is_combust(p, chart[p]["longitude"], sun_lon) else "-"
    print(f"  {p:8s}: dist from Sun = {diff:6.2f} deg    {flag}")

print("\n=== D9 (Navamsa) Chart ===")
d9 = navamsha_d9(chart)
print(f"D9 Lagna: {d9['lagna_sign_en']} (sign #{d9['lagna_sign']})")
print(f"Darakaraka (Jaimini): {d9['darakaraka']}  -> D9 sign {d9['dk_d9_sign_en']} ({d9['dk_d9_state']}) in H{d9['dk_d9_house']}")
for p in planet_order:
    if p in d9["planets"]:
        info = d9["planets"][p]
        print(f"  {p:8s}: {info['sign_en']:12s}  H{info['house']:2d}  state={info['state']}")


def d2_scheme(sign, portion):
    odd = sign % 2 == 1
    if odd:
        return 5 if portion == 1 else 4
    else:
        return 4 if portion == 1 else 5


def d3_scheme(sign, portion):
    offsets = {1: 0, 2: 4, 3: 8}
    return ((sign - 1 + offsets[portion]) % 12) + 1


def d4_scheme(sign, portion):
    offsets = {1: 0, 2: 3, 3: 6, 4: 9}
    return ((sign - 1 + offsets[portion]) % 12) + 1


def d7_scheme(sign, portion):
    odd = sign % 2 == 1
    base = sign - 1 if odd else (sign + 5) % 12
    return ((base + portion - 1) % 12) + 1


def d10_scheme(sign, portion):
    odd = sign % 2 == 1
    base = sign - 1 if odd else (sign + 7) % 12
    return ((base + portion - 1) % 12) + 1


def d12_scheme(sign, portion):
    return ((sign - 1 + portion - 1) % 12) + 1


def d16_scheme(sign, portion):
    movable = [1, 4, 7, 10]
    fixed = [2, 5, 8, 11]
    if sign in movable:
        base = 0
    elif sign in fixed:
        base = 4
    else:
        base = 8
    return ((base + portion - 1) % 12) + 1


def d20_scheme(sign, portion):
    movable = [1, 4, 7, 10]
    fixed = [2, 5, 8, 11]
    if sign in movable:
        base = 0
    elif sign in fixed:
        base = 8
    else:
        base = 4
    return ((base + portion - 1) % 12) + 1


def d24_scheme(sign, portion):
    odd = sign % 2 == 1
    base = 4 if odd else 3
    return ((base + portion - 1) % 12) + 1


def d27_scheme(sign, portion):
    sign_info = SIGNS[sign - 1]
    el = sign_info["element"]
    base_map = {"Fire": 0, "Earth": 9, "Air": 6, "Water": 3}
    return ((base_map[el] + portion - 1) % 12) + 1


def d30_special(sign, deg_in_sign):
    odd = sign % 2 == 1
    if odd:
        if deg_in_sign < 5:
            return 1, "Mars"
        elif deg_in_sign < 10:
            return 11, "Saturn"
        elif deg_in_sign < 18:
            return 9, "Jupiter"
        elif deg_in_sign < 25:
            return 3, "Mercury"
        else:
            return 7, "Venus"
    else:
        if deg_in_sign < 5:
            return 2, "Venus"
        elif deg_in_sign < 12:
            return 6, "Mercury"
        elif deg_in_sign < 20:
            return 12, "Jupiter"
        elif deg_in_sign < 25:
            return 10, "Saturn"
        else:
            return 8, "Mars"


def d40_scheme(sign, portion):
    odd = sign % 2 == 1
    base = 0 if odd else 6
    return ((base + portion - 1) % 12) + 1


def d45_scheme(sign, portion):
    movable = [1, 4, 7, 10]
    fixed = [2, 5, 8, 11]
    if sign in movable:
        base = 0
    elif sign in fixed:
        base = 4
    else:
        base = 8
    return ((base + portion - 1) % 12) + 1


def d60_scheme(sign, deg_in_sign):
    portion = int(deg_in_sign / 0.5) + 1
    return ((sign - 1 + portion) % 12) + 1, portion


print("\n=== Vargas Computation ===")
divisional = [
    ("D2", 2, d2_scheme),
    ("D3", 3, d3_scheme),
    ("D4", 4, d4_scheme),
    ("D7", 7, d7_scheme),
    ("D10", 10, d10_scheme),
    ("D12", 12, d12_scheme),
    ("D16", 16, d16_scheme),
    ("D20", 20, d20_scheme),
    ("D24", 24, d24_scheme),
    ("D27", 27, d27_scheme),
    ("D40", 40, d40_scheme),
    ("D45", 45, d45_scheme),
]

vargas = {}
for vname, divisor, scheme in divisional:
    print(f"\n--- {vname} ---")
    vargas[vname] = {}
    for p in planet_order:
        info = chart[p]
        sign = info["sign"]
        deg = info["deg_in_sign"]
        portion_size = 30.0 / divisor
        portion = int(deg / portion_size) + 1
        v_sign = scheme(sign, portion)
        state = planet_state(p, v_sign) if p != "Lagna" else "-"
        vargas[vname][p] = {"sign": v_sign, "sign_en": SIGNS[v_sign - 1]["en"], "state": state, "portion": portion}
        print(f"  {p:8s}: portion={portion:2d}  -> {SIGNS[v_sign - 1]['en']:12s}  state={state}")

print("\n--- D30 (Trimsamsha) ---")
vargas["D30"] = {}
for p in planet_order:
    info = chart[p]
    s, lord = d30_special(info["sign"], info["deg_in_sign"])
    state = planet_state(p, s) if p != "Lagna" else "-"
    vargas["D30"][p] = {"sign": s, "sign_en": SIGNS[s - 1]["en"], "state": state, "lord": lord}
    print(f"  {p:8s}: D30-lord={lord:8s}  -> {SIGNS[s - 1]['en']:12s}  state={state}")

print("\n--- D60 (Shashtiamsha) ---")
vargas["D60"] = {}
for p in planet_order:
    info = chart[p]
    s, portion = d60_scheme(info["sign"], info["deg_in_sign"])
    state = planet_state(p, s) if p != "Lagna" else "-"
    vargas["D60"][p] = {"sign": s, "sign_en": SIGNS[s - 1]["en"], "state": state, "portion": portion}
    print(f"  {p:8s}: portion={portion:2d}  -> {SIGNS[s - 1]['en']:12s}  state={state}")

print("\n=== Vimshottari Dashas ===")
moon_lon = chart["Moon"]["longitude"]
birth_dt = date(YEAR, MONTH, DAY)
dashas = compute_dashas(birth_dt, moon_lon, years=120)
for d in dashas:
    print(f"  {d['planet']:8s} : {d['start']} -> {d['end']}  ({d['years']} yrs)")

today = date(2026, 8, 15)
print(f"\nAnalysis date: {today}")
cur = current_dasha_antar(dashas, today)
print(f"  Current MD: {cur['mahadasha']['planet']} ({cur['mahadasha']['start']} -> {cur['mahadasha']['end']})")
print(f"  Current AD: {cur['antardasha']['planet']} ({cur['antardasha']['start']} -> {cur['antardasha']['end']})")
print(f"  Current PD: {cur['pratyantardasha']['planet']} ({cur['pratyantardasha']['start']} -> {cur['pratyantardasha']['end']})")

print(f"\n  All ADs of {cur['mahadasha']['planet']} MD:")
for a in cur['all_antars']:
    print(f"    {a['planet']:8s}: {a['start']} -> {a['end']}  ({a['years']} yrs)")

print(f"\n  All PDs of {cur['antardasha']['planet']} AD:")
for p in cur['all_pratyantaras']:
    print(f"    {p['planet']:8s}: {p['start']} -> {p['end']}  ({p['years']} yrs)")

print("\n=== Arudha Padas ===")


def arudha(bhava_sign, lord_sign):
    n = ((lord_sign - bhava_sign) % 12) + 1
    arudha_sign = ((lord_sign - 1 + n - 1) % 12) + 1
    if arudha_sign == bhava_sign or arudha_sign == ((bhava_sign - 1 + 6) % 12) + 1:
        arudha_sign = ((arudha_sign - 1 + 9) % 12) + 1
    return arudha_sign


lagna_sign = chart["Lagna"]["sign"]
sign_lord_planet = lambda s: SIGNS[s - 1]["lord"]
for bhava_idx in range(12):
    bsign = ((lagna_sign - 1 + bhava_idx) % 12) + 1
    lord = sign_lord_planet(bsign)
    if lord == "Rahu":
        lord = "Saturn"
    if lord == "Ketu":
        lord = "Mars"
    lord_sign = chart[lord]["sign"]
    a_sign = arudha(bsign, lord_sign)
    print(f"  Bhava {bhava_idx + 1:2d} ({SIGNS[bsign - 1]['en']:12s}, lord {lord:8s} in {SIGNS[lord_sign - 1]['en']:12s}): A{bhava_idx + 1} = {SIGNS[a_sign - 1]['en']}")
