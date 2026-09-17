"""Full antardasha tree + transit computation for Itta Sai Nikita, mirroring
the Raghunandan companion script. Reuses app.astro engine only -- no new
chart derivation, just exhaustive dasha expansion and a transit snapshot."""
from __future__ import annotations
import sys, os, json
from datetime import date

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.astro.engine import julian_day, all_planets_sidereal
from app.astro.dashas import compute_dashas, compute_antardashas
from app.astro.transits import transit_assessment

YEAR, MONTH, DAY = 1997, 12, 20
HOUR_LOCAL = 12 + 15/60.0
UTC_OFFSET = 5.5
LAT, LON = 14.12, 78.16

JD = julian_day(YEAR, MONTH, DAY, HOUR_LOCAL, UTC_OFFSET)
chart = all_planets_sidereal(JD, LAT, LON)
moon_lon = chart["Moon"]["longitude"]
birth_dt = date(YEAR, MONTH, DAY)

print("=== FULL VIMSHOTTARI DASHA TREE (all MD -> all AD) ===")
dashas = compute_dashas(birth_dt, moon_lon, years=120)
for d in dashas:
    print(f"\nMD {d['planet']:8s}: {d['start']} -> {d['end']}  ({d['years']} yrs)")
    ads = compute_antardashas(d)
    for a in ads:
        print(f"    AD {a['planet']:8s}: {a['start']} -> {a['end']}")

print("\n\n=== TRANSIT ASSESSMENT (today) ===")
today = date(2026, 8, 16)
assessment = transit_assessment(chart, today)
print(json.dumps(assessment, indent=2, default=str))

print("\n=== KEY TRANSIT SNAPSHOTS (next ~5 years, yearly Jan 1) ===")
for yr in range(2026, 2031):
    d = date(yr, 1, 1)
    a = transit_assessment(chart, d)
    t = a['transits']
    print(f"{d}: Saturn={t['Saturn']['sign_en']:12s} Jupiter={t['Jupiter']['sign_en']:12s} Rahu={t['Rahu']['sign_en']:12s} Ketu={t['Ketu']['sign_en']}")
