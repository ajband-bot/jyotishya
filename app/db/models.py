"""SQLite persistence layer (Postgres-ready) -- SQLAlchemy Core.

Deliberately thin: this is a computation app, not a CRUD app (per
docs/technical-architecture.md 4.7). No ORM models, no ActiveRecord-style
objects -- just table definitions and a handful of functions.

Swapping to Postgres later is a one-line change to DATABASE_URL.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    Integer,
    MetaData,
    String,
    Table,
    Text,
    create_engine,
    select,
)

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DB_PATH = ROOT / "data" / "jyotisha.db"
DATABASE_URL = os.environ.get("JYOTISHA_DATABASE_URL", f"sqlite:///{DEFAULT_DB_PATH}")

metadata = MetaData()

charts = Table(
    "charts", metadata,
    Column("id", String, primary_key=True),          # chart_id, e.g. "ajay_kumar"
    Column("name", String, nullable=False),
    Column("dob", String, nullable=False),
    Column("tob", String, nullable=False),
    Column("utc_offset", Float, nullable=False),
    Column("latitude", Float, nullable=False),
    Column("longitude", Float, nullable=False),
    Column("ayanamsha", String, default="lahiri"),
    Column("node_type", String, default="mean"),
    Column("house_system", String, default="whole_sign"),
    Column("created_at", DateTime, default=lambda: datetime.now(timezone.utc)),
    Column("notes", Text, default=""),
)

rule_versions = Table(
    "rule_versions", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("rule_id", String, nullable=False),
    Column("version", Integer, nullable=False),
    Column("status", String, nullable=False),        # DRAFT/SOURCE_FOUND/VERIFIED/ACTIVE/DEPRECATED/CONTESTED
    Column("payload_json", Text, nullable=False),
    Column("created_at", DateTime, default=lambda: datetime.now(timezone.utc)),
    Column("created_by", String, default="system"),
)

analysis_snapshots = Table(
    "analysis_snapshots", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("chart_id", String, nullable=False),
    Column("rule_pack_version", String, nullable=False),
    Column("computed_at", DateTime, default=lambda: datetime.now(timezone.utc)),
    Column("result_json", Text, nullable=False),
)

cheatsheet_claims = Table(
    "cheatsheet_claims", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("source_file", String, nullable=False),
    Column("section", String, nullable=False),
    Column("claim_text", Text, nullable=False),
    Column("formula_ref", String, nullable=True),
    Column("applies_to_chart", String, nullable=True),
    Column("last_validated_at", DateTime, nullable=True),
    Column("last_verdict", String, nullable=True),   # match/mismatch/unverifiable/data_gap
)

# ---------------------------------------------------------------------------
# Phase 7 -- "DB wiring for every case" tables.
#
# Design intent (per build_plan.md Phase 7 + Ajay's explicit ask): a
# follow-up question about a specific person's chart ("what dosha is
# active", "what's the current dasha", "was a gemstone recommended for
# Saturn") should be answerable with a SQL SELECT against these tables --
# never by re-opening a multi-hundred-KB output/*.html reading file.
#
# These are DERIVED/CACHE tables, not the source of truth -- app.db.ingest
# repopulates them from build_chart_context() (delete-then-insert per
# chart_id, the same "regenerate, never hand-edit" discipline already used
# for app/rules/compiled/*.yaml). data/charts/*.yaml fixtures remain the
# actual seed data.
# ---------------------------------------------------------------------------

case_planets = Table(
    "case_planets", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("chart_id", String, nullable=False, index=True),
    Column("planet", String, nullable=False),
    Column("sign", Integer, nullable=False),
    Column("house", Integer, nullable=False),
    Column("deg_in_sign", Float, nullable=False),
    Column("retrograde", Integer, nullable=False),   # 0/1 -- SQLite has no native bool
    Column("combust", Integer, nullable=False),
    Column("nakshatra", String, nullable=True),
    Column("pada", Integer, nullable=True),
    Column("functional_classification", String, nullable=True),
    Column("ingested_at", DateTime, default=lambda: datetime.now(timezone.utc)),
)

case_dashas = Table(
    "case_dashas", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("chart_id", String, nullable=False, index=True),
    Column("level", String, nullable=False),   # MD / AD / PD
    Column("lord", String, nullable=False),
    Column("start_date", String, nullable=False),
    Column("end_date", String, nullable=False),
    Column("is_current", Integer, nullable=False),
    Column("ingested_at", DateTime, default=lambda: datetime.now(timezone.utc)),
)

case_doshas = Table(
    "case_doshas", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("chart_id", String, nullable=False, index=True),
    Column("dosha_name", String, nullable=False),
    Column("present", Integer, nullable=True),      # nullable: some checks have no single top-level flag
    Column("severity", String, nullable=True),
    Column("citation", String, nullable=True),
    Column("detail_json", Text, nullable=False),     # full computed dict -- source of truth for nuance
    Column("ingested_at", DateTime, default=lambda: datetime.now(timezone.utc)),
)

case_yogas = Table(
    "case_yogas", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("chart_id", String, nullable=False, index=True),
    Column("yoga_name", String, nullable=False),
    Column("present", Integer, nullable=True),
    Column("detail_json", Text, nullable=False),
    Column("ingested_at", DateTime, default=lambda: datetime.now(timezone.utc)),
)

case_remedies = Table(
    "case_remedies", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("chart_id", String, nullable=False, index=True),
    Column("planet", String, nullable=False),
    Column("classification", String, nullable=True),
    Column("gemstone_appropriate", Integer, nullable=False),
    Column("gemstone_contraindicated", Integer, nullable=False),
    Column("remedy_note", Text, nullable=True),
    Column("ingested_at", DateTime, default=lambda: datetime.now(timezone.utc)),
)

case_qa_log = Table(
    "case_qa_log", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("chart_id", String, nullable=False, index=True),
    Column("question", Text, nullable=False),
    Column("answer", Text, nullable=False),
    Column("source_refs", Text, default=""),   # e.g. "app/derived/doshas.py::check_mangal_dosha"
    Column("asked_at", DateTime, default=lambda: datetime.now(timezone.utc)),
)

cheatsheet_concepts = Table(
    "cheatsheet_concepts", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("concept_id", String, nullable=False, unique=True),
    Column("category", String, nullable=False),
    Column("sanskrit_term", String, nullable=True),
    Column("english_gloss", String, nullable=False),
    Column("classical_definition", Text, nullable=False),
    Column("primary_citation", String, nullable=False),
    Column("code_ref", String, nullable=True),
    Column("quality_label", String, nullable=False),
    Column("caveats", Text, default=""),        # "; "-joined list
    Column("cross_check_note", Text, default=""),
    Column("last_synced_at", DateTime, default=lambda: datetime.now(timezone.utc)),
)

CASE_FACT_TABLES: dict[str, Table] = {
    "planets": case_planets,
    "dashas": case_dashas,
    "doshas": case_doshas,
    "yogas": case_yogas,
    "remedies": case_remedies,
}

_engine = None


def get_engine():
    global _engine
    if _engine is None:
        DEFAULT_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        _engine = create_engine(DATABASE_URL, echo=False, future=True)
        metadata.create_all(_engine)
    return _engine


def upsert_chart(chart_row: dict[str, Any]) -> None:
    engine = get_engine()
    with engine.begin() as conn:
        existing = conn.execute(select(charts.c.id).where(charts.c.id == chart_row["id"])).first()
        if existing:
            conn.execute(
                charts.update().where(charts.c.id == chart_row["id"]).values(**chart_row)
            )
        else:
            conn.execute(charts.insert().values(**chart_row))


def get_chart(chart_id: str) -> dict[str, Any] | None:
    engine = get_engine()
    with engine.connect() as conn:
        row = conn.execute(select(charts).where(charts.c.id == chart_id)).mappings().first()
        return dict(row) if row else None


def list_charts() -> list[dict[str, Any]]:
    engine = get_engine()
    with engine.connect() as conn:
        rows = conn.execute(select(charts)).mappings().all()
        return [dict(r) for r in rows]


def save_analysis_snapshot(chart_id: str, rule_pack_version: str, result: dict[str, Any]) -> int:
    engine = get_engine()
    with engine.begin() as conn:
        res = conn.execute(
            analysis_snapshots.insert().values(
                chart_id=chart_id,
                rule_pack_version=rule_pack_version,
                result_json=json.dumps(result, default=str),
            )
        )
        return res.inserted_primary_key[0]


def seed_charts_from_fixtures() -> int:
    """Import existing data/charts/*.yaml fixtures into the charts table.

    Additive, idempotent -- existing fixture files remain the source of
    truth for regression tests (tests/run_suite.py is untouched); this just
    makes them queryable via the DB for the new workbench API.
    """
    from app.fixtures import FIXTURE_DIR, load_chart_fixture

    count = 0
    for path in Path(FIXTURE_DIR).glob("*.yaml"):
        chart_id = path.stem
        fixture = load_chart_fixture(chart_id)
        location = fixture["location"]
        upsert_chart({
            "id": chart_id,
            "name": fixture.get("name", chart_id),
            "dob": str(fixture["dob"]),
            "tob": fixture["time_local"],
            "utc_offset": fixture["utc_offset"],
            "latitude": location["latitude"],
            "longitude": location["longitude"],
            "ayanamsha": fixture.get("settings", {}).get("ayanamsha", "lahiri"),
            "node_type": fixture.get("settings", {}).get("node_type", "mean"),
            "house_system": fixture.get("settings", {}).get("house_system", "whole_sign"),
            "notes": "; ".join(fixture.get("notes", [])),
        })
        count += 1
    return count


# ---------------------------------------------------------------------------
# Phase 7 write/read helpers -- case facts, cheatsheet claims, rule versions,
# and the case Q&A log. Kept generic and small on purpose (this stays a thin
# Core layer, not an ORM) -- app/db/ingest.py and app/db/query.py are where
# the domain-shaping logic lives.
# ---------------------------------------------------------------------------


def replace_case_rows(fact: str, chart_id: str, rows: list[dict[str, Any]]) -> int:
    """Delete every existing row for this chart_id in the named case-fact
    table, then bulk-insert the fresh set. Idempotent re-ingestion --
    running this twice for the same chart_id never accumulates duplicates.
    `fact` is one of CASE_FACT_TABLES's keys ("planets"/"dashas"/"doshas"/
    "yogas"/"remedies").
    """
    table = CASE_FACT_TABLES[fact]
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(table.delete().where(table.c.chart_id == chart_id))
        if rows:
            conn.execute(table.insert(), rows)
    return len(rows)


def get_case_rows(fact: str, chart_id: str) -> list[dict[str, Any]]:
    table = CASE_FACT_TABLES[fact]
    engine = get_engine()
    with engine.connect() as conn:
        rows = conn.execute(select(table).where(table.c.chart_id == chart_id)).mappings().all()
        return [dict(r) for r in rows]


def replace_rule_versions(rows: list[dict[str, Any]]) -> int:
    """Full resync of the rule_versions table from the current compiled
    rule packs -- this table describes ENGINE state ("what rules exist and
    at what status"), not any one chart's facts, so a full wipe+reload is
    the correct semantics (unlike case_* tables, which are scoped per
    chart_id)."""
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(rule_versions.delete())
        if rows:
            conn.execute(rule_versions.insert(), rows)
    return len(rows)


def replace_cheatsheet_claims(rows: list[dict[str, Any]]) -> int:
    """Full resync of cheatsheet_claims from a fresh
    extract_all_claims()+validate_claims() pass -- this is the literal
    build_plan.md Phase 7 ask ("wire cheatsheet_claims... live"), moving the
    console from compute-on-every-request to a persisted, queryable table
    that also carries a last_validated_at audit timestamp."""
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(cheatsheet_claims.delete())
        if rows:
            conn.execute(cheatsheet_claims.insert(), rows)
    return len(rows)


def replace_cheatsheet_concepts(rows: list[dict[str, Any]]) -> int:
    """Full resync of cheatsheet_concepts from app.engine.cheatsheet.concepts's
    registry -- the learning-platform concept table (see that module for why
    it, not this one, is the editorial source of truth)."""
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(cheatsheet_concepts.delete())
        if rows:
            conn.execute(cheatsheet_concepts.insert(), rows)
    return len(rows)


def log_case_qa(chart_id: str, question: str, answer: str, source_refs: str = "") -> int:
    """Persist one follow-up Q&A for a case. Once logged, a repeat of the
    same question is a SQL lookup (app.db.query.search_case_qa), not a
    re-read of the original reading files."""
    engine = get_engine()
    with engine.begin() as conn:
        res = conn.execute(
            case_qa_log.insert().values(
                chart_id=chart_id, question=question, answer=answer, source_refs=source_refs,
            )
        )
        return res.inserted_primary_key[0]


def list_case_qa(chart_id: str) -> list[dict[str, Any]]:
    engine = get_engine()
    with engine.connect() as conn:
        rows = conn.execute(
            select(case_qa_log).where(case_qa_log.c.chart_id == chart_id).order_by(case_qa_log.c.asked_at.desc())
        ).mappings().all()
        return [dict(r) for r in rows]

