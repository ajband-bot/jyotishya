"""API routes — chart calculation + analysis endpoints."""
from __future__ import annotations
from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from datetime import date
from typing import Optional
import json

from app.astro.engine import julian_day, all_planets_sidereal, navamsha_d9, darakaraka
from app.astro.dashas import compute_dashas, current_dasha_antar
from app.knowledge.interpreter import full_analysis
from app.rules.evaluator import evaluate_chart_fixture
from app.astro.constants import SIGNS, SI_GRID

router = APIRouter()
templates = Jinja2Templates(directory="templates")


# ── City → Lat/Lon lookup (common Indian cities, no external dep) ──────────
CITIES = {
    "hyderabad":     (17.3850, 78.4867), "vizag":       (17.6868, 83.2185),
    "visakhapatnam": (17.6868, 83.2185), "vijayawada":  (16.5062, 80.6480),
    "tirupati":      (13.6288, 79.4192), "warangal":    (17.9784, 79.5941),
    "guntur":        (16.3067, 80.4365), "nellore":     (14.4426, 79.9865),
    "kurnool":       (15.8281, 78.0373), "rajahmundry": (17.0005, 81.8040),
    "karimnagar":    (18.4386, 79.1288), "nizamabad":   (18.6725, 78.0941),
    "kakinada":      (16.9891, 82.2475), "eluru":       (16.7107, 81.0952),
    "anantapur":     (14.6819, 77.6006), "kadapa":      (14.4674, 78.8241),
    "delhi":         (28.6139, 77.2090), "new delhi":   (28.6139, 77.2090),
    "mumbai":        (19.0760, 72.8777), "bangalore":   (12.9716, 77.5946),
    "bengaluru":     (12.9716, 77.5946), "chennai":     (13.0827, 80.2707),
    "kolkata":       (22.5726, 88.3639), "pune":        (18.5204, 73.8567),
    "ahmedabad":     (23.0225, 72.5714), "jaipur":      (26.9124, 75.7873),
    "lucknow":       (26.8467, 80.9462), "bhopal":      (23.2599, 77.4126),
    "patna":         (25.5941, 85.1376), "bhubaneswar": (20.2961, 85.8245),
    "coimbatore":    (11.0168, 76.9558), "madurai":     (9.9252,  78.1198),
    "nagpur":        (21.1458, 79.0882), "surat":       (21.1702, 72.8311),
    "kochi":         (9.9312,  76.2673), "trivandrum":  (8.5241,  76.9366),
    "chandigarh":    (30.7333, 76.7794), "mysore":      (12.2958, 76.6394),
    "mysuru":        (12.2958, 76.6394), "mangalore":   (12.9141, 74.8560),
    "indore":        (22.7196, 75.8577), "goa":         (15.2993, 74.1240),
    "panjim":        (15.4909, 73.8278), "shimla":      (31.1048, 77.1734),
}


def resolve_location(place: str, lat: Optional[float], lon: Optional[float]):
    """Return (lat, lon, display_name). Fallback to Hyderabad if unknown."""
    if lat and lon:
        return float(lat), float(lon), f"{lat:.4f}°N, {lon:.4f}°E"
    key = place.lower().strip()
    if key in CITIES:
        la, lo = CITIES[key]
        return la, lo, place.title()
    # Try partial match
    for city, coords in CITIES.items():
        if city in key or key in city:
            return coords[0], coords[1], city.title()
    # Default IST +5:30 — Hyderabad
    return 17.3850, 78.4867, f"{place} (defaulted to Hyderabad)"


def build_si_grid(chart: dict) -> list:
    """Build 4x4 South Indian grid with planets placed by sign."""
    # Invert SI_GRID: position (row,col) → sign_number
    pos_to_sign = {v: k for k, v in SI_GRID.items()}
    # Planets by sign
    planets_by_sign: dict[int, list] = {i: [] for i in range(1, 13)}
    planet_abbrev = {
        "Sun":"Su","Moon":"Mo","Mars":"Ma","Mercury":"Me",
        "Jupiter":"Ju","Venus":"Ve","Saturn":"Sa","Rahu":"Ra","Ketu":"Ke"
    }
    lagna_sign = chart["Lagna"]["sign"]
    for planet, abbr in planet_abbrev.items():
        p = chart.get(planet, {})
        if p:
            planets_by_sign[p["sign"]].append(abbr)

    grid = []
    for row in range(4):
        row_data = []
        for col in range(4):
            # corners are internal triangles in real SI chart
            if (row in [1,2]) and (col in [1,2]):
                row_data.append({"type":"center", "sign":None, "planets":[], "is_lagna":False})
                continue
            sign_no = pos_to_sign.get((row, col))
            is_lagna = (sign_no == lagna_sign)
            sign_info = SIGNS[sign_no-1] if sign_no else None
            row_data.append({
                "type": "house",
                "sign": sign_no,
                "sign_name": sign_info["name"] if sign_info else "",
                "sign_en":   sign_info["en"]   if sign_info else "",
                "planets":   planets_by_sign.get(sign_no, []),
                "is_lagna":  is_lagna,
            })
        grid.append(row_data)
    return grid


@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(request, "index.html")


@router.post("/chart", response_class=HTMLResponse)
async def compute_chart(
    request: Request,
    birth_date: str = Form(...),
    birth_time: str = Form(...),
    birth_place: str = Form(...),
    lat: Optional[str] = Form(None),
    lon: Optional[str] = Form(None),
    utc_offset: float = Form(5.5),
):
    try:
        # Parse inputs
        yr, mo, dy = map(int, birth_date.split("-"))
        hh, mm = map(int, birth_time.split(":"))
        hour_decimal = hh + mm / 60.0

        lat_f, lon_f, place_name = resolve_location(
            birth_place,
            float(lat) if lat and lat.strip() else None,
            float(lon) if lon and lon.strip() else None,
        )

        jd = julian_day(yr, mo, dy, hour_decimal, utc_offset)
        chart = all_planets_sidereal(jd, lat_f, lon_f)

        # Dashas
        moon_sid = chart["Moon"]["longitude"]
        birth_dt  = date(yr, mo, dy)
        dashas    = compute_dashas(birth_dt, moon_sid)
        dasha_now = current_dasha_antar(dashas)

        # Full analysis
        analysis = full_analysis(chart, birth_date)

        # SI Grid
        si_grid = build_si_grid(chart)

        ctx = {
            "request":    request,
            "chart":      chart,
            "si_grid":    si_grid,
            "analysis":   analysis,
            "dashas":     dashas,
            "dasha_now":  dasha_now,
            "birth_date": birth_date,
            "birth_time": birth_time,
            "place_name": place_name,
            "utc_offset": utc_offset,
            "jd":         round(jd, 4),
            "error":      None,
        }
        del ctx["request"]
        return templates.TemplateResponse(request, "chart.html", ctx)

    except Exception as exc:
        import traceback
        return templates.TemplateResponse(request, "chart.html", {
            "error": str(exc),
            "tb": traceback.format_exc(),
            "chart": None, "analysis": None,
        })


@router.get("/api/d9")
async def api_d9(
    birth_date: str, birth_time: str, birth_place: str,
    lat: Optional[float] = None, lon: Optional[float] = None,
    utc_offset: float = 5.5,
):
    """Standalone D9 Navamsha chart endpoint.

    Returns the full D9 chart including:
      - D9 lagna sign
      - All 9 planets + Lagna in D9
      - D9 dignity for each planet
      - Darakaraka (DK) identification
      - DK's D9 sign, state, and house
      - Vargottama planets (D1 == D9 sign)
    """
    yr, mo, dy = map(int, birth_date.split("-"))
    hh, mm = map(int, birth_time.split(":"))
    lat_f, lon_f, place_name = resolve_location(birth_place, lat, lon)
    jd    = julian_day(yr, mo, dy, hh + mm / 60.0, utc_offset)
    chart = all_planets_sidereal(jd, lat_f, lon_f)
    d9    = navamsha_d9(chart)

    # Vargottama: D1 sign == D9 sign
    vargottama = [
        name for name in ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn","Lagna"]
        if chart.get(name, {}).get("sign") == d9["planets"].get(name, {}).get("sign")
    ]
    d9["vargottama"] = vargottama
    d9["place"] = place_name
    return d9


async def api_chart(
    birth_date: str, birth_time: str, birth_place: str,
    lat: Optional[float] = None, lon: Optional[float] = None,
    utc_offset: float = 5.5,
):
    """JSON API for chart data."""
    yr, mo, dy = map(int, birth_date.split("-"))
    hh, mm = map(int, birth_time.split(":"))
    lat_f, lon_f, place_name = resolve_location(birth_place, lat, lon)
    jd = julian_day(yr, mo, dy, hh + mm/60.0, utc_offset)
    chart = all_planets_sidereal(jd, lat_f, lon_f)
    moon_sid = chart["Moon"]["longitude"]
    dashas   = compute_dashas(date(yr, mo, dy), moon_sid)
    analysis = full_analysis(chart, birth_date)
    return {"chart": chart, "dashas": dashas, "analysis": analysis, "place": place_name}


@router.get("/api/rules/{chart_id}")
async def api_rule_evaluation(chart_id: str):
    """Evaluate a chart fixture against the default core BPHS rule pack."""
    return evaluate_chart_fixture(chart_id)
