"""Full antardasha table (all MDs) + transit assessment for Itta Raghunandan."""
from __future__ import annotations
import sys, os
from datetime import date

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.astro.engine import julian_day, all_planets_sidereal
from app.astro.dashas import compute_dashas, compute_antardashas
from app.astro.transits import transit_assessment, transit_chart, relative_sign

YEAR, MONTH, DAY = 1966, 10, 7
HOUR_LOCAL = 13 + 52/60.0
UTC_OFFSET = 5.5
LAT = 15.139167
LON = 76.921389

JD = julian_day(YEAR, MONTH, DAY, HOUR_LOCAL, UTC_OFFSET)
chart = all_planets_sidereal(JD, LAT, LON)
moon_lon = chart["Moon"]["longitude"]
birth_dt = date(YEAR, MONTH, DAY)

dashas = compute_dashas(birth_dt, moon_lon, years=120)

print("=== FULL VIMSHOTTARI DASHA TREE (all MD -> all AD) ===")
for md in dashas:
    print(f"\nMD {md['planet']} : {md['start']} -> {md['end']}  ({md['years']} yrs)")
    ads = compute_antardashas(md)
    for a in ads:
        print(f"    AD {a['planet']:8s}: {a['start']} -> {a['end']}  ({a['years']} yrs)")

print("\n\n=== TRANSIT ASSESSMENT (today) ===")
today = date(2026, 8, 16)
ta = transit_assessment(chart, today)
import json
print(json.dumps(ta, indent=2, default=str))

# Also compute Saturn/Jupiter/Rahu-Ketu sign ingress windows over next few years for narrative
print("\n=== KEY TRANSIT SNAPSHOTS (next ~3 years, yearly Jan 1) ===")
for yr in [2026, 2027, 2028, 2029, 2030]:
    d = date(yr, 1, 1)
    tc = transit_chart(d)
    moon_sign = chart["Moon"]["sign"]
    lagna_sign = chart["Lagna"]["sign"]
    sat_rel_moon = relative_sign(moon_sign, tc["Saturn"]["sign"])
    jup_rel_moon = relative_sign(moon_sign, tc["Jupiter"]["sign"])
    sat_rel_lagna = relative_sign(lagna_sign, tc["Saturn"]["sign"])
    jup_rel_lagna = relative_sign(lagna_sign, tc["Jupiter"]["sign"])
    rahu_sign = tc["Rahu"]["sign_en"]
    ketu_sign = tc["Ketu"]["sign_en"]
    print(f"{yr}-01-01: Saturn={tc['Saturn']['sign_en']:12s}(H{sat_rel_moon} fromMoon,H{sat_rel_lagna} fromLagna)  "
          f"Jupiter={tc['Jupiter']['sign_en']:12s}(H{jup_rel_moon} fromMoon,H{jup_rel_lagna} fromLagna)  "
          f"Rahu={rahu_sign:12s} Ketu={ketu_sign}")
