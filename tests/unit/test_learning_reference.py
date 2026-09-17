"""Unit tests for the Learning tab's expanded reference content: Vimsottari
Dasha reference, Transit/Gochara reference, Top Rules corpus, and the
planet relationship graph shape."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.astro.constants import DASHA_ORDER, DASHA_YEARS, TOTAL_DASHA_YEARS
from app.derived.reference_tables import (
    get_dasha_reference,
    get_planet_relationship_graph,
    get_top_rules,
    get_transit_reference,
)


def test_dasha_reference_sequence_matches_constants():
    ref = get_dasha_reference()
    assert [s["planet"] for s in ref["sequence"]] == DASHA_ORDER
    assert ref["total_years"] == TOTAL_DASHA_YEARS


def test_dasha_reference_antardasha_years_sum_to_mahadasha_years():
    """The 9 AD durations for any MD planet must sum back to that planet's
    full Mahadasha years (BPHS Ch.46 proportional formula sanity check)."""
    ref = get_dasha_reference()
    for md_planet in DASHA_ORDER:
        rows = ref["antardasha_tables"][md_planet]
        assert len(rows) == 9
        total = sum(r["years"] for r in rows)
        assert abs(total - DASHA_YEARS[md_planet]) < 0.01


def test_dasha_reference_antardasha_starts_with_md_lord():
    ref = get_dasha_reference()
    for md_planet in DASHA_ORDER:
        assert ref["antardasha_tables"][md_planet][0]["planet"] == md_planet


def test_pratyantardasha_years_sum_to_antardasha_years():
    """The 9 PD durations for any (MD, AD) pair must sum back to that AD's
    own years -- same proportional sanity check one level deeper."""
    ref = get_dasha_reference()
    for md_planet in DASHA_ORDER:
        for ad_row in ref["antardasha_tables"][md_planet]:
            ad_planet = ad_row["planet"]
            pd_rows = ref["pratyantardasha_tables"][md_planet][ad_planet]
            assert len(pd_rows) == 9
            total = sum(r["years"] for r in pd_rows)
            assert abs(total - ad_row["years"]) < 0.001


def test_pratyantardasha_starts_with_ad_lord():
    ref = get_dasha_reference()
    pd_rows = ref["pratyantardasha_tables"]["Saturn"]["Mercury"]
    assert pd_rows[0]["planet"] == "Mercury"


def test_transit_reference_covers_all_12_houses_both_planets():
    ref = get_transit_reference()
    assert set(ref["jupiter_from_moon"].keys()) == set(range(1, 13))
    assert set(ref["saturn_from_moon"].keys()) == set(range(1, 13))


def test_transit_reference_sade_sati_houses_match_engine():
    """Regression guard: must stay in sync with app.astro.transits'
    SATURN_SADE_SATI set (houses 12, 1, 2 from Moon)."""
    ref = get_transit_reference()
    sade_sati_houses = {h for h, v in ref["saturn_from_moon"].items() if v["quality"] == "sade_sati"}
    assert sade_sati_houses == {12, 1, 2}


def test_transit_reference_has_3_sade_sati_phases():
    ref = get_transit_reference()
    assert len(ref["sade_sati_phases"]) == 3
    assert {p["phase"] for p in ref["sade_sati_phases"]} == {1, 2, 3}


def test_top_rules_returns_structured_corpus():
    result = get_top_rules()
    assert result["total_rules"] >= 1
    assert result["target_total"] == 30
    assert "RC-001" in [r["rule_id"] for r in result["rules"]]
    assert "foundation" in result["by_domain"]


def test_top_rules_each_rule_has_citations():
    result = get_top_rules()
    for rule in result["rules"]:
        assert "citations" in rule
        assert "canonical_statement" in rule


def test_planet_relationship_graph_shape():
    graph = get_planet_relationship_graph()
    assert len(graph["nodes"]) == 7
    node_ids = {n["id"] for n in graph["nodes"]}
    for edge in graph["edges"]:
        assert edge["source"] in node_ids
        assert edge["target"] in node_ids
        assert edge["kind"] in {"friend", "enemy"}


def test_planet_relationship_graph_no_duplicate_edges():
    graph = get_planet_relationship_graph()
    seen = set()
    for edge in graph["edges"]:
        key = tuple(sorted([edge["source"], edge["target"]]))
        assert key not in seen
        seen.add(key)


if __name__ == "__main__":
    import traceback

    tests = [obj for name, obj in list(globals().items()) if name.startswith("test_")]
    failed = 0
    for t in tests:
        try:
            t()
            print(f"[PASS] {t.__name__}")
        except Exception:
            failed += 1
            print(f"[FAIL] {t.__name__}")
            traceback.print_exc()
    print(f"\n{len(tests) - failed}/{len(tests)} passed")
    raise SystemExit(1 if failed else 0)
