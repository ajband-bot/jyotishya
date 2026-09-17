"""Unit tests for Graha Maitri dignities -- app/derived/dignities.py.

Per build_plan.md Phase 1: "Friend/enemy (Graha Maitri) dignities --
naisargika/tatkalika/panchadha".
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.astro.constants import NATURAL_RELATIONSHIPS
from app.astro.vargas import compute_varga
from app.derived.aspects import planet_houses_from_d1_chart, planet_houses_from_varga
from app.derived.dignities import (
    PANCHADHA_SCORE,
    TEMPORAL_ENEMY_HOUSES,
    TEMPORAL_FRIEND_HOUSES,
    graha_maitri_report,
    naisargika_relationship,
    panchadha_relationship,
    tatkalika_relationship,
)
from app.derived.factors import build_chart_context
from app.fixtures import list_fixture_ids, load_chart_fixture


def _chart(fixture_id: str = "ajay_kumar"):
    return build_chart_context(load_chart_fixture(fixture_id))["chart"]


def test_naisargika_core_seven_planet_table_is_symmetric_on_friendship_where_expected():
    """Cross-check spot: Sun-Moon and Mars-Jupiter are BPHS mutual friends;
    Sun-Saturn and Sun-Venus are mutual enemies -- classic textbook pairs
    that happen to agree in both directions."""
    assert naisargika_relationship("Sun", "Moon") == "friend"
    assert naisargika_relationship("Moon", "Sun") == "friend"
    assert naisargika_relationship("Mars", "Jupiter") == "friend"
    assert naisargika_relationship("Jupiter", "Mars") == "friend"
    assert naisargika_relationship("Sun", "Saturn") == "enemy"
    assert naisargika_relationship("Saturn", "Sun") == "enemy"
    assert naisargika_relationship("Sun", "Venus") == "enemy"
    assert naisargika_relationship("Venus", "Sun") == "enemy"


def test_naisargika_relationship_is_not_generally_symmetric():
    """Graha Maitri is directional per BPHS -- Jupiter treats Venus as an
    enemy, but Venus treats Jupiter as merely neutral. This asymmetry is
    classical doctrine, not a bug."""
    assert naisargika_relationship("Jupiter", "Venus") == "enemy"
    assert naisargika_relationship("Venus", "Jupiter") == "neutral"


def test_naisargika_moon_has_no_enemies():
    """Classical fact: Moon has friends and neutrals but zero enemies."""
    assert NATURAL_RELATIONSHIPS["Moon"]["enemies"] == []
    for other in ("Sun", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"):
        assert naisargika_relationship("Moon", other) != "enemy"


def test_temporal_relationship_houses_partition_correctly():
    assert TEMPORAL_FRIEND_HOUSES == {2, 3, 4, 10, 11, 12}
    assert TEMPORAL_ENEMY_HOUSES == {1, 5, 6, 7, 8, 9}
    assert TEMPORAL_FRIEND_HOUSES | TEMPORAL_ENEMY_HOUSES == set(range(1, 13))
    assert TEMPORAL_FRIEND_HOUSES & TEMPORAL_ENEMY_HOUSES == set()


def test_tatkalika_conjunction_is_temporal_enemy():
    """Two planets in the same house (distance 1) are temporal enemies,
    per the classical rule -- even if naturally friendly."""
    planet_houses = {"Sun": 5, "Moon": 5}
    assert tatkalika_relationship(planet_houses, "Sun", "Moon") == "enemy"


def test_panchadha_compound_table_matches_cross_checked_pyjhora_logic():
    assert panchadha_relationship("friend", "friend") == "adhi_mitra"
    assert panchadha_relationship("neutral", "friend") == "mitra"
    assert panchadha_relationship("friend", "enemy") == "sama"
    assert panchadha_relationship("enemy", "friend") == "sama"
    assert panchadha_relationship("neutral", "enemy") == "shatru"
    assert panchadha_relationship("enemy", "enemy") == "adhi_shatru"
    assert PANCHADHA_SCORE["adhi_mitra"] > PANCHADHA_SCORE["mitra"] > PANCHADHA_SCORE["sama"] \
        > PANCHADHA_SCORE["shatru"] > PANCHADHA_SCORE["adhi_shatru"]


def test_graha_maitri_report_symmetric_naisargika_and_complete_for_every_fixture():
    for fixture_id in list_fixture_ids():
        chart = _chart(fixture_id)
        planet_houses = planet_houses_from_d1_chart(chart)
        report = graha_maitri_report(planet_houses)
        planets = list(planet_houses.keys())
        for planet in planets:
            relationships = report["planets"][planet]["relationships"]
            assert set(relationships.keys()) == set(planets) - {planet}
            for other, data in relationships.items():
                assert data["naisargika"] in {"friend", "neutral", "enemy"}
                assert data["tatkalika"] in {"friend", "enemy"}
                assert data["panchadha"] in PANCHADHA_SCORE


def test_graha_maitri_is_varga_aware_via_d9():
    chart = _chart("ajay_kumar")
    d9 = compute_varga(chart, 9)
    d1_report = graha_maitri_report(planet_houses_from_d1_chart(chart))
    d9_report = graha_maitri_report(planet_houses_from_varga(d9))
    assert set(d1_report["planets"].keys()) == set(d9_report["planets"].keys())


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
