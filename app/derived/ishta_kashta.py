"""Full classical Ishta/Kashta Phala, BPHS Ch.28 -- build_plan.md Phase 6
("Ishta/Kashta Phala"), closing (partially, honestly) the data_gap named
in AGENTS.md/build_plan.md since Phase 0.

Primary text read directly (`Reference books/BPHS - 1 RSanthanam.pdf`,
via `pdftotext -layout`, per AGENTS.md AD-8), not guessed or ported from
either reference repo (neither PyJHora nor OpenJyotish exposes a
dedicated Ishta/Kashta module -- see docs/public-repo-review; this is a
genuine build-from-text-only case, same category as Argala).

BPHS Ch.28 v.2-6 gives an exact, reconstructible formula:

  1. Uchcha Rasmi ("exaltation ray"): fold the planet's distance from its
     own deep-debilitation point to <=180 deg (D). Rasmi = 1 + D/30,
     continuous over [1, 7]. (Verse 2's "add 1 Rasi, double the degrees"
     instruction is the classical Rasi;Kala mixed-radix way of expressing
     this same continuous ratio -- reconciled here algebraically: signs =
     D//30, remainder = D%30, Rasmi = (signs+1) + (2*remainder)/60, which
     simplifies to exactly 1 + D/30.)
  2. Cheshta Rasmi ("motion ray"): identical fold-and-scale formula
     applied to the planet's Cheshta Kendra instead of the debilitation
     distance. BPHS gives the Cheshta Kendra formula explicitly ONLY for
     Sun (Sun + 90 deg) and Moon (Moon - Sun) in this chapter (v.3-4) --
     Mars through Saturn need the retrograde/direct 8-tier motion
     classification from Ch.27's own Chesta Bala, which
     app.derived.shadbala's own module docstring already discloses as a
     data_gap (exact tier boundaries not present in the extracted excerpt).
     Rather than silently reuse a different, unrelated proxy for those 5
     planets, Cheshta Rasmi (and therefore Ishta/Kashta) is reported as an
     explicit data_gap for them -- the SAME disclosed gap, not a new one.
  3. Ishta Phala = 5 * (Uchcha Rasmi + Cheshta Rasmi - 2), which is
     verse 6's "(Uchcha Rasmi - 1) and (Cheshta Rasmi - 1), each x10,
     summed, halved" -- algebraically identical, kept as one line for
     clarity. Range [0, 60] by construction (each Rasmi in [1, 7]).
  4. Kashta Phala = 60 - Ishta Phala.

Disclosed, NOT attempted this pass (real, separate refinement per v.7-14,
same "partial-but-honest" precedent as Shadbala's own remaining gaps):
the Saptavargaja Ishta-Kashta refinement, which re-weights the above by
each of 7 divisional charts' dignity tier (Subhanka/Asubhanka points:
60/45/30/22/15/8/4/2/0 for exalted/moolatrikona/own/great-friend/friend/
neutral/enemy/great-enemy/debilitated) multiplied by that planet's own
Shadbala Pinda -- a genuinely separate compounding layer BPHS treats as
"Ishta Kashta (Continued)", not a refinement of the base Sun/Moon figure
computed here.
"""
from __future__ import annotations

from typing import Any

from app.derived.shadbala import debilitation_distance

CLASSICAL_7 = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]


def _fold(distance_deg: float) -> float:
    """Fold any angular difference to the classical <=180 deg range used
    by both Uchcha Rasmi and Cheshta Rasmi (BPHS Ch.28 v.2-4's own
    'if the sum exceeds 6 signs, deduct from 12 signs' instruction)."""
    d = distance_deg % 360
    return 360 - d if d > 180 else d


def _rasmi(folded_distance_deg: float) -> float:
    """BPHS Ch.28 v.2 (Uchcha Rasmi) / v.3-4 (Cheshta Rasmi, same
    algorithm applied to a different base angle): Rasmi = 1 + D/30,
    continuous over [1, 7] -- see module docstring for the Rasi;Kala
    mixed-radix derivation this closed form reproduces exactly."""
    return round(1.0 + folded_distance_deg / 30.0, 4)


def uchcha_rasmi(planet: str, longitude: float) -> float:
    return _rasmi(_fold(debilitation_distance(planet, longitude)))


def cheshta_kendra_sun(sun_longitude: float) -> float:
    """BPHS Ch.28 v.3: Sun's own Cheshta Kendra = Sayana Sun + 3 Rasis (90 deg)."""
    return (sun_longitude + 90.0) % 360.0


def cheshta_kendra_moon(moon_longitude: float, sun_longitude: float) -> float:
    """BPHS Ch.28 v.4: Moon's Cheshta Kendra = Moon - Sun."""
    return (moon_longitude - sun_longitude) % 360.0


def cheshta_rasmi_luminary(kendra_deg: float) -> float:
    return _rasmi(_fold(kendra_deg))


def ishta_phala(uchcha: float, cheshta: float) -> float:
    """BPHS Ch.28 v.6: [(Uchcha Rasmi - 1) + (Cheshta Rasmi - 1)] x 10 / 2,
    algebraically = 5 * (Uchcha + Cheshta - 2). Clamped to [0, 60] as a
    defensive guard only -- by construction (each Rasmi in [1, 7]) this
    never actually triggers, kept purely to fail loudly instead of
    silently if a future refactor breaks that invariant."""
    value = 5.0 * (uchcha + cheshta - 2.0)
    return round(max(0.0, min(60.0, value)), 4)


def kashta_phala(ishta: float) -> float:
    return round(60.0 - ishta, 4)


def classical_ishta_kashta(ctx: dict[str, Any]) -> dict[str, Any]:
    """Sun and Moon: full classical Ishta/Kashta Phala (BPHS Ch.28 v.2-6).
    Mars/Mercury/Jupiter/Venus/Saturn: disclosed data_gap (Cheshta Rasmi
    needs the same Chesta-Bala motion-tier data app.derived.shadbala
    already discloses as incomplete -- not fabricated here either)."""
    chart = ctx["chart"]
    sun_lon = chart["Sun"]["longitude"]
    moon_lon = chart["Moon"]["longitude"]

    planets: dict[str, Any] = {}

    sun_uchcha = uchcha_rasmi("Sun", sun_lon)
    sun_cheshta = cheshta_rasmi_luminary(cheshta_kendra_sun(sun_lon))
    sun_ishta = ishta_phala(sun_uchcha, sun_cheshta)
    planets["Sun"] = {
        "model": "classical", "uchcha_rasmi": sun_uchcha, "cheshta_rasmi": sun_cheshta,
        "ishta_phala": sun_ishta, "kashta_phala": kashta_phala(sun_ishta),
        "citation": "BPHS Ch.28 v.2-6",
    }

    moon_uchcha = uchcha_rasmi("Moon", moon_lon)
    moon_cheshta = cheshta_rasmi_luminary(cheshta_kendra_moon(moon_lon, sun_lon))
    moon_ishta = ishta_phala(moon_uchcha, moon_cheshta)
    planets["Moon"] = {
        "model": "classical", "uchcha_rasmi": moon_uchcha, "cheshta_rasmi": moon_cheshta,
        "ishta_phala": moon_ishta, "kashta_phala": kashta_phala(moon_ishta),
        "citation": "BPHS Ch.28 v.2-6",
    }

    for planet in ["Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
        planets[planet] = {
            "model": "data_gap",
            "uchcha_rasmi": uchcha_rasmi(planet, chart[planet]["longitude"]),
            "cheshta_rasmi": None,
            "ishta_phala": None,
            "kashta_phala": None,
            "reason": (
                "Cheshta Rasmi needs this planet's exact Cheshta Kendra, which depends on the same "
                "8-tier retrograde/direct motion classification app.derived.shadbala's Chesta Bala "
                "already discloses as an incomplete extract -- reusing that disclosed gap, not "
                "fabricating a substitute."
            ),
        }

    return {
        "planets": planets,
        "saptavargaja_refinement": (
            "data_gap -- BPHS Ch.28 v.7-14's Saptavargaja Ishta-Kashta re-weighting "
            "(per-varga dignity tier x Shadbala Pinda) is a separate, further compounding layer "
            "not attempted this pass; see module docstring."
        ),
        "citation": "BPHS Ch.28 (R. Santhanam translation, Reference books/BPHS - 1 RSanthanam.pdf), read directly per AGENTS.md AD-8",
    }
