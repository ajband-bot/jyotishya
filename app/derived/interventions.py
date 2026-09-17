"""Argala (Planetary Intervention), BPHS Ch.31 -- build_plan.md Phase 6
("Argala, built from text only, extra review pass -- no reference repo
has it, confirmed across all three").

Per that instruction, the primary text (`Reference books/BPHS -
1 RSanthanam.pdf`, Ch.31 "Argala Or Planetary Intervention") was read
directly (via `pdftotext -layout`, per AGENTS.md AD-8) since neither
PyJHora nor OpenJyotish has ANY Argala implementation to cross-check
against (confirmed by grep -- docs/public-repo-review/02-feature-
comparison.md). This is the pre-existing `practical_house_argala` engine
(itself already build_plan-scoped as `computed_simplified`/practical_proxy
for the STRENGTH-COMPARISON side, since "is planet A stronger than planet
B" has no single universally-agreed numeric answer), corrected and
extended against the primary text's own verses:

  - v.2-9 gives FOUR support/obstruction channels, not three: 2nd/12th,
    4th/10th, 11th/3rd -- AND a 4th, previously MISSING here: "The 5th is
    also an Argala place [obstructed by] the 9th." Added below as a real
    textual correction, same category as Phase 3's Mangal Dosha
    cancellation-condition fix.
  - v.4-5: "If there are 3 or more malefics in the 3rd, they cause
    Vipareeta Argala (more effective intervention) which will also be
    harmless and very favourable" -- an explicit reversal (obstruction
    becomes auspicious), modeled as `vipareeta_argala` on the 11th/3rd
    channel specifically (the only channel v.4-5 names).
  - v.2-9 ALSO gives a count-based tiebreak alongside the strength-based
    one already implemented: "if the number of Argala [supporting]
    planets are more than the obstructing planets, then also the Argala
    will prevail" -- added as an explicit OR condition, not a replacement
    (both rules are textually present; this module never silently drops
    one for the other, per Cardinal Rule 3).
  - v.11-17 give named effects for unobstructed Argala on each of the
    12 houses -- ARGALA_HOUSE_EFFECTS below, cited verbatim in spirit.
  - v.17 (fame) and v.18 (raja yoga) name TWO composite conditions this
    module now also flags: Argala for {Arudha Pada, Lagna, 7th-from-both}
    -> fame; Argala for {Lagna, 5th, 9th} -> raja yoga. These reuse the
    exact same per-house Argala computation, just at extra reference
    points (the Arudha Lagna's own house), rather than a new engine.

NOT attempted this pass (disclosed, not fabricated): v.4-5's quarter-
based (7deg30' padas) fine-grained nullification rule, which needs a
degree-level tiebreak beyond whole-sign house counting. This is a real
refinement candidate, not silently assumed to already be covered by the
whole-sign channel logic above.
"""
from __future__ import annotations

from typing import Any


BENEFICS = {"Moon", "Mercury", "Jupiter", "Venus"}
MALEFICS = {"Sun", "Mars", "Saturn", "Rahu", "Ketu"}
ALL_PLANETS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]

# BPHS Ch.31 v.2-9: (support_offset, counter_offset) pairs, each counted
# from the reference house/planet. The 5th/9th pair is the correction
# this module adds over the original 3-channel version.
CHANNELS = ((2, 12), (4, 10), (11, 3), (5, 9))
VIPAREETA_COUNTER_OFFSET = 3  # v.4-5 names the 3rd specifically
REFERENCE_HOUSES = (1, 2, 5, 7, 9, 10, 12)

# BPHS Ch.31 v.11-17: named effect of an unobstructed Argala for each house.
ARGALA_HOUSE_EFFECTS = {
    1: "Fame and public recognition.",
    2: "Acquisition of wealth and grains.",
    3: "Happiness from co-born (siblings).",
    4: "Residences, quadrupeds (vehicles/livestock), and relatives.",
    5: "Sons/grandsons and intelligence.",
    6: "Fear from enemies (Argala here is a mixed/cautionary signal, not purely benefic).",
    7: "Abundant wealth and marital happiness.",
    8: "Difficulties.",
    9: "Fortunes.",
    10: "Royal honour (career/status recognition).",
    11: "Gains.",
    12: "Expenses.",
}


def _rel_house(from_house: int, offset: int) -> int:
    return ((from_house - 1 + offset - 1) % 12) + 1


def _occupants(chart: dict[str, Any], house_no: int) -> list[str]:
    return [planet for planet in ALL_PLANETS if chart[planet]["house"] == house_no]


def _planet_weight(planet: str, shadbala: dict[str, Any], yoga_karakas: list[str]) -> float:
    strength = shadbala[planet]["total_score"] / 100.0
    if planet in BENEFICS:
        nature = 1.0
    elif planet in MALEFICS:
        nature = -0.85
    else:
        nature = 0.4
    if planet in yoga_karakas:
        strength *= 1.1
    return round(strength * nature, 4)


def _channel_status(net_score: float, support_score: float, counter_score: float, support_count: int, counter_count: int) -> str:
    """BPHS v.2-9 gives TWO independent ways an Argala can be said to
    'prevail' over its obstruction -- strength (already modeled via
    Shadbala-weighted score) OR sheer count of supporting vs obstructing
    planets. Either one is sufficient; only when BOTH favor the
    obstruction does the channel count as genuinely cancelled."""
    if support_score <= 0:
        return "no_argala"
    strength_favors_support = counter_score <= abs(support_score)
    count_favors_support = support_count >= counter_count
    if strength_favors_support or count_favors_support:
        if net_score >= 0.45 or count_favors_support:
            return "supportive"
        return "mixed"
    return "cancelled"


def _compute_house_argala(reference_house: int, chart: dict[str, Any], shadbala: dict[str, Any], yoga_karakas: list[str]) -> dict[str, Any]:
    channels = []
    total_net = 0.0
    for support_offset, counter_offset in CHANNELS:
        support_house = _rel_house(reference_house, support_offset)
        counter_house = _rel_house(reference_house, counter_offset)
        support_planets = _occupants(chart, support_house)
        counter_planets = _occupants(chart, counter_house)
        support_score = round(sum(_planet_weight(p, shadbala, yoga_karakas) for p in support_planets), 4)
        counter_score = round(sum(abs(_planet_weight(p, shadbala, yoga_karakas)) for p in counter_planets), 4)
        net_score = round(support_score - counter_score, 4)
        total_net += net_score

        vipareeta = (
            counter_offset == VIPAREETA_COUNTER_OFFSET
            and sum(1 for p in counter_planets if p in MALEFICS) >= 3
        )
        status = "vipareeta_favorable" if vipareeta else _channel_status(
            net_score, support_score, counter_score, len(support_planets), len(counter_planets)
        )

        channels.append({
            "support_house": support_house,
            "counter_house": counter_house,
            "support_planets": support_planets,
            "counter_planets": counter_planets,
            "support_score": support_score,
            "counter_score": counter_score,
            "net_score": net_score,
            "vipareeta_argala": vipareeta,
            "status": status,
            "citation": "BPHS Ch.31 v.2-9" + (" + v.4-5 (Vipareeta Argala)" if vipareeta else ""),
        })

    total_net = round(total_net, 4)
    any_vipareeta = any(c["vipareeta_argala"] for c in channels)
    if any_vipareeta or total_net >= 0.75:
        verdict = "supportive"
    elif total_net <= -0.75:
        verdict = "obstructive"
    else:
        verdict = "mixed"

    return {
        "reference_house": reference_house,
        "channels": channels,
        "net_score": total_net,
        "verdict": verdict,
        "unobstructed": verdict == "supportive",
        "classical_effect": ARGALA_HOUSE_EFFECTS.get(reference_house),
    }


def practical_argala(context: dict[str, Any], shadbala: dict[str, Any] | None = None) -> dict[str, Any]:
    chart = context["chart"]
    shadbala = shadbala or context["shadbala"]
    yoga_karakas = context.get("yoga_karakas", [])

    houses: dict[int, Any] = {
        reference_house: _compute_house_argala(reference_house, chart, shadbala, yoga_karakas)
        for reference_house in REFERENCE_HOUSES
    }

    # v.17: Argala for {Arudha Pada (AL), Lagna, 7th-from-both} -> fame.
    # v.18: Argala for {Lagna, 5th, 9th} -> raja yoga. Both reuse the same
    # per-house computation at extra reference points (AL's own house and
    # the 7th from it), rather than a new engine.
    lagna_pada = context.get("lagna_pada")
    fame_via_argala = None
    if lagna_pada is not None:
        al_house = lagna_pada["pada_house"]
        seventh_from_al = _rel_house(al_house, 7)
        for extra_house in (al_house, seventh_from_al):
            if extra_house not in houses:
                houses[extra_house] = _compute_house_argala(extra_house, chart, shadbala, yoga_karakas)
        fame_via_argala = all(
            houses[h]["unobstructed"] for h in (1, 7, al_house, seventh_from_al)
        )

    raja_yoga_via_argala = all(houses[h]["unobstructed"] for h in (1, 5, 9))

    return {
        "model": "house_argala_v2",
        "houses": houses,
        "lagna": houses[1],
        "marriage": houses[7],
        "career": houses[10],
        "raja_yoga_via_argala": raja_yoga_via_argala,
        "fame_via_argala": fame_via_argala,
        "citation": "BPHS Ch.31 (R. Santhanam translation, Reference books/BPHS - 1 RSanthanam.pdf), read directly per AGENTS.md AD-8",
    }
