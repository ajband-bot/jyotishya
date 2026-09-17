"""Compute Karthik Agasthya's full chart for the 3-part Jyotish horoscope.

Birth details:
  Name : Karthik Agasthya
  DOB  : 29 December 1986 (Monday / Somavāra)
  TOB  : 23:45 IST
  Place: Bengaluru, Karnataka, India
  Lat  : 12.9629 N
  Lon  : 77.5775 E
"""
from __future__ import annotations
import sys, os
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

# ── Birth Data ────────────────────────────────────────────────────────────
YEAR, MONTH, DAY = 1986, 12, 29
HOUR_LOCAL = 23 + 45/60.0      # 23:45 IST
UTC_OFFSET = 5.5
LAT = 12.9629
LON = 77.5775

JD = julian_day(YEAR, MONTH, DAY, HOUR_LOCAL, UTC_OFFSET)
print(f"JD (UT): {JD}")

chart = all_planets_sidereal(JD, LAT, LON)


def fmt_deg(d: float) -> str:
    deg = int(d)
    m = (d - deg) * 60
    mins = int(m)
    s = (m - mins) * 60
    return f"{deg:02d}°{mins:02d}'{s:04.1f}\""


print("\n=== D1 (Rāśi) Chart ===")
print(f"Ayanāṁśa (Lahiri): {chart['_ayanamsa']:.6f}°  ({fmt_deg(chart['_ayanamsa'])})")

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
            combust = f"  ★ COMBUST ({diff:.2f}°)"
    print(f"  {p:8s} : {sign['en']:12s} H{info['house']:2d}  "
          f"{fmt_deg(info['deg_in_sign']):>14s}  lon={info['longitude']:8.4f}  "
          f"{nak['nakshatra']['en']:14s} P{nak['pada']}  "
          f"lord={nak['nakshatra']['lord']:8s}  state={state}{rstat}{combust}")

print("\n=== Combustion check ===")
for p in ["Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
    diff = abs(chart[p]["longitude"] - sun_lon)
    if diff > 180:
        diff = 360 - diff
    flag = "COMBUST" if is_combust(p, chart[p]["longitude"], sun_lon) else "-"
    print(f"  {p:8s}: dist from Sun = {diff:6.2f}°    {flag}")

print("\n=== D9 (Navāṁśa) Chart ===")
d9 = navamsha_d9(chart)
print(f"D9 Lagna: {d9['lagna_sign_en']} (sign #{d9['lagna_sign']})")
print(f"Darakaraka (Jaimini): {d9['darakaraka']}  → D9 sign {d9['dk_d9_sign_en']} ({d9['dk_d9_state']}) in H{d9['dk_d9_house']}")
for p in planet_order:
    if p in d9["planets"]:
        info = d9["planets"][p]
        print(f"  {p:8s}: {info['sign_en']:12s}  H{info['house']:2d}  state={info['state']}")

# ── Vimshottari Dashas ─────────────────────────────────────────────────────
print("\n=== Vimshottari Mahādaśās (120 yrs) ===")
moon_lon = chart["Moon"]["longitude"]
birth_dt = date(YEAR, MONTH, DAY)
dashas = compute_dashas(birth_dt, moon_lon, years=120)
for d in dashas:
    print(f"  {d['planet']:8s} : {d['start']} → {d['end']}  ({d['years']} yrs)")

# Current dasha as of today
today = date.today()
print(f"\nToday: {today}")
cur = current_dasha_antar(dashas, today)
print(f"  Current MD: {cur['mahadasha']['planet']} ({cur['mahadasha']['start']} → {cur['mahadasha']['end']})")
print(f"  Current AD: {cur['antardasha']['planet']} ({cur['antardasha']['start']} → {cur['antardasha']['end']})")
print(f"  Current PD: {cur['pratyantardasha']['planet']} ({cur['pratyantardasha']['start']} → {cur['pratyantardasha']['end']})")

print(f"\n  All ADs of current {cur['mahadasha']['planet']} MD:")
for a in cur['all_antars']:
    print(f"    {a['planet']:8s}: {a['start']} → {a['end']}  ({a['years']} yrs)")

print(f"\n  All PDs of current {cur['antardasha']['planet']} AD:")
for p in cur['all_pratyantaras']:
    print(f"    {p['planet']:8s}: {p['start']} → {p['end']}  ({p['years']} yrs)")

# ── House lord placements ──────────────────────────────────────────────────
print("\n=== House lord placements ===")
lagna_sign = chart["Lagna"]["sign"]
for h in range(1, 13):
    bsign = ((lagna_sign - 1 + h - 1) % 12) + 1
    lord = SIGNS[bsign - 1]["lord"]
    if lord in chart:
        l_info = chart[lord]
        print(f"  H{h:2d} ({SIGNS[bsign-1]['en']:12s}) lord {lord:8s} → {SIGNS[l_info['sign']-1]['en']:12s} (H{l_info['house']:2d})")

# ── Aspects (Drishti) — basic Parashari ───────────────────────────────────
print("\n=== Special Aspects (Parashari) ===")
# Mars: 4th, 7th, 8th. Jup: 5th, 7th, 9th. Sat: 3rd, 7th, 10th. All planets aspect 7th.
def aspect_houses(planet: str):
    if planet == "Mars":    return [4, 7, 8]
    if planet == "Jupiter": return [5, 7, 9]
    if planet == "Saturn":  return [3, 7, 10]
    if planet == "Rahu":    return [5, 7, 9]   # Rahu like Jupiter (debated)
    if planet == "Ketu":    return [5, 7, 9]
    return [7]

for p in ["Mars", "Jupiter", "Saturn", "Rahu", "Ketu", "Sun", "Moon", "Mercury", "Venus"]:
    info = chart[p]
    src_sign = info["sign"]
    src_house = info["house"]
    targets = []
    for n in aspect_houses(p):
        target_house = ((src_house - 1 + n - 1) % 12) + 1
        target_sign = ((src_sign - 1 + n - 1) % 12) + 1
        targets.append(f"H{target_house}({SIGNS[target_sign-1]['en']})")
    print(f"  {p:8s} from H{src_house:2d} aspects: {', '.join(targets)}")

# ── Yogas detection (basic) ───────────────────────────────────────────────
print("\n=== Yoga checks ===")
# Gajakesari: Jupiter in Kendra (1,4,7,10) from Moon
moon_house = chart["Moon"]["house"]
jup_house = chart["Jupiter"]["house"]
diff = ((jup_house - moon_house) % 12) + 1
gaja = (jup_house - moon_house) % 12 in (0, 3, 6, 9)
print(f"  Gajakesari (Jup in Kendra from Moon)? Moon H{moon_house}, Jup H{jup_house} → {'YES ✅' if gaja else 'NO'}")

# Budha-Aditya: Sun + Mercury in same sign
budha_aditya = chart["Sun"]["sign"] == chart["Mercury"]["sign"]
print(f"  Budha-Āditya (Sun+Mercury same sign)? {'YES ✅' if budha_aditya else 'NO'}")

# Pancha Mahapurusha for Mars/Mercury/Jupiter/Venus/Saturn in own/exalt + Kendra (1,4,7,10)
kendras = (1, 4, 7, 10)
pmp_map = {
    "Mars":   "Ruchaka",
    "Mercury":"Bhadra",
    "Jupiter":"Hamsa",
    "Venus":  "Malavya",
    "Saturn": "Shasha",
}
for p, name in pmp_map.items():
    info = chart[p]
    state = planet_state(p, info["sign"])
    in_kendra = info["house"] in kendras
    own_or_ex = state in ("own-sign", "exalted")
    print(f"  {name:8s} ({p}): state={state}, H{info['house']} → {'YES ✅' if (in_kendra and own_or_ex) else 'no'}")

# Chandra-Mangala: Moon and Mars together
cm = chart["Moon"]["sign"] == chart["Mars"]["sign"]
print(f"  Chandra-Maṅgala (Moon+Mars same sign)? {'YES ✅' if cm else 'NO'}")

# Neechabhanga rules (BPHS Ch.28) — quick check for any debilitated planet
print("\n  Debilitated planets:")
for p in ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn"]:
    if planet_state(p, chart[p]["sign"]) == "debilitated":
        print(f"    {p} debilitated in {SIGNS[chart[p]['sign']-1]['en']} (H{chart[p]['house']})")
