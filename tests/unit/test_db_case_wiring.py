"""Unit tests for app.db.ingest / app.db.query -- the Phase 7 "DB wiring
for every case" pipeline. Uses a throwaway temp SQLite file (via
JYOTISHA_DATABASE_URL, set BEFORE importing app.db.models) so this test
never touches the real data/jyotisha.db.
"""
from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

_TMP_DB = tempfile.NamedTemporaryFile(prefix="jyotisha_test_", suffix=".db", delete=False)
os.environ["JYOTISHA_DATABASE_URL"] = f"sqlite:///{_TMP_DB.name}"

from app.db import ingest, models, query  # noqa: E402 -- must follow env var setup above
from app.derived.factors import build_chart_context  # noqa: E402
from app.fixtures import load_chart_fixture  # noqa: E402


def test_ingest_case_populates_every_case_table():
    counts = ingest.ingest_case("ajay_kumar")
    assert counts["planets"] == 9
    assert counts["dashas"] > 0
    assert counts["doshas"] == 8
    assert counts["yogas"] == 18
    assert counts["remedies"] == 9


def test_ingest_case_is_idempotent_not_accumulating():
    """Running ingestion twice for the same chart_id must not double the
    row count -- delete-then-insert, never append."""
    ingest.ingest_case("ajay_kumar")
    first = len(models.get_case_rows("planets", "ajay_kumar"))
    ingest.ingest_case("ajay_kumar")
    second = len(models.get_case_rows("planets", "ajay_kumar"))
    assert first == second == 9


def test_ingested_planet_facts_match_freshly_computed_context():
    """The DB row for a planet must agree with build_chart_context() output
    -- this table is a cache of computed truth, never an independent guess."""
    ingest.ingest_case("ajay_kumar")
    ctx = build_chart_context(load_chart_fixture("ajay_kumar"))
    moon_row = query.get_planet_fact("ajay_kumar", "Moon")
    assert moon_row is not None
    assert moon_row["sign"] == ctx["chart"]["Moon"]["sign"]
    assert moon_row["house"] == ctx["chart"]["Moon"]["house"]


def test_get_current_dasha_returns_md_ad_pd():
    ingest.ingest_case("ajay_kumar")
    current = query.get_current_dasha("ajay_kumar")
    assert "MD" in current
    assert current["MD"]["is_current"] == 1


def test_get_active_doshas_only_returns_present_rows():
    ingest.ingest_case("ajay_kumar")
    active = query.get_active_doshas("ajay_kumar")
    assert all(row["present"] == 1 for row in active)
    names = {row["dosha_name"] for row in active}
    assert "mangal_dosha" in names  # present (though cancelled -- 'present' tracks the raw flag)


def test_qa_log_round_trip():
    ingest.ingest_case("ajay_kumar")
    query.log_qa("ajay_kumar", "Is Mangal Dosha active?", "Present but cancelled (Mars own sign).", "app/derived/doshas.py")
    entries = query.list_qa("ajay_kumar")
    assert len(entries) == 1
    assert entries[0]["question"] == "Is Mangal Dosha active?"

    found = query.search_qa("ajay_kumar", "mangal")
    assert len(found) == 1


def test_ingest_all_fixtures_covers_every_fixture_id():
    from app.fixtures import list_fixture_ids

    counts = ingest.ingest_all_fixtures()
    assert set(counts.keys()) == set(list_fixture_ids())


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
    os.unlink(_TMP_DB.name)
    raise SystemExit(1 if failed else 0)
