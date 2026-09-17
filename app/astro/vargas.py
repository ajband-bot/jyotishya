"""Divisional Charts (Varga) Engine — D1 through D60.

Formulas implemented here are the standard Pārāśarī divisional schemes used
across virtually all Vedic astrology software (JHora / Jagannātha Hora
convention — same lineage this project's Lahiri ayanāṁśa setup follows).

HONESTY NOTE (per AGENTS.md Cardinal Rule #2 — never fabricate):
These are the well-established *computational* rules, not independently
re-verified verse-by-verse against BPHS in this pass. Each entry in
``VARGA_META`` carries ``citation_status: "pending_audit"`` until a human
walks it against ``Reference books/BPHS - 1 RSanthanam.pdf`` chapter 6-7,
mirroring the same honesty convention already used in
``app/rules/bphs_top20_rule_cards_v1.yaml`` ("sloka_range values are
parser-estimated ... should be manually audited").

D60 in particular has genuine unresolved disagreement across classical
sources on the exact sign-assignment rule. The simple continuous-cycle
method used here is the most common software default; every D60 response
MUST carry ``birth_time_sensitivity_warning: True`` and callers must not
treat D60 claims as decisive without independent corroboration.

D40 (Khavedamsa) AND D45 (Akshavedamsa) FORMULAS VERIFIED 2026-09-16
directly against BPHS Ch.6, verses 29-32 (Santhanam translation, via
`pdftotext -layout` extraction of `Reference books/BPHS - 1 RSanthanam.pdf`
— not copied from any public-git-repos/ reference, per AD-4):
  - D40 (Chatvarimsamsa/Khavedamsa, 45' = 0.75deg per part): odd signs
    count from Aries, even signs count from Libra, cycling forward
    through all 12 signs.
  - D45 (Akshavedamsa, 40' = 0.6667deg per part): movable signs count
    from Aries, fixed signs from Leo, dual signs from Sagittarius,
    cycling forward.
These carry ``citation_status: "verified_against_bphs_ch6"`` below —
distinct from ``pending_audit`` (not yet checked) and from
``verified_by_engine`` (D1/D9, cross-checked mathematically but not via a
fresh chapter/verse read in this pass).

GENUINE FINDING — D5/D6/D8/D11 ARE NOT IN BPHS AND ARE DELIBERATELY NOT
IMPLEMENTED HERE. build_plan.md (2026-09-16 draft) assumed "all 20
divisional charts" following PyJHora's module list (which names functions
for panchamsa/D5, shashthamsa/D6, ashtamsa/D8, rudramsa/D11 in addition to
the 16 below). A full-text search of this project's actual BPHS PDF (the
AD-5 tier-1 source) for every plausible spelling of Panchamsa, Shashthamsa,
Ashtamsa, and Rudramsa — and for "fifth/sixth/eighth/eleventh part of a
sign" — returned zero matches. BPHS Ch.6 itself states explicitly "the
zodiac is divided into sixteen Vargas... from Rasi down to Shashtiamsa" —
BPHS's own Shodasavarga (16-fold) scheme is exactly the 16 divisors in
``VARGA_META`` below, no more. Per AD-4 (never copy code, cross-check
formula shape only) and AD-5 (classical hierarchy is binding, BPHS
primary), D5/D6/D8/D11 are NOT ported from PyJHora here — doing so would
silently import a non-BPHS convention as if it were classical without
labeling its actual source tier. If these four divisions are wanted, the
next step is checking Brihat Jataka / Phaladipika / Saravali (the next
tiers down per AD-5) for an independent textual basis BEFORE writing any
code — tracked as a genuine open research item, not a mechanical addition.
"""
from __future__ import annotations

from typing import Any

from app.astro.constants import SIGNS, PLANET_STATES

_ALL_PLANET_NAMES = [
    "Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn",
    "Rahu", "Ketu", "Lagna",
]

VARGA_META: dict[int, dict[str, Any]] = {
    1:  {"name": "Rasi",         "significance": "Physical body, overall life", "citation_status": "verified_by_engine"},
    2:  {"name": "Hora",         "significance": "Wealth",                      "citation_status": "pending_audit"},
    3:  {"name": "Drekkana",     "significance": "Siblings, courage",           "citation_status": "pending_audit"},
    4:  {"name": "Chaturthamsa", "significance": "Property, fortune, home",     "citation_status": "pending_audit"},
    7:  {"name": "Saptamsa",     "significance": "Children, progeny",          "citation_status": "pending_audit"},
    9:  {"name": "Navamsa",      "significance": "Spouse, dharma, D1 confirmation", "citation_status": "verified_by_engine"},
    10: {"name": "Dasamsa",      "significance": "Career, profession, public role", "citation_status": "pending_audit"},
    12: {"name": "Dwadasamsa",   "significance": "Parents, ancestry",           "citation_status": "pending_audit"},
    16: {"name": "Shodasamsa",   "significance": "Vehicles, comforts, mental peace", "citation_status": "pending_audit"},
    20: {"name": "Vimsamsa",     "significance": "Spiritual progress, worship", "citation_status": "pending_audit"},
    24: {"name": "Chaturvimsamsa", "significance": "Education, learning",       "citation_status": "pending_audit"},
    27: {"name": "Bhamsa",       "significance": "Strengths/weaknesses, general vitality (Nakshatramsa)", "citation_status": "pending_audit"},
    30: {"name": "Trimsamsa",    "significance": "Misfortunes, evils, health struggles", "citation_status": "pending_audit"},
    40: {"name": "Khavedamsa",   "significance": "General auspicious/inauspicious effects (BPHS Ch.6 v.29-30)", "citation_status": "verified_against_bphs_ch6"},
    45: {"name": "Akshavedamsa", "significance": "General character/conduct effects (BPHS Ch.6 v.31-32)", "citation_status": "verified_against_bphs_ch6"},
    60: {"name": "Shashtiamsa",  "significance": "Past-life karma, fine-grained destiny", "citation_status": "pending_audit_high_disagreement"},
}

SUPPORTED_VARGAS = tuple(sorted(VARGA_META.keys()))


def _is_odd(sign_no: int) -> bool:
    return sign_no % 2 == 1


def _quality(sign_no: int) -> str:
    return ["movable", "fixed", "dual"][(sign_no - 1) % 3]


def _element(sign_no: int) -> str:
    return ["fire", "earth", "air", "water"][(sign_no - 1) % 4]


def _offset_sign(sign_no: int, offset: int) -> int:
    return ((sign_no - 1 + offset) % 12) + 1


# ── Trimsamsa (D30) irregular degree-range table ───────────────────────────
# (start_deg, end_deg, ruling_planet, resulting_sign)
_D30_ODD = [
    (0.0, 5.0,  "Mars",    1),   # Aries
    (5.0, 10.0, "Saturn",  11),  # Aquarius
    (10.0, 18.0, "Jupiter", 9),  # Sagittarius
    (18.0, 25.0, "Mercury", 3),  # Gemini
    (25.0, 30.0, "Venus",   7),  # Libra
]
_D30_EVEN = [
    (0.0, 5.0,  "Venus",   2),   # Taurus
    (5.0, 12.0, "Mercury", 6),   # Virgo
    (12.0, 20.0, "Jupiter", 12), # Pisces
    (20.0, 25.0, "Saturn",  10), # Capricorn
    (25.0, 30.0, "Mars",    8),  # Scorpio
]


def _trimsamsa(sign_no: int, deg_in_sign: float) -> tuple[int, float, str]:
    table = _D30_ODD if _is_odd(sign_no) else _D30_EVEN
    for start, end, lord, out_sign in table:
        if start <= deg_in_sign < end or (end == 30.0 and deg_in_sign == 30.0):
            proportion = (deg_in_sign - start) / (end - start)
            return out_sign, round(proportion * 30.0, 4), lord
    # degree exactly 30.0 edge-case fallback
    start, end, lord, out_sign = table[-1]
    return out_sign, 30.0, lord


def _varga_sign_and_degree(sign_no: int, deg_in_sign: float, n: int) -> tuple[int, float]:
    """Return (resulting_sign, scaled_degree_in_resulting_sign) for divisor n."""
    if n == 1:
        return sign_no, deg_in_sign
    if n == 30:
        out_sign, scaled_deg, _lord = _trimsamsa(sign_no, deg_in_sign)
        return out_sign, scaled_deg

    part_size = 30.0 / n
    idx = min(int(deg_in_sign / part_size), n - 1)
    lon_in_part = deg_in_sign - (idx * part_size)
    scaled_deg = round((lon_in_part / part_size) * 30.0, 4)

    if n == 2:
        if _is_odd(sign_no):
            out_sign = 5 if idx == 0 else 4    # Leo (Sun) then Cancer (Moon)
        else:
            out_sign = 4 if idx == 0 else 5    # Cancer (Moon) then Leo (Sun)
        return out_sign, scaled_deg

    if n == 3:
        return _offset_sign(sign_no, [0, 4, 8][idx]), scaled_deg

    if n == 4:
        return _offset_sign(sign_no, [0, 3, 6, 9][idx]), scaled_deg

    if n == 7:
        start = sign_no if _is_odd(sign_no) else _offset_sign(sign_no, 6)
        return _offset_sign(start, idx), scaled_deg

    if n == 9:
        # Element-based start; mathematically equivalent to the global
        # formula already used in app.astro.engine.navamsha_sign().
        e = _element(sign_no)
        start = {"fire": 1, "earth": 10, "air": 7, "water": 4}[e]
        return _offset_sign(start, idx), scaled_deg

    if n == 10:
        start = sign_no if _is_odd(sign_no) else _offset_sign(sign_no, 8)
        return _offset_sign(start, idx), scaled_deg

    if n == 12:
        return _offset_sign(sign_no, idx), scaled_deg

    if n == 16:
        start = {"movable": 1, "fixed": 5, "dual": 9}[_quality(sign_no)]
        return _offset_sign(start, idx), scaled_deg

    if n == 20:
        start = {"movable": 1, "fixed": 9, "dual": 5}[_quality(sign_no)]
        return _offset_sign(start, idx), scaled_deg

    if n == 24:
        start = 5 if _is_odd(sign_no) else 4   # Leo (odd) / Cancer (even)
        return _offset_sign(start, idx), scaled_deg

    if n == 27:
        start = {"fire": 1, "earth": 4, "air": 7, "water": 10}[_element(sign_no)]
        return _offset_sign(start, idx), scaled_deg

    if n == 40:
        # BPHS Ch.6 v.29-30 (Chatvarimsamsa/Khavedamsa): odd signs count
        # from Aries, even signs count from Libra, cycling forward.
        start = 1 if _is_odd(sign_no) else 7
        return _offset_sign(start, idx), scaled_deg

    if n == 45:
        # BPHS Ch.6 v.31-32 (Akshavedamsa): movable signs count from Aries,
        # fixed signs from Leo, dual signs from Sagittarius, cycling forward.
        start = {"movable": 1, "fixed": 5, "dual": 9}[_quality(sign_no)]
        return _offset_sign(start, idx), scaled_deg

    if n == 60:
        return _offset_sign(sign_no, idx), scaled_deg

    raise ValueError(f"Unsupported varga divisor: D{n}")


def _dignity(planet: str, sign: int) -> str:
    ps = PLANET_STATES.get(planet, {})
    if sign == ps.get("exalt"):
        return "exalted"
    if sign == ps.get("debil"):
        return "debilitated"
    if sign in ps.get("own", []):
        return "own-sign"
    return "neutral"


def compute_varga(d1_chart: dict[str, Any], n: int) -> dict[str, Any]:
    """Compute a single divisional chart (Dn) from a D1 sidereal chart dict."""
    if n not in VARGA_META:
        raise ValueError(f"D{n} is not a supported varga. Supported: {SUPPORTED_VARGAS}")

    lagna_lon = d1_chart["Lagna"]["longitude"]
    lagna_sign_no = int(lagna_lon / 30) + 1
    lagna_deg = lagna_lon % 30
    varga_lagna_sign, _ = _varga_sign_and_degree(lagna_sign_no, lagna_deg, n)
    lagna_info = SIGNS[varga_lagna_sign - 1]

    planets: dict[str, Any] = {}
    for name in _ALL_PLANET_NAMES:
        p = d1_chart.get(name)
        if not p:
            continue
        lon = p["longitude"]
        sign_no = int(lon / 30) + 1
        deg_in_sign = lon % 30
        v_sign, v_deg = _varga_sign_and_degree(sign_no, deg_in_sign, n)
        v_house = ((v_sign - varga_lagna_sign) % 12) + 1
        si = SIGNS[v_sign - 1]
        planets[name] = {
            "sign": v_sign,
            "deg_in_sign": v_deg,
            "house": v_house,
            "state": _dignity(name, v_sign) if name != "Lagna" else "n/a",
            "sign_en": si["en"],
            "sign_tel": si["name"],
            "sign_lord": si["lord"],
            "retrograde": p.get("retrograde", False),
        }

    vargottama = [
        name for name in ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Lagna")
        if d1_chart.get(name, {}).get("sign") == planets.get(name, {}).get("sign")
    ]

    result = {
        "varga": n,
        "name": VARGA_META[n]["name"],
        "significance": VARGA_META[n]["significance"],
        "citation_status": VARGA_META[n]["citation_status"],
        "lagna_sign": varga_lagna_sign,
        "lagna_sign_en": lagna_info["en"],
        "lagna_sign_tel": lagna_info["name"],
        "planets": planets,
        "vargottama": vargottama,
    }
    if n == 60:
        result["birth_time_sensitivity_warning"] = True
        result["warning_note"] = (
            "D60 is extremely sensitive to birth-time accuracy (each amsa is "
            "only 0.5 degrees) and classical sources disagree on the exact "
            "sign-assignment rule. Treat any D60-only claim as low-confidence "
            "unless corroborated by other vargas/dasha/transit evidence."
        )
    return result


def compute_all_vargas(d1_chart: dict[str, Any], divisors: tuple[int, ...] = SUPPORTED_VARGAS) -> dict[str, Any]:
    """Compute every requested divisional chart in one pass."""
    return {f"D{n}": compute_varga(d1_chart, n) for n in divisors}
