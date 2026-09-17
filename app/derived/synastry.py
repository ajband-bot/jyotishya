"""Cross-chart synastry + D9 (Navamsha) cross-compatibility -- build_plan.md
Phase 4a item 4 (§5b: "Synastry (inter-chart Venus/Jupiter/7th-lord
aspects) between the two natal charts, per Marriage_Guide_Part4").

Implements the 7 synastry indicators (Marriage_Guide_Part4.md §15.1) and
the 5 D9 cross-compatibility rules (§16.1). All sign-relationship
classification reuses `app.derived.compatibility`'s axis machinery (DRY --
"is sign B in the 5/9, 6/8, etc. axis from sign A" is the exact same
question Bhakut Kuta already answers) rather than re-deriving distance
math a second time.
"""
from __future__ import annotations

from typing import Any

from app.astro.constants import SIGNS
from app.derived.compatibility import AXIS_RAW_SCORE, DIST_TO_AXIS, mutual_friends
from app.derived.factors import house_to_sign

CLASSICAL_7 = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]

# Qualitative gloss per axis, per Marriage_Guide_Part4.md §15.1's own
# per-indicator language -- descriptive only, does not feed any score.
AXIS_QUALITY = {
    "1/1": "highest_alignment_same_sign",
    "1/7": "complementary_polarity",
    "3/11": "friendly_growing_together",
    "4/10": "power_dynamic_tension",
    "5/9": "trikona_best_possible",
    "2/12": "value_and_resource_tension",
    "6/8": "adversarial_challenging",
}


def sign_axis(sign_a: int, sign_b: int) -> dict[str, Any]:
    dist = ((sign_b - sign_a) % 12) + 1
    axis = DIST_TO_AXIS[dist]
    return {"distance": dist, "axis": axis, "quality": AXIS_QUALITY[axis], "bhakut_raw_score_if_applicable": AXIS_RAW_SCORE[axis]}


def sun_moon_synastry(groom_chart: dict[str, Any], bride_chart: dict[str, Any]) -> dict[str, Any]:
    """Indicator 1 (most important per source): groom Sun <-> bride Moon,
    checked both directions."""
    groom_sun_to_bride_moon = sign_axis(groom_chart["Sun"]["sign"], bride_chart["Moon"]["sign"])
    bride_sun_to_groom_moon = sign_axis(bride_chart["Sun"]["sign"], groom_chart["Moon"]["sign"])
    return {
        "groom_sun_to_bride_moon": groom_sun_to_bride_moon,
        "bride_sun_to_groom_moon": bride_sun_to_groom_moon,
        "citation": "Vivaha Vrindavana Ch.4 Synastry Adhyaya (Marriage_Guide_Part4.md Indicator 1)",
    }


def moon_moon_synastry(groom_chart: dict[str, Any], bride_chart: dict[str, Any]) -> dict[str, Any]:
    """Indicator 2: Moon-to-Moon relationship (mental/emotional resonance)."""
    axis = sign_axis(groom_chart["Moon"]["sign"], bride_chart["Moon"]["sign"])
    return {"axis": axis, "citation": "Marriage_Guide_Part4.md Indicator 2"}


def lagna_lagna_synastry(groom_chart: dict[str, Any], bride_chart: dict[str, Any]) -> dict[str, Any]:
    """Indicator 3: Lagna-to-Lagna relationship -- 5/9 trikona is graded
    best per source."""
    axis = sign_axis(groom_chart["Lagna"]["sign"], bride_chart["Lagna"]["sign"])
    return {"axis": axis, "citation": "BPHS Ch.78 Lagna Melapaka (Marriage_Guide_Part4.md Indicator 3)"}


def venus_moon_synastry(groom_chart: dict[str, Any], bride_chart: dict[str, Any]) -> dict[str, Any]:
    """Indicator 4: groom's Venus (his love expression) vs bride's Moon
    (her emotional core)."""
    axis = sign_axis(groom_chart["Venus"]["sign"], bride_chart["Moon"]["sign"])
    return {"axis": axis, "citation": "Marriage_Guide_Part4.md Indicator 4"}


def jupiter_moon_synastry(groom_chart: dict[str, Any], bride_chart: dict[str, Any]) -> dict[str, Any]:
    """Indicator 5: bride's Jupiter (her marriage karaka, per BPHS Ch.32)
    vs groom's Moon (his emotional core)."""
    axis = sign_axis(bride_chart["Jupiter"]["sign"], groom_chart["Moon"]["sign"])
    return {"axis": axis, "citation": "Marriage_Guide_Part4.md Indicator 5"}


def lagna_lord_cross(groom_chart: dict[str, Any], bride_chart: dict[str, Any]) -> dict[str, Any]:
    """Indicator 6: are the two Lagna lords natural friends? Determines
    baseline fundamental-personality compatibility."""
    groom_lord = SIGNS[groom_chart["Lagna"]["sign"] - 1]["lord"]
    bride_lord = SIGNS[bride_chart["Lagna"]["sign"] - 1]["lord"]
    return {
        "groom_lagna_lord": groom_lord, "bride_lagna_lord": bride_lord,
        "mutual_friends": mutual_friends(groom_lord, bride_lord),
        "citation": "Marriage_Guide_Part4.md Indicator 6",
    }


def h7_lord_cross(groom_ctx: dict[str, Any], bride_ctx: dict[str, Any]) -> dict[str, Any]:
    """Indicator 7: are the two 7th-house lords natural friends? Determines
    whether both partners' marriage expectations are mutually satisfying."""
    groom_lord = groom_ctx["house_lords"][7]
    bride_lord = bride_ctx["house_lords"][7]
    return {
        "groom_h7_lord": groom_lord, "bride_h7_lord": bride_lord,
        "mutual_friends": mutual_friends(groom_lord, bride_lord),
        "citation": "Marriage_Guide_Part4.md Indicator 7",
    }


def synastry_report(groom_ctx: dict[str, Any], bride_ctx: dict[str, Any]) -> dict[str, Any]:
    """All 7 synastry indicators for one groom/bride ctx pair."""
    g_chart, b_chart = groom_ctx["chart"], bride_ctx["chart"]
    return {
        "sun_moon": sun_moon_synastry(g_chart, b_chart),
        "moon_moon": moon_moon_synastry(g_chart, b_chart),
        "lagna_lagna": lagna_lagna_synastry(g_chart, b_chart),
        "venus_moon": venus_moon_synastry(g_chart, b_chart),
        "jupiter_moon": jupiter_moon_synastry(g_chart, b_chart),
        "lagna_lord": lagna_lord_cross(g_chart, b_chart),
        "h7_lord": h7_lord_cross(groom_ctx, bride_ctx),
        "citation": "Marriage_Guide_Part4.md Step 15 (7 Key Synastry Indicators)",
    }


def d9_cross_compatibility(groom_ctx: dict[str, Any], bride_ctx: dict[str, Any]) -> dict[str, Any]:
    """5 D9 cross-compatibility rules (Marriage_Guide_Part4.md §16.1).

    Rule 5 interpretation note (disclosed, editorial): the source text's
    "D9 7th houses are mutually aspecting" is not fully explicit about
    which aspect relationship qualifies. Interpreted here as the two
    people's D9-7th signs being in a 1/7 (mutual full-aspect/opposition)
    relationship to each other -- the only aspect both classical Parashari
    aspect doctrine and this codebase's own aspect engine treat as
    universal to every planet, making it the least assumption-laden
    reading of "mutually aspecting" between two independent D9 charts.
    """
    g_d9, b_d9 = groom_ctx["d9"], bride_ctx["d9"]

    moon_axis = sign_axis(g_d9["planets"]["Moon"]["sign"], b_d9["planets"]["Moon"]["sign"])
    jupiter_axis = sign_axis(g_d9["planets"]["Jupiter"]["sign"], b_d9["planets"]["Jupiter"]["sign"])
    shared_exalted = [
        p for p in CLASSICAL_7
        if g_d9["planets"][p]["state"] == "exalted" and b_d9["planets"][p]["state"] == "exalted"
    ]
    venus_lagna_match = (
        g_d9["planets"]["Venus"]["sign"] == b_d9["lagna_sign"]
        or b_d9["planets"]["Venus"]["sign"] == g_d9["lagna_sign"]
    )
    g_d9_h7_sign = house_to_sign(g_d9["lagna_sign"], 7)
    b_d9_h7_sign = house_to_sign(b_d9["lagna_sign"], 7)
    h7_axis = sign_axis(g_d9_h7_sign, b_d9_h7_sign)

    return {
        "rule1_moon_mirror": {"met": moon_axis["axis"] == "1/7", "axis": moon_axis},
        "rule2_jupiter_mirror": {"met": jupiter_axis["axis"] == "1/7", "axis": jupiter_axis},
        "rule3_shared_exalted_planets": {"met": len(shared_exalted) > 0, "planets": shared_exalted},
        "rule4_venus_lagna_match": {"met": venus_lagna_match},
        "rule5_d9_seventh_houses_mutual_aspect": {
            "met": h7_axis["axis"] == "1/7",
            "groom_d9_h7_sign": g_d9_h7_sign, "bride_d9_h7_sign": b_d9_h7_sign, "axis": h7_axis,
        },
        "citation": "BPHS Ch.79 (Marriage_Guide_Part4.md Step 16, 5 D9 Cross-Compatibility Rules)",
    }
