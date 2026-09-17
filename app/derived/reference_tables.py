"""Reference Tables -- the always-on "fundamentals" layer for the
Learning/Cheat-Sheet tab (spec 7.1 Functional Nature Heat Map, 7.2 House
Theme Explorer, 7.3 Lord Placement Matrix, plus classical dignity +
friend/enemy tables).

Unlike everything else in app/derived/, these are LAGNA-GENERIC or
chart-INDEPENDENT: they describe the fixed classical doctrine every chart
is read against, not one specific person's placements. This is exactly the
reference material Ajay asked for: "house ownerships, lagna malefics versus
benefics, house themes, connections based on lords of different houses,
enemies, friends, exalted, debilitated etc."
"""
from __future__ import annotations

from typing import Any

from app.astro.constants import PLANET_STATES, SIGNS, DASHA_ORDER, DASHA_YEARS, TOTAL_DASHA_YEARS
from app.derived.factors import house_lord, is_yoga_karaka

KENDRA = {1, 4, 7, 10}
TRIKONA = {1, 5, 9}
DUSTHANA = {6, 8, 12}
UPACHAYA = {3, 6, 10, 11}
MARAKA_HOUSES = {2, 7}

ALL_PLANETS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]

NATURAL_BENEFICS = {"Moon", "Mercury", "Jupiter", "Venus"}
NATURAL_MALEFICS = {"Sun", "Mars", "Saturn", "Rahu", "Ketu"}

# Verified, verbatim-sourced from app/rules/bphs_top20_rule_cards_v1.yaml
# (meta.graha_condition_policy.sub_factors.natural_relationship.table).
# Kept as a plain constant here (rather than re-parsing the 115KB YAML at
# request time) with a regression test asserting the two stay in sync.
NATURAL_RELATIONSHIPS: dict[str, dict[str, list[str]]] = {
    "Sun":     {"friends": ["Moon", "Mars", "Jupiter"], "neutral": ["Mercury"], "enemies": ["Venus", "Saturn"]},
    "Moon":    {"friends": ["Sun", "Mercury"], "neutral": ["Mars", "Jupiter", "Venus", "Saturn"], "enemies": []},
    "Mars":    {"friends": ["Sun", "Moon", "Jupiter"], "neutral": ["Venus", "Saturn"], "enemies": ["Mercury"]},
    "Mercury": {"friends": ["Sun", "Venus"], "neutral": ["Mars", "Jupiter", "Saturn"], "enemies": ["Moon"]},
    "Jupiter": {"friends": ["Sun", "Moon", "Mars"], "neutral": ["Saturn"], "enemies": ["Mercury", "Venus"]},
    "Venus":   {"friends": ["Mercury", "Saturn"], "neutral": ["Mars", "Jupiter"], "enemies": ["Sun", "Moon"]},
    "Saturn":  {"friends": ["Mercury", "Venus"], "neutral": ["Jupiter"], "enemies": ["Sun", "Moon", "Mars"]},
}

# House theme layers per spec 7.2 (Core / Material / Higher). Telugu names +
# karakas already exist in app.knowledge.houses.HOUSES -- this adds the
# spec's three-layer semantic breakdown as a distinct, additive dataset.
HOUSE_THEMES: dict[int, dict[str, str]] = {
    1:  {"core": "Self", "material": "Body, identity, vitality", "higher": "Incarnation"},
    2:  {"core": "Accumulation", "material": "Wealth, family, speech", "higher": "Values"},
    3:  {"core": "Effort", "material": "Skill, courage, communication", "higher": "Initiative"},
    4:  {"core": "Foundation", "material": "Home, property, mother, education", "higher": "Sukha (inner contentment)"},
    5:  {"core": "Intelligence", "material": "Children, creativity, learning", "higher": "Purva-punya / mantra"},
    6:  {"core": "Conflict/Service", "material": "Work, competition, disease, debt", "higher": "Overcoming"},
    7:  {"core": "Other", "material": "Spouse, partnerships, contracts", "higher": "Relational mirror"},
    8:  {"core": "Hidden Transformation", "material": "Joint resources, crisis, inheritance", "higher": "Transformation"},
    9:  {"core": "Dharma", "material": "Guru, father, fortune, higher learning", "higher": "Grace"},
    10: {"core": "Karma", "material": "Profession, authority, public role", "higher": "Action"},
    11: {"core": "Realisation", "material": "Gains, network, fulfilment", "higher": "Results"},
    12: {"core": "Release", "material": "Expenditure, foreign, isolation", "higher": "Moksha"},
}

# Moolatrikona sign + degree range per planet (BPHS Ch.3). Distinct from
# "own sign" -- Moolatrikona is a specific degree-band within one of the
# planet's own/exalt-adjacent signs. NOTE: pending_audit -- not yet
# independently re-verified verse-by-verse in this codebase; follows the
# widely-used software convention (same lineage as JHora/Lahiri setup this
# project already uses).
MOOLATRIKONA: dict[str, dict[str, Any]] = {
    "Sun":     {"sign": 5, "range": (0, 20), "citation_status": "pending_audit"},
    "Moon":    {"sign": 2, "range": (3, 30), "citation_status": "pending_audit"},
    "Mars":    {"sign": 1, "range": (0, 12), "citation_status": "pending_audit"},
    "Mercury": {"sign": 6, "range": (15, 20), "citation_status": "pending_audit"},
    "Jupiter": {"sign": 9, "range": (0, 10), "citation_status": "pending_audit"},
    "Venus":   {"sign": 7, "range": (0, 15), "citation_status": "pending_audit"},
    "Saturn":  {"sign": 11, "range": (0, 20), "citation_status": "pending_audit"},
}


def get_house_themes() -> dict[int, dict[str, Any]]:
    """House Theme Explorer data (spec 7.2)."""
    from app.knowledge.houses import HOUSES

    out = {}
    for house_no in range(1, 13):
        base = HOUSES[house_no]
        themes = HOUSE_THEMES[house_no]
        out[house_no] = {
            "house": house_no,
            "name_en": base["en"],
            "name_tel": base["name"],
            "karakas": base["karakas"],
            "nature": (
                "trikona" if house_no in TRIKONA else
                "kendra" if house_no in KENDRA else
                "dusthana" if house_no in DUSTHANA else
                "upachaya" if house_no in UPACHAYA else "neutral"
            ),
            "is_maraka_house": house_no in MARAKA_HOUSES,
            "core": themes["core"],
            "material": themes["material"],
            "higher": themes["higher"],
        }
    return out


def get_natural_relationships() -> dict[str, Any]:
    """Friend/Enemy/Neutral table (spec, planet-relationship layer)."""
    return {
        "table": NATURAL_RELATIONSHIPS,
        "source": "BPHS Ch.3 -- verified against app/rules/bphs_top20_rule_cards_v1.yaml graha_condition_policy",
        "citation_status": "verified",
    }


def get_dignity_table() -> dict[str, Any]:
    """Exaltation / Debilitation / Own-sign / Moolatrikona reference (spec dignity layer)."""
    out = {}
    for planet in ALL_PLANETS:
        ps = PLANET_STATES[planet]
        mt = MOOLATRIKONA[planet]
        out[planet] = {
            "exalted_sign": SIGNS[ps["exalt"] - 1]["en"],
            "exalted_degree": ps["exalt_deg"],
            "debilitated_sign": SIGNS[ps["debil"] - 1]["en"],
            "own_signs": [SIGNS[s - 1]["en"] for s in ps["own"]],
            "moolatrikona_sign": SIGNS[mt["sign"] - 1]["en"],
            "moolatrikona_range_deg": mt["range"],
            "moolatrikona_citation_status": mt["citation_status"],
        }
    return out


def _classify_cell(lagna_sign: int, planet: str) -> dict[str, Any]:
    """Functional Nature Heat Map cell (spec 7.1) for one (Lagna, Planet) pair."""
    owned = [h for h in range(1, 13) if house_lord(lagna_sign, h) == planet]
    is_lagna_lord = 1 in owned
    yoga_karaka = is_yoga_karaka(lagna_sign, planet)
    owns_dusthana = any(h in DUSTHANA for h in owned)
    owns_maraka = any(h in MARAKA_HOUSES for h in owned)
    owns_trikona_only = any(h in TRIKONA for h in owned) and not any(h in KENDRA - TRIKONA for h in owned)
    owns_kendra_only = any(h in KENDRA for h in owned) and not any(h in TRIKONA for h in owned)

    if yoga_karaka:
        tag, classification = "YK", "yogakaraka"
    elif is_lagna_lord and owns_dusthana:
        tag, classification = "0", "mixed (lagna lord + dusthana lord)"
    elif owns_dusthana and not is_lagna_lord:
        tag, classification = "--", "strongly_adverse"
    elif owns_maraka:
        tag, classification = "M", "maraka_tendency"
    elif is_lagna_lord:
        tag, classification = "LL", "lagna_lord"
    elif owns_trikona_only:
        tag, classification = "++", "strong_functional_benefic"
    elif owns_kendra_only and planet in NATURAL_BENEFICS:
        tag, classification = "0", "neutral (kendradhipati dosha)"
    elif owns_kendra_only:
        tag, classification = "+", "functional_benefic"
    else:
        tag, classification = "0", "neutral_mixed"

    return {
        "houses_owned": owned,
        "tag": tag,
        "classification": classification,
        "is_lagna_lord": is_lagna_lord,
        "is_yoga_karaka": yoga_karaka,
        "natural_nature": "benefic" if planet in NATURAL_BENEFICS else "malefic",
    }


def get_functional_nature_grid() -> dict[str, Any]:
    """Full 12-Lagna x 7-planet Functional Nature Heat Map (spec 7.1).

    This is lagna-generic -- it answers "for EVERY possible Lagna, what is
    each planet's functional role" -- not tied to any one person's chart.
    """
    grid: dict[int, dict[str, Any]] = {}
    for lagna_sign in range(1, 13):
        grid[lagna_sign] = {
            "lagna_sign_en": SIGNS[lagna_sign - 1]["en"],
            "planets": {planet: _classify_cell(lagna_sign, planet) for planet in ALL_PLANETS},
        }
    return {
        "grid": grid,
        "legend": {
            "YK": "Yogakaraka",
            "++": "Strong functional benefic",
            "+": "Functional benefic",
            "0": "Neutral / mixed",
            "-": "Adverse",
            "--": "Strongly adverse",
            "M": "Maraka tendency",
            "LL": "Lagna lord",
        },
        "disclaimer": "Functional Nature only -- this is NOT planet strength (spec 7.1).",
    }


def house_connection_text(source_house: int, dest_house: int, themes: dict[int, Any] | None = None) -> dict[str, Any]:
    """Shared theme-bridge text generator: 'source house theme -> dest
    house theme', reused by both the LAGNA-GENERIC Lord Placement Matrix
    (get_lord_placement_connections) and the chart-SPECIFIC Chart Lab
    sandbox house-connections (app/derived/sandbox.py) -- one true
    connection-text formula, never duplicated.
    """
    themes = themes or get_house_themes()
    src_theme = themes[source_house]["core"]
    dest_theme = themes[dest_house]["core"]
    return {
        "connection": f"{src_theme} -> {dest_theme}",
        "dest_nature": themes[dest_house]["nature"],
    }


def get_lord_placement_connections(lagna_sign: int) -> dict[str, Any]:
    """Lord Placement Matrix for one Lagna (spec 7.3) -- 12x12: for each
    house-lord (1-12), which house is it placed in (by default/mean
    sign-distance from that lord's own house), and what thematic connection
    does that create.

    This is NOT chart-specific placement (that depends on a real birth
    chart) -- it is the STRUCTURAL lord-to-house theme connection template:
    "if the Nth lord ends up in the Mth house, here is the thematic bridge."
    Rows = source house (whose lord we're tracing), columns = every
    possible destination house that lord could occupy.
    """
    themes = get_house_themes()
    matrix: dict[int, dict[int, dict[str, Any]]] = {}
    for source_house in range(1, 13):
        lord = house_lord(lagna_sign, source_house)
        matrix[source_house] = {"lord": lord, "destinations": {}}
        for dest_house in range(1, 13):
            matrix[source_house]["destinations"][dest_house] = house_connection_text(source_house, dest_house, themes)
    return {
        "lagna_sign": lagna_sign,
        "lagna_sign_en": SIGNS[lagna_sign - 1]["en"],
        "matrix": matrix,
        "note": (
            "Connections are structural theme-bridges (Nth-house-theme -> "
            "Mth-house-theme), generated mechanically from house themes -- "
            "not individually hand-authored classical citations. Treat as "
            "an application heuristic (source_tier 5) for teaching the "
            "Ownership -> Placement -> Connection mental grammar, not as a "
            "verbatim scriptural quote."
        ),
    }


# --------------------------------------------------------------------------
# Chart-SPECIFIC layer (Planet Lab) -- reads one real chart's context (from
# build_chart_context) and reuses _classify_cell, joined with already-
# computed strength/dignity/combustion data. No new astrology math here --
# purely a transparency/assembly layer over existing derived signals.
# --------------------------------------------------------------------------

NODES = ["Rahu", "Ketu"]


def get_planet_lab(ctx: dict[str, Any]) -> dict[str, Any]:
    """One transparent profile per graha: sign/house/dignity/combustion/
    D9-state/functional-role/Shadbala breakdown/Ishta-Kashta verdict, all
    pulled from the SAME computed context every other screen uses (so this
    can never drift from the truth layer)."""
    chart = ctx["chart"]
    d9 = ctx["d9"]["planets"]
    lagna_sign = ctx["lagna_sign"]
    shadbala = ctx["shadbala"]
    ishta_kashta = ctx["ishta_kashta"]
    combustion = ctx["combustion"]
    aspect_map = ctx["aspect_map"]

    profiles: dict[str, Any] = {}
    for planet in ALL_PLANETS + NODES:
        pos = chart[planet]
        if planet in ALL_PLANETS:
            cell = _classify_cell(lagna_sign, planet)
        else:
            cell = {
                "tag": "N/A", "classification": "node_no_house_ownership",
                "houses_owned": [], "is_lagna_lord": False, "is_yoga_karaka": False,
                "natural_nature": "malefic",
            }
        received_from = [
            other for other, hits in aspect_map.items()
            if other != planet and pos["house"] in hits
        ]
        profiles[planet] = {
            "sign_en": SIGNS[pos["sign"] - 1]["en"],
            "deg_in_sign": pos["deg_in_sign"],
            "house": pos["house"],
            "retrograde": pos["retrograde"],
            "functional": cell,
            "combust": combustion.get(planet, {}).get("combust", False),
            "combustion_orb_deg": combustion.get(planet, {}).get("diff"),
            "d9_sign_en": SIGNS[d9[planet]["sign"] - 1]["en"],
            "d9_state": d9[planet]["state"],
            "vargottama": pos["sign"] == d9[planet]["sign"],
            "shadbala": shadbala[planet],
            "ishta_kashta": ishta_kashta[planet],
            "aspected_by": received_from,
        }
    return {"lagna_sign": lagna_sign, "planets": profiles}


def get_dasha_reference() -> dict[str, Any]:
    """Fixed Vimsottari cycle + full Antardasha AND Pratyantardasha duration
    tables for every Mahadasha planet, computed by proportion only (BPHS
    Ch.46 formula). No calendar dates -- doctrine reference, not a
    person's timeline."""
    sequence = [{"planet": p, "years": DASHA_YEARS[p]} for p in DASHA_ORDER]
    antardasha_tables = {}
    pratyantardasha_tables: dict[str, dict[str, list[dict[str, Any]]]] = {}
    for md_planet in DASHA_ORDER:
        md_years = DASHA_YEARS[md_planet]
        md_start_idx = DASHA_ORDER.index(md_planet)
        rows = []
        pratyantardasha_tables[md_planet] = {}
        for i in range(9):
            ad_planet = DASHA_ORDER[(md_start_idx + i) % 9]
            ad_years = round((DASHA_YEARS[ad_planet] / TOTAL_DASHA_YEARS) * md_years, 4)
            rows.append({"planet": ad_planet, "years": ad_years, "months": round(ad_years * 12, 2)})

            ad_start_idx = DASHA_ORDER.index(ad_planet)
            pd_rows = []
            for j in range(9):
                pd_planet = DASHA_ORDER[(ad_start_idx + j) % 9]
                pd_years = round((DASHA_YEARS[pd_planet] / TOTAL_DASHA_YEARS) * ad_years, 5)
                pd_days = round(pd_years * 365.25, 1)
                pd_rows.append({"planet": pd_planet, "years": pd_years, "days": pd_days})
            pratyantardasha_tables[md_planet][ad_planet] = pd_rows
        antardasha_tables[md_planet] = rows
    return {
        "sequence": sequence,
        "total_years": TOTAL_DASHA_YEARS,
        "antardasha_tables": antardasha_tables,
        "pratyantardasha_tables": pratyantardasha_tables,
        "pratyantardasha_formula": "PD_years = (PD_lord_years / 120) * AD_years -- sequence starts from the AD lord",
        "citation": "BPHS Ch.46 (Vimsottari Dasha)",
        "note": "Order and years are fixed. Only the STARTING planet and elapsed-fraction offset are chart-specific.",
    }


_JUPITER_TRANSIT_BLURBS = {
    1: "Vitality and visibility rise; can also mean weight or health shifts.",
    2: "Financial and family growth; speech becomes more persuasive.",
    3: "Auspicious for siblings, courage, and short-distance efforts.",
    4: "Challenging for domestic peace and mother's health; property needs care.",
    5: "Excellent for children, learning, creative and speculative gains.",
    6: "Testing house -- can bring health or legal friction despite Jupiter's benevolence.",
    7: "Strong for partnerships and marriage-related developments.",
    8: "Sensitive transit -- transformation, inheritance, or health caution.",
    9: "One of the most auspicious transits -- fortune, dharma, higher learning.",
    10: "Career growth, recognition, authority expansion.",
    11: "Gains, fulfilment of desires, expanding social network.",
    12: "Introspective and expense-heavy; favors spiritual withdrawal over material push.",
}

_SATURN_TRANSIT_BLURBS = {
    1: "Sade Sati Phase 2 (Peak) -- maximum intensity, transformation of self-identity.",
    2: "Sade Sati Phase 3 (Setting) -- financial and family adjustment, resolution phase.",
    3: "Generally supportive -- discipline channelled into effort and courage pays off.",
    4: "Kantaka friction point -- domestic and property pressure, patience needed.",
    5: "Tests creative and intellectual confidence; slow but stabilizing for children matters.",
    6: "One of Saturn's best transits -- discipline defeats obstacles, service-oriented gains.",
    7: "Kantaka -- partnership and health need sustained patience, not haste.",
    8: "Often the most difficult -- longevity caution, hidden stress, avoid major risk-taking.",
    9: "Tests faith and father figures, but rewards long-term discipline in dharma.",
    10: "Kantaka but also Saturn's natural strength house -- hard work now compounds later.",
    11: "Strong for slow-but-permanent material gains.",
    12: "Sade Sati Phase 1 (Rising) -- financial pressure, quiet preparation phase.",
}


def get_transit_reference() -> dict[str, Any]:
    """Classical Gochara doctrine for Jupiter/Saturn from Moon -- reuses
    the exact house sets app.astro.transits already computes with, so this
    reference and the live engine can never silently disagree."""
    from app.astro.transits import (
        JUPITER_AUSPICIOUS_FROM_MOON,
        JUPITER_CHALLENGING_FROM_MOON,
        SATURN_KANTAKA,
        SATURN_SADE_SATI,
    )

    jupiter_houses = {}
    for house in range(1, 13):
        if house in JUPITER_AUSPICIOUS_FROM_MOON:
            quality = "auspicious"
        elif house in JUPITER_CHALLENGING_FROM_MOON:
            quality = "challenging"
        else:
            quality = "mixed"
        jupiter_houses[house] = {"quality": quality, "effect": _JUPITER_TRANSIT_BLURBS[house]}

    saturn_houses = {}
    for house in range(1, 13):
        if house in SATURN_SADE_SATI:
            quality = "sade_sati"
        elif house in SATURN_KANTAKA:
            quality = "kantaka"
        else:
            quality = "neutral"
        saturn_houses[house] = {"quality": quality, "effect": _SATURN_TRANSIT_BLURBS[house]}

    return {
        "jupiter_from_moon": jupiter_houses,
        "saturn_from_moon": saturn_houses,
        "sade_sati_phases": [
            {"phase": 1, "label": "Rising", "house_from_moon": 12, "duration_years": 2.5},
            {"phase": 2, "label": "Peak", "house_from_moon": 1, "duration_years": 2.5},
            {"phase": 3, "label": "Setting", "house_from_moon": 2, "duration_years": 2.5},
        ],
        "citation": "Sarvartha Cintamani (primary transit-methodology authority per AGENTS.md 7)",
    }


def get_top_rules() -> dict[str, Any]:
    """Structured view of every rule card in bphs_top20_rule_cards_v1.yaml
    -- id, name, chapter, canonical statement, why it matters, citations,
    worked examples. Honestly labeled as 20-of-30 (the corpus's own name)."""
    from app.rules.loader import load_rule_pack

    pack = load_rule_pack()
    cards = pack.get("rule_cards", [])
    by_domain: dict[str, list[str]] = {}
    rules = []
    for card in cards:
        fields = card.get("card_fields", {})
        rule_id = card.get("rule_id", "UNKNOWN")
        domains = card.get("domain_tags", ["uncategorized"])
        for d in domains:
            by_domain.setdefault(d, []).append(rule_id)
        rules.append({
            "rule_id": rule_id,
            "priority": card.get("priority"),
            "name": card.get("rule_name"),
            "authority_tier": card.get("authority_tier"),
            "chapter_signal": card.get("chapter_signal"),
            "domain_tags": domains,
            "why_it_matters": card.get("why_top20"),
            "canonical_statement": fields.get("canonical_statement"),
            "activation_conditions": fields.get("activation_conditions", []),
            "exclusions": fields.get("exclusions", []),
            "examples": fields.get("examples", []),
            "citations": fields.get("citations", []),
            "citation_status": card.get("citation_status"),
        })
    fallback_priority = 999
    rules_sorted = sorted(rules, key=lambda r: r["priority"] if r["priority"] is not None else fallback_priority)
    coverage_note = str(len(rules)) + " of a planned 30 top rules are structured so far -- the rest are a documented backlog item, not silently treated as complete."
    return {
        "total_rules": len(rules),
        "target_total": 30,
        "coverage_note": coverage_note,
        "rules": rules_sorted,
        "by_domain": by_domain,
    }


def get_planet_relationship_graph() -> dict[str, Any]:
    """Nodes + edges for a graphical (React Flow style) rendering of
    NATURAL_RELATIONSHIPS -- same source data as get_natural_relationships(),
    reshaped for a graph instead of a table."""
    nodes = [{"id": p, "label": p} for p in ALL_PLANETS]
    edges = []
    seen = set()
    for planet, rel in NATURAL_RELATIONSHIPS.items():
        for other in rel["friends"]:
            key = tuple(sorted([planet, other]))
            if key not in seen:
                edges.append({"source": planet, "target": other, "kind": "friend"})
                seen.add(key)
        for other in rel["enemies"]:
            key = tuple(sorted([planet, other]))
            if key not in seen:
                edges.append({"source": planet, "target": other, "kind": "enemy"})
                seen.add(key)
    return {"nodes": nodes, "edges": edges}
