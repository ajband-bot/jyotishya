"""House Connection Graph -- a core computed artifact (build_plan.md Phase 2
item 3), not a side-effect of narrative prose.

BPHS's own method of judging a house (Ch.11 v.1-8, and the "bhava chakra"
tradition generally) is relational, not isolated: a house is strengthened
or weakened by (a) where its lord sits, (b) who occupies it, and (c) who
aspects it. Every existing engine already computes these three primitives
separately (`house_lord()`, chart occupation, `graha_drishti_houses()`) --
this module is the first place they are assembled into one explicit graph
object, so downstream engines (dispositor chains, lord-placement rules, the
Event Agreement Engine) can consume a single, DRY structure instead of each
re-deriving house connectivity by hand.

VARGA-AWARE: every function takes `lagna_sign` + a plain `{planet: house}`
mapping (never a raw chart dict), exactly like `app.derived.aspects`, so the
same graph builder runs unmodified on D1 or any `compute_varga()` output.
"""
from __future__ import annotations

from typing import Any

from app.derived.aspects import build_aspect_map, graha_drishti_houses

ALL_PLANETS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]


def house_lords_for_lagna(lagna_sign: int, sign_lord_fn) -> dict[int, str]:
    """Build the {house_no: lord_planet} map for a given lagna sign.

    `sign_lord_fn` is injected (rather than imported) to avoid a circular
    import with app.derived.factors, which already owns `house_lord()`.
    """
    return {house: sign_lord_fn(lagna_sign, house) for house in range(1, 13)}


def _occupants(planet_houses: dict[str, int]) -> dict[int, list[str]]:
    occupants: dict[int, list[str]] = {house: [] for house in range(1, 13)}
    for planet, house in planet_houses.items():
        if planet in ALL_PLANETS:
            occupants[house].append(planet)
    return occupants


def build_house_connection_graph(
    house_lords: dict[int, str],
    planet_houses: dict[str, int],
) -> dict[str, Any]:
    """Assemble the full house connection graph for one chart (D1 or varga).

    Three edge types, kept explicitly separate (Cardinal Rule 3 -- distinct
    classical mechanisms are never blended into one undifferentiated "is
    connected" boolean):

      lordship_edges     -- house X -> the house its own lord currently
                             occupies (12 edges, always exactly one per
                             house; BPHS's primary connectivity test).
      conjunction_edges   -- house X <-> house Y where X's lord and Y's lord
                             sit together in the same house (a stronger,
                             mutual signal than either lordship edge alone).
      aspect_edges        -- house X -> house Y where X's lord graha-drishti
                             aspects the house Y occupies from wherever that
                             lord currently sits.

    `adjacency` folds all three into a single per-house list for graph
    traversal, each entry still tagged with its edge type -- never
    collapsed to an untyped adjacency list.
    """
    occupants = _occupants(planet_houses)

    lordship_edges = []
    for house in range(1, 13):
        lord = house_lords[house]
        lord_house = planet_houses.get(lord)
        if lord_house is not None:
            lordship_edges.append({"from_house": house, "to_house": lord_house, "lord": lord})

    lord_house_of = {edge["from_house"]: edge["to_house"] for edge in lordship_edges}
    lord_of_house = {edge["from_house"]: edge["lord"] for edge in lordship_edges}

    conjunction_edges = []
    seen_pairs: set[tuple[int, int]] = set()
    for house_a in range(1, 13):
        for house_b in range(house_a + 1, 13):
            loc_a = lord_house_of.get(house_a)
            loc_b = lord_house_of.get(house_b)
            if loc_a is not None and loc_a == loc_b:
                pair = (house_a, house_b)
                if pair not in seen_pairs:
                    seen_pairs.add(pair)
                    conjunction_edges.append({
                        "house_a": house_a, "house_b": house_b,
                        "lord_a": lord_of_house[house_a], "lord_b": lord_of_house[house_b],
                        "meeting_house": loc_a,
                    })

    aspect_edges = []
    for house in range(1, 13):
        lord = lord_of_house.get(house)
        lord_house = lord_house_of.get(house)
        if lord is None or lord_house is None:
            continue
        for aspected_house in graha_drishti_houses(lord, lord_house):
            aspect_edges.append({"from_house": house, "to_house": aspected_house, "via_lord": lord})

    adjacency: dict[int, list[dict[str, Any]]] = {house: [] for house in range(1, 13)}
    for edge in lordship_edges:
        adjacency[edge["from_house"]].append({"type": "lordship", "to_house": edge["to_house"], "lord": edge["lord"]})
    for edge in conjunction_edges:
        adjacency[edge["house_a"]].append({"type": "conjunction", "to_house": edge["house_b"], "meeting_house": edge["meeting_house"]})
        adjacency[edge["house_b"]].append({"type": "conjunction", "to_house": edge["house_a"], "meeting_house": edge["meeting_house"]})
    for edge in aspect_edges:
        if edge["to_house"] != edge["from_house"]:
            adjacency[edge["from_house"]].append({"type": "aspect", "to_house": edge["to_house"], "via_lord": edge["via_lord"]})

    return {
        "house_lords": house_lords,
        "occupants": occupants,
        "lordship_edges": lordship_edges,
        "conjunction_edges": conjunction_edges,
        "aspect_edges": aspect_edges,
        "adjacency": adjacency,
        "citation": "BPHS Ch.11 v.1-8 (bhava-chakra connectivity: lordship placement, occupation, aspect)",
    }


def connections_of(graph: dict[str, Any], house: int) -> list[dict[str, Any]]:
    """Every distinct connection touching one house, across all three edge types."""
    return graph["adjacency"].get(house, [])


def connection_strength(graph: dict[str, Any], house: int) -> int:
    """A structural connectivity count (NOT a Bhava Bala substitute -- see
    app.derived.bhava_bala for the classical strength calculation). This is
    purely "how many distinct houses does this house's network touch,"
    useful as a quick evidence signal for e.g. career (10th house)
    connectivity discussions."""
    return len({edge["to_house"] for edge in connections_of(graph, house)})
