"""Unit tests for app.derived.reference_tables -- the Learning/Cheat-Sheet
tab's fundamentals layer (house themes, functional nature grid, natural
relationships, dignity table, lord-placement connections).
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.derived.reference_tables import (
    ALL_PLANETS,
    NATURAL_RELATIONSHIPS,
    get_dignity_table,
    get_functional_nature_grid,
    get_house_themes,
    get_lord_placement_connections,
    get_natural_relationships,
)
from app.rules.loader import load_rule_pack


def test_house_themes_covers_all_12_houses_with_three_layers():
    themes = get_house_themes()
    assert set(themes.keys()) == set(range(1, 13))
    for house_no, data in themes.items():
        assert data["core"] and data["material"] and data["higher"]
        assert data["nature"] in {"trikona", "kendra", "dusthana", "upachaya", "neutral"}


def test_natural_relationships_matches_verified_rule_pack_table_exactly():
    """Regression guard: the constant in reference_tables.py must stay in
    sync with the verified table embedded in bphs_top20_rule_cards_v1.yaml."""
    pack = load_rule_pack()
    source_table = pack["meta"]["graha_condition_policy"]["sub_factors"]["natural_relationship"]["table"]
    for planet in ALL_PLANETS:
        assert set(NATURAL_RELATIONSHIPS[planet]["friends"]) == set(source_table[planet]["friends"])
        assert set(NATURAL_RELATIONSHIPS[planet]["neutral"]) == set(source_table[planet]["neutral"])
        assert set(NATURAL_RELATIONSHIPS[planet]["enemies"]) == set(source_table[planet]["enemies"])


def test_natural_relationships_response_shape():
    result = get_natural_relationships()
    assert result["citation_status"] == "verified"
    assert set(result["table"].keys()) == set(ALL_PLANETS)


def test_dignity_table_matches_known_classical_exaltations():
    dignity = get_dignity_table()
    assert dignity["Sun"]["exalted_sign"] == "Aries"
    assert dignity["Sun"]["debilitated_sign"] == "Libra"
    assert dignity["Jupiter"]["exalted_sign"] == "Cancer"
    assert dignity["Saturn"]["exalted_sign"] == "Libra"
    assert dignity["Saturn"]["debilitated_sign"] == "Aries"
    for planet in ALL_PLANETS:
        assert dignity[planet]["moolatrikona_citation_status"] == "pending_audit"


def test_functional_nature_grid_covers_all_12_lagnas_and_7_planets():
    result = get_functional_nature_grid()
    grid = result["grid"]
    assert set(grid.keys()) == set(range(1, 13))
    for lagna_sign, data in grid.items():
        assert set(data["planets"].keys()) == set(ALL_PLANETS)
    assert "not planet strength" in result["disclaimer"].lower()


def test_functional_nature_grid_taurus_saturn_is_yogakaraka():
    result = get_functional_nature_grid()
    cell = result["grid"][2]["planets"]["Saturn"]  # 2 = Taurus
    assert cell["tag"] == "YK"
    assert cell["is_yoga_karaka"] is True


def test_functional_nature_grid_scorpio_mars_is_lagna_lord_dusthana_mix():
    """Scorpio Lagna: Mars owns H1 (lagna) and H6 (dusthana) -- mixed case,
    must NOT be flagged yoga-karaka (regression guard for the fixed bug)."""
    result = get_functional_nature_grid()
    cell = result["grid"][8]["planets"]["Mars"]  # 8 = Scorpio
    assert cell["is_yoga_karaka"] is False
    assert cell["is_lagna_lord"] is True
    assert 6 in cell["houses_owned"]


def test_lord_placement_connections_full_matrix_shape():
    result = get_lord_placement_connections(lagna_sign=8)  # Scorpio
    assert len(result["matrix"]) == 12
    for source_house, row in result["matrix"].items():
        assert row["lord"]
        assert len(row["destinations"]) == 12
        for dest_house, cell in row["destinations"].items():
            assert "->" in cell["connection"]


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
