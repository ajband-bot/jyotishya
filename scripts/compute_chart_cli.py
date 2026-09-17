"""Jyotisha — Generic CLI Chart Compute Script.

Outputs a complete Vedic chart as JSON to stdout.
Used by Wibey commands and the MCP server.

Usage:
    python scripts/compute_chart_cli.py \
        --name "Karthik Agasthya" \
        --dob "1986-12-29" \
        --tob "23:45" \
        --utc 5.5 \
        --lat 12.9629 \
        --lon 77.5775

Output: JSON with keys: meta, d1, d9, dashas, current_dasha, yogas, aspects, house_lords
"""
from __future__ import annotations
import argparse, json, sys, os
from datetime import date

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.astro.engine import (
    julian_day, all_planets_sidereal, navamsha_d9,
    get_nakshatra, planet_state, is_combust, darakaraka,
)
from app.astro.constants import SIGNS, NAKSHATRAS
from app.astro.dashas import (
    compute_dashas, compute_antardashas,
    compute_pratyantaradashas, current_dasha_antar,
)


def fmt_deg(d: float) -> str:
    deg = int(d)
    m = (d - deg) * 60
    mins = int(m)
    s = (m - mins) * 60
    return f"{deg:02d}°{mins:02d}'{s:04.1f}\""


def aspect_houses(planet: str) -> list[int]:
    if planet == "Mars":    return [4, 7, 8]
    if planet == "Jupiter": return [5, 7, 9]
    if planet == "Saturn":  return [3, 7, 10]
    if planet in ("Rahu", "Ketu"): return [5, 7, 9]
    return [7]


def compute_full_chart(name: str, dob: str, tob: str, utc_offset: float,
                       lat: float, lon: float) -> dict:
    """Compute a full Vedic chart and return structured dict."""
    yr, mo, dy = map(int, dob.split("-"))
    hh, mm    = map(int, tob.split(":"))
    hour_dec  = hh + mm / 60.0
    birth_dt  = date(yr, mo, dy)

    jd    = julian_day(yr, mo, dy, hour_dec, utc_offset)
    chart = all_planets_sidereal(jd, lat, lon)
    d9    = navamsha_d9(chart)

    # ── Dashas ────────────────────────────────────────────────────────────────
    moon_lon = chart["Moon"]["longitude"]
    dashas   = compute_dashas(birth_dt, moon_lon, years=120)
    cur      = current_dasha_antar(dashas)

    # ── D1 enriched planets ───────────────────────────────────────────────────
    sun_lon = chart["Sun"]["longitude"]
    planet_order = ["Lagna","Sun","Moon","Mars","Mercury",
                    "Jupiter","Venus","Saturn","Rahu","Ketu"]

    d1_planets = {}
    for p in planet_order:
        info   = chart[p]
        sign   = SIGNS[info["sign"] - 1]
        nak    = get_nakshatra(info["longitude"])
        state  = planet_state(p, info["sign"]) if p != "Lagna" else "—"
        retro  = info.get("retrograde", False)
        comb   = False
        comb_deg = None
        if p not in ("Lagna", "Sun", "Rahu", "Ketu"):
            diff = abs(info["longitude"] - sun_lon)
            if diff > 180: diff = 360 - diff
            comb = is_combust(p, info["longitude"], sun_lon)
            comb_deg = round(diff, 2)
        d1_planets[p] = {
            "sign":       sign["en"],
            "sign_no":    info["sign"],
            "house":      info["house"],
            "longitude":  round(info["longitude"], 4),
            "deg_in_sign": fmt_deg(info["deg_in_sign"]),
            "nakshatra":  nak["nakshatra"]["en"],
            "nakshatra_sa": nak["nakshatra"].get("sa", ""),
            "pada":       nak["pada"],
            "nak_lord":   nak["nakshatra"]["lord"],
            "state":      state,
            "retrograde": retro,
            "combust":    comb,
            "combust_deg": comb_deg,
        }

    # ── D9 enriched ───────────────────────────────────────────────────────────
    d9_planets = {}
    for p in planet_order:
        if p in d9.get("planets", {}):
            info = d9["planets"][p]
            d9_planets[p] = {
                "sign":    info.get("sign_en", ""),
                "sign_no": info.get("sign", 0),
                "house":   info.get("house", 0),
                "state":   info.get("state", ""),
            }
    vargottama = [
        p for p in planet_order
        if p != "Lagna" and
           chart.get(p, {}).get("sign") == d9.get("planets", {}).get(p, {}).get("sign")
    ]

    # ── House lords ───────────────────────────────────────────────────────────
    lagna_sign = chart["Lagna"]["sign"]
    house_lords = {}
    for h in range(1, 13):
        bsign = ((lagna_sign - 1 + h - 1) % 12) + 1
        lord  = SIGNS[bsign - 1]["lord"]
        if lord in chart:
            li = chart[lord]
            house_lords[f"H{h}"] = {
                "sign":  SIGNS[bsign - 1]["en"],
                "lord":  lord,
                "lord_house": li["house"],
                "lord_sign":  SIGNS[li["sign"] - 1]["en"],
                "lord_state": planet_state(lord, li["sign"]),
            }

    # ── Special aspects ───────────────────────────────────────────────────────
    aspects = {}
    for p in planet_order:
        if p == "Lagna": continue
        info = chart[p]
        targets = []
        for n in aspect_houses(p):
            th = ((info["house"] - 1 + n - 1) % 12) + 1
            ts = ((info["sign"] - 1 + n - 1) % 12) + 1
            targets.append({"house": th, "sign": SIGNS[ts - 1]["en"]})
        aspects[p] = {"from_house": info["house"], "aspects": targets}

    # ── Yoga checks ───────────────────────────────────────────────────────────
    yogas = {}
    moon_h = chart["Moon"]["house"]
    jup_h  = chart["Jupiter"]["house"]
    yogas["gajakesari"]    = (jup_h - moon_h) % 12 in (0, 3, 6, 9)
    yogas["budha_aditya"]  = chart["Sun"]["sign"] == chart["Mercury"]["sign"]
    yogas["chandra_mangala"] = chart["Moon"]["sign"] == chart["Mars"]["sign"]
    kendras = {1, 4, 7, 10}
    pmp = {"Mars":"Ruchaka","Mercury":"Bhadra","Jupiter":"Hamsa","Venus":"Malavya","Saturn":"Shasha"}
    for p, yname in pmp.items():
        st = planet_state(p, chart[p]["sign"])
        yogas[yname.lower()] = chart[p]["house"] in kendras and st in ("own-sign","exalted")
    debilitated = [p for p in ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn"]
                   if planet_state(p, chart[p]["sign"]) == "debilitated"]
    yogas["debilitated_planets"] = debilitated

    # ── Current transits ──────────────────────────────────────────────────────
    transits_note = ("Use app.astro.transits for live transit positions. "
                     "Key planets: Jupiter, Saturn, Rahu/Ketu, Mars.")

    return {
        "meta": {
            "name":       name,
            "dob":        dob,
            "tob":        tob,
            "utc_offset": utc_offset,
            "lat":        lat,
            "lon":        lon,
            "julian_day": round(jd, 6),
            "ayanamsa":   round(chart["_ayanamsa"], 6),
            "lagna":      d1_planets["Lagna"]["sign"],
            "lagna_nakshatra": d1_planets["Lagna"]["nakshatra"],
        },
        "d1": d1_planets,
        "d9": {
            "lagna":      d9.get("lagna_sign_en", ""),
            "darakaraka": d9.get("darakaraka", ""),
            "dk_d9_sign": d9.get("dk_d9_sign_en", ""),
            "vargottama": vargottama,
            "planets":    d9_planets,
        },
        "house_lords":    house_lords,
        "aspects":        aspects,
        "yogas":          yogas,
        "dashas":         dashas,
        "current_dasha":  cur,
        "transits_note":  transits_note,
    }


def _parse_args():
    p = argparse.ArgumentParser(description="Compute Vedic chart — outputs JSON")
    p.add_argument("--name",   required=True,        help="Person's full name")
    p.add_argument("--dob",    required=True,        help="Date of birth YYYY-MM-DD")
    p.add_argument("--tob",    required=True,        help="Time of birth HH:MM (local)")
    p.add_argument("--utc",    type=float, default=5.5, help="UTC offset (e.g. 5.5 for IST)")
    p.add_argument("--lat",    type=float, required=True, help="Latitude (decimal)")
    p.add_argument("--lon",    type=float, required=True, help="Longitude (decimal)")
    p.add_argument("--pretty", action="store_true",  help="Pretty-print JSON")
    return p.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    result = compute_full_chart(
        name=args.name, dob=args.dob, tob=args.tob,
        utc_offset=args.utc, lat=args.lat, lon=args.lon,
    )
    indent = 2 if args.pretty else None
    print(json.dumps(result, indent=indent, default=str))
