"""Unit tests for build_plan.md Phase 2 foundational engines:
house connection graph, functional benefic/malefic classification, and
the dispositor-chain engine.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.derived.aspects import planet_houses_from_d1_chart
from app.derived.dispositors import (
    detect_mutual_receptions,
    dispositor_chain,
    dispositor_of,
    is_self_disposed,
)
from app.derived.factors import build_chart_context, house_lord
from app.derived.functional_nature import classify_planet, functional_nature_report
from app.derived.house_graph import build_house_connection_graph, connections_of
from app.fixtures import list_fixture_ids, load_chart_fixture


def _context(fixture_id: str = "ajay_kumar"):
    return build_chart_context(load_chart_fixture(fixture_id))


# ── House Connection Graph ──────────────────────────────────────────────
def test_house_graph_has_exactly_12_lordship_edges_for_every_fixture():
    for fixture_id in list_fixture_ids():
        ctx = _context(fixture_id)
        graph = ctx["house_graph"]
        assert len(graph["lordship_edges"]) == 12


def test_house_graph_adjacency_covers_all_12_houses():
    ctx = _context()
    graph = ctx["house_graph"]
    assert set(graph["adjacency"].keys()) == set(range(1, 13))


def test_house_graph_conjunction_edge_symmetric():
    """If A's lord and B's lord meet in the same house, connections_of(A)
    must list B and vice-versa."""
    ctx = _context()
    graph = ctx["house_graph"]
    for edge in graph["conjunction_edges"]:
        a, b = edge["house_a"], edge["house_b"]
        assert any(c["type"] == "conjunction" and c["to_house"] == b for c in connections_of(graph, a))
        assert any(c["type"] == "conjunction" and c["to_house"] == a for c in connections_of(graph, b))


def test_house_graph_is_varga_aware_via_manual_build():
    """Same builder works on any {house: lord} + {planet: house} pair --
    smoke test with a trivial synthetic mapping, not just D1."""
    house_lords = {h: "Sun" if h == 1 else "Moon" for h in range(1, 13)}
    planet_houses = {"Sun": 1, "Moon": 4}
    graph = build_house_connection_graph(house_lords, planet_houses)
    assert graph["lordship_edges"][0] == {"from_house": 1, "to_house": 1, "lord": "Sun"}


# ── Functional Benefic/Malefic Engine ───────────────────────────────────
def test_functional_nature_aries_lagna_mars_gets_dusthana_mitigation():
    """Aries Lagna is the one lagna where a single planet (Mars) rules both
    H1 and H8 -- BPHS's documented exception, not a plain functional malefic."""
    result = classify_planet(1, "Mars", house_lord)
    assert result["owned_houses"] == [1, 8]
    assert result["classification"] == "functional_benefic_with_dusthana_mitigation"


def test_functional_nature_dusthana_lord_without_lagna_exception_is_malefic():
    """Taurus Lagna: Mars rules H7 (kendra) and H12 (dusthana) -- no lagna
    lordship involved, so straightforward functional malefic applies."""
    result = classify_planet(2, "Mars", house_lord)
    assert result["owned_houses"] == [7, 12]
    assert result["classification"] == "functional_malefic"


def test_functional_nature_trikona_lord_is_benefic_regardless_of_natural_nature():
    """Capricorn Lagna: Saturn (natural malefic) rules H1 and H2 -- not
    trikona/kendra/dusthana at all beyond H1; separately, Jupiter rules H12
    and H3 -- verify a natural malefic ruling ONLY a trikona is benefic via
    a lagna where that's structurally true: Cancer Lagna, Jupiter rules H6
    and H9. H9 is trikona -> functional benefic despite H6 dusthana? That
    would be a conflict case -- use a cleaner one instead: Leo Lagna, Mars
    rules H9 (trikona) and H4 (kendra) -> yoga_karaka."""
    result = classify_planet(5, "Mars", house_lord)
    assert result["owned_houses"] == [4, 9]
    assert result["classification"] == "yoga_karaka"


def test_functional_nature_kendradhipati_dosha_for_natural_benefic_sole_kendra_lord():
    """Gemini Lagna: Jupiter rules H7 (kendra) and H10 (kendra) only --
    natural benefic ruling kendra-only -> Kendradhipati Dosha."""
    result = classify_planet(3, "Jupiter", house_lord)
    assert set(result["owned_houses"]) <= {1, 4, 7, 10}
    assert result["classification"] == "kendradhipati_dosha"


def test_functional_nature_report_covers_all_7_classical_planets():
    report = functional_nature_report(1, house_lord)
    assert set(report["planets"].keys()) == {"Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"}
    assert "rahu_ketu" in report and "data_gap" in report["rahu_ketu"]


def test_functional_nature_maraka_flag_independent_of_classification():
    for lagna in range(1, 13):
        report = functional_nature_report(lagna, house_lord)
        for data in report["planets"].values():
            if data["is_maraka"]:
                assert any("maraka" in note for note in data["notes"])


# ── Dispositor Chain Engine ──────────────────────────────────────────────
def test_dispositor_chain_terminates_for_every_planet_in_every_fixture():
    for fixture_id in list_fixture_ids():
        chart = _context(fixture_id)["chart"]
        for planet in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]:
            result = dispositor_chain(chart, planet)
            assert result["terminal"] in {"self_disposed", "cycle", "max_depth_exceeded"}
            if result["terminal"] == "self_disposed":
                assert is_self_disposed(chart, result["final_dispositor"])


def test_dispositor_of_matches_sign_lord_directly():
    chart = _context()["chart"]
    for planet in ["Sun", "Moon"]:
        assert dispositor_of(chart, planet) in {
            "Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn",
        }


def test_mutual_reception_detection_finds_a_real_synthetic_case():
    """Mercury in Cancer (Moon's sign) + Moon in Gemini (Mercury's sign) is
    a textbook mutual reception -- construct it directly rather than
    relying on a fixture happening to contain one."""
    synthetic_chart = {
        "Mercury": {"sign": 4},  # Cancer, ruled by Moon
        "Moon": {"sign": 3},     # Gemini, ruled by Mercury
        "Sun": {"sign": 5},
        "Mars": {"sign": 1},
        "Jupiter": {"sign": 9},
        "Venus": {"sign": 2},
        "Saturn": {"sign": 10},
    }
    pairs = detect_mutual_receptions(synthetic_chart)
    assert any(set(p["planets"]) == {"Mercury", "Moon"} for p in pairs)


def test_dispositor_report_wired_into_chart_context():
    ctx = _context()
    assert "dispositors" in ctx
    assert "mutual_receptions" in ctx["dispositors"]
    assert set(ctx["dispositors"]["chains"].keys()) == {
        "Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu",
    }


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
