"""Generic Event Agreement Engine (build_plan.md Phase 2 item 8):
D1 house strength + relevant varga confirmation + daśā activation + transit
activation, tallied into one evidence-backed agreement score per life-event
domain.

EVENT_DOMAINS below encodes the theme list build_plan.md asked to be
connectable to predictions (Career, Promotion, Marriage, ... 23 themes),
each mapped to its classical house(s)/karaka(s)/varga per BPHS Ch.11
(house significations) + Ch.10 (karakatva) + Ch.6 (varga purposes).
Several themes have NO dedicated varga among the 16 BPHS-genuine vargas
this codebase actually implements (see app.astro.vargas docstring -- D5/
D6/D8/D11 are deliberately unsupported); those are marked `varga: None`
here rather than guessing a substitute, per Cardinal Rule 2/4.
"""
from __future__ import annotations

from typing import Any

from app.derived.varga_confirmation import confirm_dignity

EVENT_DOMAINS: dict[str, dict[str, Any]] = {
    "career": {"houses": [10, 6], "karakas": ["Saturn", "Sun"], "varga": 10},
    "promotion": {"houses": [10, 11], "karakas": ["Sun", "Jupiter"], "varga": 10},
    "job_change": {"houses": [10, 12, 6], "karakas": ["Saturn"], "varga": 10},
    "business": {"houses": [7, 10, 3], "karakas": ["Mercury"], "varga": 10},
    "income": {"houses": [2, 11], "karakas": ["Jupiter"], "varga": 2},
    "windfall": {"houses": [11, 8, 5], "karakas": ["Jupiter", "Rahu"], "varga": 2},
    "property_purchase": {"houses": [4, 12], "karakas": ["Mars", "Venus"], "varga": 4},
    "property_sale": {"houses": [4, 12], "karakas": ["Mars"], "varga": 4},
    "marriage": {"houses": [7, 2], "karakas": ["Venus", "Jupiter"], "varga": 9},
    "relationship_strain": {"houses": [7, 8, 12], "karakas": ["Venus"], "varga": 9},
    "childbirth": {"houses": [5], "karakas": ["Jupiter"], "varga": 7},
    "education": {"houses": [4, 5, 9], "karakas": ["Mercury", "Jupiter"], "varga": 24},
    "foreign_travel": {"houses": [3, 9, 12], "karakas": ["Rahu"], "varga": None},
    "foreign_relocation": {"houses": [12, 9], "karakas": ["Rahu"], "varga": None},
    "litigation": {"houses": [6, 8, 12], "karakas": ["Saturn", "Mars"], "varga": None},
    "debt": {"houses": [6, 8, 12], "karakas": ["Saturn"], "varga": 2},
    "health_attention": {"houses": [1, 6], "karakas": ["Sun"], "varga": None},  # D6 (disease) not implemented -- see app.astro.vargas
    "spiritual_development": {"houses": [9, 12], "karakas": ["Jupiter", "Ketu"], "varga": 20},
    "retirement": {"houses": [10, 12], "karakas": ["Saturn"], "varga": None},
    "inheritance": {"houses": [8], "karakas": ["Saturn"], "varga": None},
    "partnership": {"houses": [7], "karakas": ["Venus", "Mercury"], "varga": 9},
    "vehicle": {"houses": [4], "karakas": ["Venus", "Mars"], "varga": 4},
    "public_recognition": {"houses": [10, 1, 9], "karakas": ["Sun"], "varga": 10},
}

GOOD_DIGNITIES = {"exalted", "own-sign"}


def event_agreement(ctx: dict[str, Any], theme: str) -> dict[str, Any]:
    if theme not in EVENT_DOMAINS:
        raise ValueError(f"Unknown event theme: {theme!r}. Known: {sorted(EVENT_DOMAINS)}")
    domain = EVENT_DOMAINS[theme]
    houses = domain["houses"]
    karakas = domain["karakas"]
    chart = ctx["chart"]
    house_lords = ctx["house_lords"]

    score = 0
    max_score = 0
    evidence: dict[str, Any] = {}

    # 1. D1 house strength (always applicable)
    house_strengths = {h: ctx["bhava_bala"]["houses"][h]["verdict"] for h in houses}
    evidence["d1_house_strength"] = house_strengths
    max_score += 1
    if any(v == "strong" for v in house_strengths.values()):
        score += 1

    # 2. Relevant-varga confirmation (only if this theme has a supported varga)
    if domain["varga"] is not None:
        varga_confirmations = {}
        for house in houses:
            lord = house_lords[house]
            varga_confirmations[house] = confirm_dignity(chart, lord, GOOD_DIGNITIES, vargas=[domain["varga"]])
        evidence["varga_confirmation"] = {"varga": domain["varga"], "by_house": varga_confirmations}
        max_score += 1
        if any(v["confirmation_count"] >= 1 for v in varga_confirmations.values()):
            score += 1
    else:
        evidence["varga_confirmation"] = {
            "varga": None,
            "note": "data_gap -- no BPHS-genuine varga implemented for this theme (see app.astro.vargas docstring)",
        }

    # 3. Dasha activation
    current = ctx.get("current_dasha") or {}
    md = current.get("mahadasha", {}).get("planet")
    ad = current.get("antardasha", {}).get("planet")
    domain_lords = {house_lords[h] for h in houses}
    md_connected = md in domain_lords or md in karakas
    ad_connected = ad in domain_lords or ad in karakas
    evidence["dasha_activation"] = {"md": md, "ad": ad, "md_connected": md_connected, "ad_connected": ad_connected}
    max_score += 1
    if md_connected or ad_connected:
        score += 1

    # 4. Transit activation (only meaningful for the 2 planets we assess in depth)
    trackable_karakas = [k for k in karakas if k in ("Jupiter", "Saturn")]
    if trackable_karakas:
        transit_quality = {}
        for karaka in trackable_karakas:
            key = "jupiter_assessment" if karaka == "Jupiter" else "saturn_assessment"
            transit_quality[karaka] = ctx["transits"].get(key, {}).get("quality")
        evidence["transit_activation"] = transit_quality
        max_score += 1
        if any(q == "auspicious" for q in transit_quality.values()):
            score += 1
    else:
        evidence["transit_activation"] = {"note": "data_gap -- transit engine only assesses Jupiter/Saturn in depth"}

    ratio = round(score / max_score, 4) if max_score else 0.0
    if ratio >= 0.75:
        verdict = "strong_agreement"
    elif ratio >= 0.5:
        verdict = "moderate_agreement"
    else:
        verdict = "weak_agreement"

    return {
        "theme": theme,
        "domain": domain,
        "evidence": evidence,
        "score": score,
        "max_score": max_score,
        "agreement_ratio": ratio,
        "verdict": verdict,
        "citation": "Generic composed engine: D1 house strength + relevant-varga confirmation + dasha activation + transit activation (build_plan.md Phase 2 item 8)",
    }


def all_event_agreements(ctx: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {theme: event_agreement(ctx, theme) for theme in EVENT_DOMAINS}
