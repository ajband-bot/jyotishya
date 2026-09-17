"""Unit tests for the Phase 8 workbench-catchup API surface: chart
creation, the rule-pack browser, the DB browser, and the two new
additions to app/api/v2/routes.py (coverage + full-context).

Route handlers are `async def` but do no actual I/O-suspension work, so
they're called directly via asyncio.run() -- no HTTP client/dependency
needed, consistent with this repo's existing "test the function, not the
transport" style (see test_db_case_wiring.py, test_reference_tables.py).

Chart-creation tests write a REAL fixture file (app/fixtures.FIXTURE_DIR
is a fixed path, not injectable) -- every test that creates one cleans it
up in a `finally` block so the real data/charts/ and data/jyotisha.db
never end up with test debris.
"""
from __future__ import annotations

import asyncio
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.api.v2 import chart_create, rules_browser  # noqa: E402
from app.api.v2.routes import api_chart_coverage, api_full_context  # noqa: E402
from app.fixtures import FIXTURE_DIR, list_fixture_ids  # noqa: E402


def _run(coro):
    return asyncio.run(coro)


# ---------------------------------------------------------------------
# Chart creation
# ---------------------------------------------------------------------

def _cleanup_chart(chart_id: str) -> None:
    from app.db.models import get_engine, metadata
    from sqlalchemy import delete

    path = FIXTURE_DIR / f"{chart_id}.yaml"
    path.unlink(missing_ok=True)
    engine = get_engine()
    with engine.begin() as conn:
        for name, table in metadata.tables.items():
            if "chart_id" in table.columns:
                conn.execute(delete(table).where(table.c.chart_id == chart_id))
            elif name == "charts":
                conn.execute(delete(table).where(table.c.id == chart_id))


def test_create_chart_fixture_end_to_end():
    req = chart_create.NewChartRequest(
        name="Phase8 Unit Test Person",
        dob="1995-07-04",
        tob="08:00:00",
        utc_offset=5.5,
        latitude=12.9716,
        longitude=77.5946,
        place="Bengaluru",
    )
    chart_id = None
    try:
        result = chart_create.create_chart_fixture(req)
        chart_id = result["chart_id"]
        assert chart_id == "phase8_unit_test_person"
        assert (FIXTURE_DIR / f"{chart_id}.yaml").exists()
        assert "lagna_sign" in result
        assert result["ingested"]["planets"] == 9

        from app.db.models import get_chart

        row = get_chart(chart_id)
        assert row is not None
        assert row["latitude"] == 12.9716
    finally:
        if chart_id:
            _cleanup_chart(chart_id)


def test_unique_chart_id_avoids_collision_with_existing_fixture():
    existing = list_fixture_ids()[0]
    unique = chart_create._unique_chart_id(existing)
    assert unique != existing
    assert unique not in set(list_fixture_ids())


def test_new_chart_request_rejects_out_of_range_latitude():
    """Input Lock (AGENTS.md Step 0): pydantic must reject an impossible
    latitude before any file gets written or any ephemeris call happens."""
    import pydantic

    try:
        chart_create.NewChartRequest(
            name="Phase8 Bad Chart Person", dob="1995-07-04", tob="08:00:00",
            utc_offset=5.5, latitude=200.0, longitude=77.5946,
        )
        assert False, "expected a validation error"
    except pydantic.ValidationError:
        pass


def test_create_chart_fixture_leaves_zero_trace_after_cleanup():
    req = chart_create.NewChartRequest(
        name="Phase8 Cleanup Check Person", dob="1995-07-04", tob="08:00:00",
        utc_offset=5.5, latitude=45.0, longitude=77.5946,
    )
    chart_id = chart_create.create_chart_fixture(req)["chart_id"]
    _cleanup_chart(chart_id)
    assert not (FIXTURE_DIR / f"{chart_id}.yaml").exists()


# ---------------------------------------------------------------------
# Rule pack browser
# ---------------------------------------------------------------------

def test_list_rule_packs_includes_v2_and_v1():
    data = rules_browser.list_rule_packs_data()
    pack_ids = {p["pack_id"] for p in data["packs"]}
    assert "generic_rules_pilot" in pack_ids
    assert "dosha_v2" in pack_ids
    assert "bphs_top20_rule_cards_v1" in pack_ids
    dosha_pack = next(p for p in data["packs"] if p["pack_id"] == "dosha_v2")
    assert dosha_pack["rule_count"] == 15
    assert dosha_pack["kind"] == "v2_generic"


def test_get_rule_pack_returns_full_rule_detail():
    data = rules_browser.get_rule_pack_data("dosha_v2")
    assert data["rule_count"] == 15
    first = data["rules"][0]
    assert "conditions" in first and "outputs" in first and "source_ref" in first


def test_get_rule_pack_filters_by_search():
    data = rules_browser.get_rule_pack_data("dosha_v2", search="mangal")
    assert data["rule_count"] > 0
    assert all("mangal" in r["title"].lower() or "mangal" in r["id"].lower() for r in data["rules"])


def test_get_rule_pack_unknown_pack_raises_keyerror():
    try:
        rules_browser.get_rule_pack_data("does_not_exist")
        assert False, "expected KeyError"
    except KeyError:
        pass


# ---------------------------------------------------------------------
# DB browser (isolated temp DB, same discipline as test_db_case_wiring.py)
# ---------------------------------------------------------------------

def test_db_browser_lists_tables_and_rows():
    tmp_db = tempfile.NamedTemporaryFile(prefix="jyotisha_test_dbbrowser_", suffix=".db", delete=False)
    os.environ["JYOTISHA_DATABASE_URL"] = f"sqlite:///{tmp_db.name}"
    try:
        import importlib

        from app.db import models as db_models
        importlib.reload(db_models)
        from app.api.v2 import db_browser
        importlib.reload(db_browser)

        db_models.upsert_chart({
            "id": "dbtest", "name": "DB Test", "dob": "2000-01-01", "tob": "00:00:00",
            "utc_offset": 5.5, "latitude": 1.0, "longitude": 1.0,
        })

        tables_data = db_browser.list_tables_data()
        names = {t["name"] for t in tables_data["tables"]}
        assert "charts" in names

        rows_data = db_browser.get_table_rows_data("charts", limit=10, offset=0)
        assert rows_data["total_rows"] >= 1
        assert any(r["id"] == "dbtest" for r in rows_data["rows"])

        try:
            db_browser.get_table_rows_data("not_a_table")
            assert False, "expected KeyError"
        except KeyError:
            pass

        try:
            db_browser.get_table_rows_data("charts", limit=0)
            assert False, "expected ValueError"
        except ValueError:
            pass
    finally:
        os.unlink(tmp_db.name)
        os.environ.pop("JYOTISHA_DATABASE_URL", None)


# ---------------------------------------------------------------------
# Coverage + full-context additions to app/api/v2/routes.py
# ---------------------------------------------------------------------

def test_chart_coverage_endpoint_returns_all_four_metrics():
    result = _run(api_chart_coverage("ajay_kumar"))
    for key in ("rule_coverage_pct", "evidence_traceability_pct", "unsupported_claim_count", "contradictions"):
        assert key in result


def test_full_context_endpoint_returns_every_named_section():
    result = _run(api_full_context("ajay_kumar"))
    for key in ("aspects", "ashtakavarga", "doshas", "yogas", "panchanga", "vimsopaka", "gochara", "remedies"):
        assert key in result, f"missing {key}"


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
