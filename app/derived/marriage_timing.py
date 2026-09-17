"""Marriage timing -- the Dasha/Transit/D9 "Triple Agreement" engine,
build_plan.md Phase 4a item 3 (§5b: "Dasha/Transit/D9 Triple Agreement for
marriage timing... already specified in Marriage_Guide_Part3").

Per Marriage_Guide_Part3.md's own framing:

    AGREEMENT 1: Dasha period (MD or AD) involves 7th lord, marriage
                 karaka (Venus/Jupiter), or Darakaraka
    AGREEMENT 2: Transit (Gochara) of Jupiter/Saturn/Rahu-Ketu activates
                 H7, H7 lord, or Venus
    AGREEMENT 3: Navamsha (D9) activation -- D9 Lagna lord or D9 7th
                 lord's dasha period is running
    Event = CONFIRMED when 2 of 3 agree; CERTAIN when all 3 align.

Every number here is computed, not narrated: dasha windows come from
app.astro.dashas (the same Vimshottari engine every other reading already
uses), transit checks reuse app.astro.transits.transit_assessment's
already-built (and already ephemeris-backed) `marriage_alignment` flags
verbatim -- no new transit logic was invented for this module.
"""
from __future__ import annotations

from datetime import date, timedelta
from typing import Any

from app.astro.constants import SIGNS
from app.astro.dashas import compute_antardashas
from app.astro.transits import transit_assessment
from app.derived.factors import house_to_sign

CLASSICAL_9 = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]

# Rank order per Marriage_Guide_Part3.md §9.1 "Primary Dasha Triggers for
# Marriage" -- lower rank number = higher probability per source.
RANK_LABELS = {
    1: "h7_lord", 2: "marriage_karaka", 3: "darakaraka", 4: "d9_lagna_lord",
    5: "h7_occupant", 6: "second_lord", 7: "lagna_lord",
}


def identify_significators(ctx: dict[str, Any], gender: str = "male") -> dict[str, Any]:
    """The marriage-timing significator set for one chart. `gender`
    selects the natural marriage karaka per BPHS Ch.32 (Venus for a male
    chart, Jupiter for a female chart) -- everything else is
    gender-agnostic."""
    if gender not in ("male", "female"):
        raise ValueError("gender must be 'male' or 'female'")
    chart = ctx["chart"]
    h7_lord = ctx["house_lords"][7]
    marriage_karaka = "Venus" if gender == "male" else "Jupiter"
    darakaraka = ctx["karakas"]["darakaraka"]
    d9_lagna_sign = ctx["d9"]["lagna_sign"]
    d9_lagna_lord = SIGNS[d9_lagna_sign - 1]["lord"]
    d9_seventh_sign = house_to_sign(d9_lagna_sign, 7)
    d9_seventh_lord = SIGNS[d9_seventh_sign - 1]["lord"]
    h7_occupants = [p for p in CLASSICAL_9 if chart[p]["house"] == 7]
    second_lord = ctx["house_lords"][2]
    lagna_lord = ctx["house_lords"][1]

    ranked = [
        {"rank": 1, "role": "h7_lord", "planet": h7_lord},
        {"rank": 2, "role": "marriage_karaka", "planet": marriage_karaka},
        {"rank": 3, "role": "darakaraka", "planet": darakaraka},
        {"rank": 4, "role": "d9_lagna_lord", "planet": d9_lagna_lord},
    ]
    ranked += [{"rank": 5, "role": "h7_occupant", "planet": p} for p in h7_occupants]
    ranked += [
        {"rank": 6, "role": "second_lord", "planet": second_lord},
        {"rank": 7, "role": "lagna_lord", "planet": lagna_lord},
    ]

    return {
        "gender": gender, "h7_lord": h7_lord, "marriage_karaka": marriage_karaka,
        "darakaraka": darakaraka, "d9_lagna_lord": d9_lagna_lord, "d9_seventh_lord": d9_seventh_lord,
        "h7_occupants": h7_occupants, "second_lord": second_lord, "lagna_lord": lagna_lord,
        "ranked_significators": ranked,
        "citation": "BPHS Ch.32/78 + Phaladeepika Ch.7 (Marriage_Guide_Part3.md §9.1 Primary Dasha Triggers)",
    }


def dasha_agreement_windows(ctx: dict[str, Any], significators: dict[str, Any]) -> list[dict[str, Any]]:
    """Every Antardasha window (across the full stored Mahadasha timeline)
    whose MD or AD lord matches a ranked significator, best (lowest)
    matched rank first."""
    best_rank_by_planet: dict[str, int] = {}
    for item in significators["ranked_significators"]:
        planet = item["planet"]
        if planet not in best_rank_by_planet or item["rank"] < best_rank_by_planet[planet]:
            best_rank_by_planet[planet] = item["rank"]

    windows: list[dict[str, Any]] = []
    for md in ctx["dashas"]:
        for ad in compute_antardashas(md):
            matched = []
            if md["planet"] in best_rank_by_planet:
                matched.append({"level": "mahadasha", "planet": md["planet"], "rank": best_rank_by_planet[md["planet"]]})
            if ad["planet"] in best_rank_by_planet:
                matched.append({"level": "antardasha", "planet": ad["planet"], "rank": best_rank_by_planet[ad["planet"]]})
            if matched:
                windows.append({
                    "mahadasha": md["planet"], "antardasha": ad["planet"],
                    "start": ad["start"], "end": ad["end"],
                    "matched_significators": matched,
                    "best_rank": min(m["rank"] for m in matched),
                    "best_rank_label": RANK_LABELS[min(m["rank"] for m in matched)],
                })
    windows.sort(key=lambda w: (w["best_rank"], w["start"]))
    return windows


def transit_agreement_dates(
    chart: dict[str, Any], start_date: date, end_date: date,
    node_type: str = "mean", step_days: int = 30,
) -> list[dict[str, Any]]:
    """Sample app.astro.transits.transit_assessment across a date range and
    flag dates where at least 2 of its 4 `marriage_alignment` checks
    (Jupiter from Moon in a marriage house, Jupiter from Lagna on the H1/H7
    axis, Saturn not in the 8th from Moon, Rahu/Ketu on the H1/H7 axis)
    agree -- reuses the existing, already-ephemeris-backed transit engine
    verbatim rather than inventing a second one."""
    favorable = []
    current = start_date
    while current <= end_date:
        assessment = transit_assessment(chart, current, node_type=node_type)
        alignment = assessment["marriage_alignment"]
        score = sum(1 for flag in alignment.values() if flag)
        if score >= 2:
            favorable.append({
                "date": assessment["date"], "score": score, "marriage_alignment": alignment,
                "jupiter_transit_sign": assessment["jupiter_assessment"]["transit_sign"],
                "saturn_transit_sign": assessment["saturn_assessment"]["transit_sign"],
            })
        current += timedelta(days=step_days)
    return favorable


PROBABILITY_BY_VERDICT = {"certain": 85, "confirmed": 60, "possible": 35}


def _reason_text(window: dict[str, Any]) -> str:
    """Plain-English derivation string for one combined window -- built
    entirely from fields already on `window`, never a fresh LLM narration.
    Kept separate from `verdict`/`probability_percent` so the UI can show
    both the number and *why* without re-deriving anything."""
    role_bits = ", ".join(
        f"{m['level']}={m['planet']} ({RANK_LABELS[m['rank']].replace('_', ' ')})" for m in window["matched_significators"]
    )
    reason = f"Vimshottari {window['mahadasha']}/{window['antardasha']} period matches {role_bits}"
    if "transit" in window["agreements"]:
        reason += "; a favorable Jupiter/Saturn/Rahu-Ketu transit window (Gochara marriage-alignment check) falls inside this period"
    if "d9_activation" in window["agreements"]:
        reason += "; the dasha lord is also the D9 (Navamsha) Lagna or 7th lord, confirming the marriage significator in the divisional chart too"
    return reason


def _combine_agreements(
    dasha_windows: list[dict[str, Any]], transit_dates: list[dict[str, Any]], significators: dict[str, Any],
) -> list[dict[str, Any]]:
    d9_lords = {significators["d9_lagna_lord"], significators["d9_seventh_lord"]}
    combined = []
    for window in dasha_windows:
        matching_transits = [t for t in transit_dates if window["start"] <= t["date"] <= window["end"]]
        agreements = ["dasha"]
        if matching_transits:
            agreements.append("transit")
        if window["mahadasha"] in d9_lords or window["antardasha"] in d9_lords:
            agreements.append("d9_activation")
        agreement_count = len(agreements)
        verdict = "certain" if agreement_count == 3 else ("confirmed" if agreement_count == 2 else "possible")
        entry = {
            **window, "agreements": agreements, "agreement_count": agreement_count,
            "matching_transit_dates": [t["date"] for t in matching_transits], "verdict": verdict,
            "probability_percent": PROBABILITY_BY_VERDICT[verdict],
        }
        entry["reason"] = _reason_text(entry)
        combined.append(entry)
    combined.sort(key=lambda c: (-c["agreement_count"], c["best_rank"], c["start"]))
    return combined


def upcoming_marriage_windows(
    combined: list[dict[str, Any]], today: date | None = None, top_n: int = 5,
) -> list[dict[str, Any]]:
    """Restrict the combined Triple-Agreement windows to ones that are
    still current or in the future (an 'unmarried native, when might this
    happen' view is meaningless over windows that already passed) --
    same strength ordering as `combined`, just filtered and capped."""
    if today is None:
        today = date.today()
    today_str = today.isoformat()
    future = [w for w in combined if w["end"] >= today_str]
    return future[:top_n]


def marriage_timing_report(
    ctx: dict[str, Any], gender: str = "male", years: int = 30, step_days: int = 30,
) -> dict[str, Any]:
    """Full Triple Agreement marriage-timing report for one chart.

    `years` bounds how far past today (or birth, whichever is later) the
    transit scan runs -- kept finite deliberately since Swiss Ephemeris
    transit calls are not free; 30 years at a 30-day step is ~365 calls,
    fast in practice and covers the entire classically-relevant marriage
    window for a native of any age.
    """
    significators = identify_significators(ctx, gender)
    dasha_windows = dasha_agreement_windows(ctx, significators)

    dob = date.fromisoformat(str(ctx["fixture"]["dob"]))
    today = date.today()
    scan_start = today if today > dob else dob
    try:
        scan_end = scan_start.replace(year=scan_start.year + years)
    except ValueError:  # Feb 29 edge case
        scan_end = scan_start.replace(month=2, day=28, year=scan_start.year + years)
    node_type = ctx.get("settings", {}).get("node_type", "mean")
    transit_dates = transit_agreement_dates(ctx["chart"], scan_start, scan_end, node_type=node_type, step_days=step_days)

    combined = _combine_agreements(dasha_windows, transit_dates, significators)
    upcoming = upcoming_marriage_windows(combined, today=today, top_n=5)
    return {
        "significators": significators,
        "scan_window": {"start": scan_start.isoformat(), "end": scan_end.isoformat()},
        "dasha_windows": dasha_windows[:20],
        "transit_favorable_dates": transit_dates,
        "combined_windows": combined[:10],
        "upcoming_windows": upcoming,
        "probability_model": "heuristic_proxy",
        "probability_caveat": (
            "probability_percent is a heuristic proxy derived only from how many of the 3 classical "
            "agreement channels (dasha/transit/D9) coincide in a window (85/60/35 for certain/confirmed/"
            "possible) -- it is NOT a statistically validated probability, and Jyotisha itself never claims "
            "one (Axiom 3: free will operates within karmic parameters). Treat as relative ranking between "
            "windows for THIS chart, not an absolute likelihood."
        ),
        "citation": "BPHS Ch.78 Vivaha Kala Adhyaya (Marriage_Guide_Part3.md's Triple Agreement principle)",
    }
