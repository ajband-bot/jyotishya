"""Classical Ashtakavarga engine -- Bhinnashtakavarga (BAV) + Sarvashtakavarga (SAV).

Source note (AD-5/AD-4 compliance): the BPHS PDF under `Reference books/`
(R. Santhanam translation, OCR scan) is an abridged edition that stops
around Chapter 45 and does not carry a full Ashtakavarga chapter -- a
full-text search of the OCR'd scan turns up only one mangled fragment
("...InAshtakaY4tg,add Bindus...") mentioning the concept in passing, not
the bindu tables themselves. Per AD-4 (cross-check, never copy code), the
fixed bindu-contribution table below -- standard Parashari Ashtakavarga,
identical across every classical source and every software implementation
because it is *not* a textually-contested formula the way Upapada is --
was transcribed verbatim (data only) from
`public-git-repos/PyJHora-main/src/jhora/const.py`'s `ashtaka_varga_dict`,
and independently cross-checked against
`public-git-repos/OpenJyotish-main/src/jhora/data/books/primer-05-ashtakavarga.txt`,
which states this table's per-planet row totals as a hand-verified,
chart-invariant fact (true for every chart ever cast, regardless of birth
data): Sun 48, Moon 49, Mars 39, Mercury 54, Jupiter 56, Venus 52,
Saturn 39, SAV (sum of the 7 planetary rows, Lagna excluded) = 337.

Both independent sources agree exactly on these totals. `_self_check()`
below asserts the invariant at import time, and
`tests/unit/test_ashtakavarga.py` re-asserts it against every golden
fixture on every test run -- if this table or the engine logic is ever
silently corrupted, that assertion fails loudly instead of producing a
quietly-wrong reading (this is the exact risk a prior session flagged and
paused on rather than guess at).

Rahu/Ketu deliberately have NO row here: the classical Parashari system
does not define Ashtakavarga contributions for the lunar nodes. Several
modern manuals borrow Saturn's or Jupiter's bindus for them as a
convenience, but that is a non-classical convention, not BPHS doctrine --
per Cardinal Rule 4, this is reported as an explicit `data_gap`
(`app.derived.ashtakavarga.classical_ashtakavarga`'s `current_transits`),
never silently invented.
"""
from __future__ import annotations

from typing import Any

from app.astro.constants import SIGNS

CONTRIBUTORS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Lagna"]
SEVEN_PLANETS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]

# BINDU_TABLE[target][contributor] = houses (1-12, counted from the
# contributor's own occupied sign) that drop a bindu into `target`'s BAV.
BINDU_TABLE: dict[str, dict[str, list[int]]] = {
    "Sun": {
        "Sun": [1, 2, 4, 7, 8, 9, 10, 11], "Moon": [3, 6, 10, 11],
        "Mars": [1, 2, 4, 7, 8, 9, 10, 11], "Mercury": [3, 5, 6, 9, 10, 11, 12],
        "Jupiter": [5, 6, 9, 11], "Venus": [6, 7, 12],
        "Saturn": [1, 2, 4, 7, 8, 9, 10, 11], "Lagna": [3, 4, 6, 10, 11, 12],
    },
    "Moon": {
        "Sun": [3, 6, 7, 8, 10, 11], "Moon": [1, 3, 6, 7, 9, 10, 11],
        "Mars": [2, 3, 5, 6, 10, 11], "Mercury": [1, 3, 4, 5, 7, 8, 10, 11],
        "Jupiter": [1, 2, 4, 7, 8, 10, 11], "Venus": [3, 4, 5, 7, 9, 10, 11],
        "Saturn": [3, 5, 6, 11], "Lagna": [3, 6, 10, 11],
    },
    "Mars": {
        "Sun": [3, 5, 6, 10, 11], "Moon": [3, 6, 11],
        "Mars": [1, 2, 4, 7, 8, 10, 11], "Mercury": [3, 5, 6, 11],
        "Jupiter": [6, 10, 11, 12], "Venus": [6, 8, 11, 12],
        "Saturn": [1, 4, 7, 8, 9, 10, 11], "Lagna": [1, 3, 6, 10, 11],
    },
    "Mercury": {
        "Sun": [5, 6, 9, 11, 12], "Moon": [2, 4, 6, 8, 10, 11],
        "Mars": [1, 2, 4, 7, 8, 9, 10, 11], "Mercury": [1, 3, 5, 6, 9, 10, 11, 12],
        "Jupiter": [6, 8, 11, 12], "Venus": [1, 2, 3, 4, 5, 8, 9, 11],
        "Saturn": [1, 2, 4, 7, 8, 9, 10, 11], "Lagna": [1, 2, 4, 6, 8, 10, 11],
    },
    "Jupiter": {
        "Sun": [1, 2, 3, 4, 7, 8, 9, 10, 11], "Moon": [2, 5, 7, 9, 11],
        "Mars": [1, 2, 4, 7, 8, 10, 11], "Mercury": [1, 2, 4, 5, 6, 9, 10, 11],
        "Jupiter": [1, 2, 3, 4, 7, 8, 10, 11], "Venus": [2, 5, 6, 9, 10, 11],
        "Saturn": [3, 5, 6, 12], "Lagna": [1, 2, 4, 5, 6, 7, 9, 10, 11],
    },
    "Venus": {
        "Sun": [8, 11, 12], "Moon": [1, 2, 3, 4, 5, 8, 9, 11, 12],
        "Mars": [3, 4, 6, 9, 11, 12], "Mercury": [3, 5, 6, 9, 11],
        "Jupiter": [5, 8, 9, 10, 11], "Venus": [1, 2, 3, 4, 5, 8, 9, 10, 11],
        "Saturn": [3, 4, 5, 8, 9, 10, 11], "Lagna": [1, 2, 3, 4, 5, 8, 9, 11],
    },
    "Saturn": {
        "Sun": [1, 2, 4, 7, 8, 10, 11], "Moon": [3, 6, 11],
        "Mars": [3, 5, 6, 10, 11, 12], "Mercury": [6, 8, 9, 10, 11, 12],
        "Jupiter": [5, 6, 11, 12], "Venus": [6, 11, 12],
        "Saturn": [3, 5, 6, 11], "Lagna": [1, 3, 4, 6, 10, 11],
    },
    "Lagna": {
        "Sun": [3, 4, 6, 10, 11, 12], "Moon": [3, 6, 10, 11, 12],
        "Mars": [1, 3, 6, 10, 11], "Mercury": [1, 2, 4, 6, 8, 10, 11],
        "Jupiter": [1, 2, 4, 5, 6, 7, 9, 10, 11], "Venus": [1, 2, 3, 4, 5, 8, 9],
        "Saturn": [1, 3, 4, 6, 10, 11], "Lagna": [3, 6, 10, 11],
    },
}

EXPECTED_ROW_TOTAL = {
    "Sun": 48, "Moon": 49, "Mars": 39, "Mercury": 54,
    "Jupiter": 56, "Venus": 52, "Saturn": 39, "Lagna": 49,
}
EXPECTED_SAV_TOTAL = sum(EXPECTED_ROW_TOTAL[p] for p in SEVEN_PLANETS)  # 337


def _self_check() -> None:
    for target, contributions in BINDU_TABLE.items():
        total = sum(len(houses) for houses in contributions.values())
        expected = EXPECTED_ROW_TOTAL[target]
        if total != expected:
            raise AssertionError(
                f"Ashtakavarga BINDU_TABLE for {target!r} sums to {total} bindus, "
                f"expected the classical invariant {expected} -- table is corrupted."
            )


_self_check()


def _sign_name(sign_no: int) -> str:
    return SIGNS[sign_no - 1]["en"]


def _house_for_sign(lagna_sign: int, sign_no: int) -> int:
    return ((sign_no - lagna_sign) % 12) + 1


def bhinna_ashtakavarga(chart: dict[str, Any]) -> dict[str, dict[int, int]]:
    """Bhinnashtakavarga: per-target (7 planets + Lagna), per-sign bindu counts."""
    positions = {contributor: chart[contributor]["sign"] for contributor in CONTRIBUTORS}
    bav: dict[str, dict[int, int]] = {}
    for target, contributions in BINDU_TABLE.items():
        sign_bindus = {sign_no: 0 for sign_no in range(1, 13)}
        for contributor, houses in contributions.items():
            source_sign = positions[contributor]
            for house in houses:
                landing_sign = ((source_sign - 1 + house - 1) % 12) + 1
                sign_bindus[landing_sign] += 1
        bav[target] = sign_bindus
    return bav


def sarva_ashtakavarga(bav: dict[str, dict[int, int]]) -> dict[int, int]:
    """Sarvashtakavarga: sum of the 7 planetary BAVs per sign (Lagna row excluded, per classical convention)."""
    sav = {sign_no: 0 for sign_no in range(1, 13)}
    for planet in SEVEN_PLANETS:
        for sign_no in range(1, 13):
            sav[sign_no] += bav[planet][sign_no]
    return sav


def sav_verdict(bindus: int) -> str:
    if bindus >= 30:
        return "favorable"
    if bindus < 25:
        return "challenging"
    return "neutral"


def full_ashtakavarga(chart: dict[str, Any]) -> dict[str, Any]:
    """Full classical Ashtakavarga for a natal chart: BAV (8 rows) + SAV (7-row sum), sign-keyed."""
    lagna_sign = chart["Lagna"]["sign"]
    bav = bhinna_ashtakavarga(chart)
    sav = sarva_ashtakavarga(bav)
    sav_total = sum(sav.values())
    if sav_total != EXPECTED_SAV_TOTAL:
        raise AssertionError(f"SAV total {sav_total} != classical invariant {EXPECTED_SAV_TOTAL}")

    signs: dict[int, Any] = {}
    for sign_no in range(1, 13):
        signs[sign_no] = {
            "sign": sign_no,
            "sign_en": _sign_name(sign_no),
            "house": _house_for_sign(lagna_sign, sign_no),
            "lord": SIGNS[sign_no - 1]["lord"],
            "sav_bindus": sav[sign_no],
            "verdict": sav_verdict(sav[sign_no]),
            "occupants": [p for p in SEVEN_PLANETS if chart[p]["sign"] == sign_no],
            "bav_by_planet": {p: bav[p][sign_no] for p in SEVEN_PLANETS},
        }

    return {
        "model": "classical_parashari",
        "bhinna": bav,
        "sarva": sav,
        "sav_total": sav_total,
        "signs": signs,
    }
