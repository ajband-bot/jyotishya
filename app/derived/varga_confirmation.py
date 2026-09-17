"""Generic cross-varga repetition/confirmation engine (build_plan.md Phase 2
item 6).

BPHS's own doctrine for weighing a placement's real strength is never
"read D1 alone" -- a factor repeated across multiple divisional charts
(Vargottama being the simplest, best-known case) is held to be far more
reliably significative than one that appears in D1 only. Every varga
engine in this codebase (`app.astro.vargas.compute_varga`) already exists;
this module is the first GENERIC confirmation layer that runs an arbitrary
boolean check across D1 + a chosen set of vargas and reports how many
agree, rather than every caller hand-rolling its own "check D1 and D9 and
D10" loop (DRY -- this was previously duplicated ad hoc, e.g. Vargottama
being computed inline in `app.knowledge.interpreter.analyze_navamsha`).

The engine is deliberately domain-agnostic: it takes a `check_fn` closure
operating on `{planet: house}` or `{planet: sign}` mappings (whichever the
caller's check needs) and does not know or care what astrological claim is
being confirmed -- that keeps this module honest and reusable rather than
hardcoding one confirmation rule (e.g. "confirm exaltation") and calling it
generic.
"""
from __future__ import annotations

from typing import Any, Callable

from app.astro.vargas import compute_varga

# The BPHS-16 vargas most commonly invoked for cross-confirmation in this
# corpus's own guides (D1 is always implicit/first).
DEFAULT_CONFIRMATION_VARGAS = [9, 10]


def varga_sign_map(chart: dict[str, Any], varga_n: int) -> dict[str, int]:
    """{planet: sign} for D1 (varga_n=1) or any compute_varga() result."""
    if varga_n == 1:
        return {planet: data["sign"] for planet, data in chart.items() if isinstance(data, dict) and "sign" in data}
    varga_data = compute_varga(chart, varga_n)
    return {planet: data["sign"] for planet, data in varga_data["planets"].items()}


def varga_house_map(chart: dict[str, Any], varga_n: int) -> dict[str, int]:
    """{planet: house} for D1 (varga_n=1) or any compute_varga() result."""
    if varga_n == 1:
        return {planet: data["house"] for planet, data in chart.items() if isinstance(data, dict) and "house" in data}
    varga_data = compute_varga(chart, varga_n)
    return {planet: data["house"] for planet, data in varga_data["planets"].items()}


def confirm_across_vargas(
    chart: dict[str, Any],
    check_fn: Callable[[dict[str, int]], bool],
    map_builder: Callable[[dict[str, Any], int], dict[str, int]] = varga_sign_map,
    vargas: list[int] | None = None,
) -> dict[str, Any]:
    """Run `check_fn` against D1 and every varga in `vargas`, tally agreement.

    `check_fn` receives whatever `map_builder` produces for that varga
    (sign map by default; pass `varga_house_map` for house-based checks).
    """
    vargas = vargas if vargas is not None else DEFAULT_CONFIRMATION_VARGAS
    all_vargas = [1] + [v for v in vargas if v != 1]
    per_varga: dict[str, bool] = {}
    for varga_n in all_vargas:
        mapping = map_builder(chart, varga_n)
        label = "D1" if varga_n == 1 else f"D{varga_n}"
        per_varga[label] = bool(check_fn(mapping))

    confirmations = sum(1 for v in per_varga.values() if v)
    total = len(per_varga)
    return {
        "per_varga": per_varga,
        "confirmation_count": confirmations,
        "confirmation_total": total,
        "confirmation_ratio": round(confirmations / total, 4) if total else 0.0,
        "fully_confirmed": confirmations == total,
        "d1_only": per_varga.get("D1", False) and confirmations == 1,
        "citation": "BPHS multi-varga confirmation doctrine (Vargottama being the most-cited instance; generalized here)",
    }


def confirm_planet_in_sign(chart: dict[str, Any], planet: str, sign_no: int, vargas: list[int] | None = None) -> dict[str, Any]:
    """Convenience wrapper: is `planet` in `sign_no` across D1 and the given vargas."""
    return confirm_across_vargas(chart, lambda mapping: mapping.get(planet) == sign_no, varga_sign_map, vargas)


def confirm_planet_in_house(chart: dict[str, Any], planet: str, house_no: int, vargas: list[int] | None = None) -> dict[str, Any]:
    """Convenience wrapper: is `planet` in `house_no` across D1 and the given vargas."""
    return confirm_across_vargas(chart, lambda mapping: mapping.get(planet) == house_no, varga_house_map, vargas)


def confirm_dignity(chart: dict[str, Any], planet: str, dignity_states: set[str], vargas: list[int] | None = None) -> dict[str, Any]:
    """Confirm a planet holds one of `dignity_states` (e.g. {"exalted", "own-sign"})
    consistently across D1 and the given vargas."""
    from app.astro.engine import planet_state

    def check(mapping: dict[str, int]) -> bool:
        sign_no = mapping.get(planet)
        if sign_no is None:
            return False
        return planet_state(planet, sign_no) in dignity_states

    return confirm_across_vargas(chart, check, varga_sign_map, vargas)
