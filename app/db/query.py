"""Read-side query helpers for case facts (build_plan.md Phase 7).

Every function here answers exactly the kind of follow-up question a human
or an LLM session asks about a person's chart AFTER the initial reading was
generated -- "what's the current dasha", "is Mangal Dosha still active",
"was a gemstone cleared for Jupiter" -- via a plain SQL SELECT against the
case_* tables app.db.ingest populates. None of these re-run astrology
computation; if a chart hasn't been ingested yet (app.db.ingest.ingest_case)
these simply return empty results, they never silently fall back to
recomputing (that would defeat the point: fast, deterministic, file-free
retrieval).
"""
from __future__ import annotations

import json
from typing import Any

from sqlalchemy import select

from app.db import models


def get_case_summary(chart_id: str) -> dict[str, Any]:
    """One-shot bundle: chart metadata + every case-fact table's rows for
    this chart_id. This is the DB-backed replacement for "open the person's
    output/*.html files to check their case details."""
    return {
        "chart": models.get_chart(chart_id),
        "planets": models.get_case_rows("planets", chart_id),
        "dashas": models.get_case_rows("dashas", chart_id),
        "doshas": models.get_case_rows("doshas", chart_id),
        "yogas": models.get_case_rows("yogas", chart_id),
        "remedies": models.get_case_rows("remedies", chart_id),
    }


def get_current_dasha(chart_id: str) -> dict[str, Any]:
    rows = models.get_case_rows("dashas", chart_id)
    current = {row["level"]: row for row in rows if row["is_current"]}
    return current


def get_active_doshas(chart_id: str) -> list[dict[str, Any]]:
    """Doshas whose case_doshas.present column is truthy (1). Rows with a
    NULL present column (no single top-level flag in the computed detail --
    see app.db.ingest._summarize_presence) are excluded here but remain
    visible via get_case_summary()'s full row set, detail_json included."""
    rows = models.get_case_rows("doshas", chart_id)
    return [r for r in rows if r["present"] == 1]


def get_active_yogas(chart_id: str) -> list[dict[str, Any]]:
    rows = models.get_case_rows("yogas", chart_id)
    return [r for r in rows if r["present"] == 1]


def get_planet_fact(chart_id: str, planet: str) -> dict[str, Any] | None:
    rows = models.get_case_rows("planets", chart_id)
    for row in rows:
        if row["planet"] == planet:
            return row
    return None


def get_remedy(chart_id: str, planet: str) -> dict[str, Any] | None:
    rows = models.get_case_rows("remedies", chart_id)
    for row in rows:
        if row["planet"] == planet:
            return row
    return None


def get_detail(chart_id: str, fact: str, name_column: str, name: str) -> dict[str, Any] | None:
    """Generic accessor for the parsed detail_json of a single dosha/yoga
    row, e.g. get_detail('ajay_kumar', 'doshas', 'dosha_name', 'mangal_dosha')."""
    rows = models.get_case_rows(fact, chart_id)
    for row in rows:
        if row.get(name_column) == name:
            detail = row.get("detail_json")
            return json.loads(detail) if detail else None
    return None


def log_qa(chart_id: str, question: str, answer: str, source_refs: str = "") -> int:
    return models.log_case_qa(chart_id, question, answer, source_refs)


def list_qa(chart_id: str) -> list[dict[str, Any]]:
    return models.list_case_qa(chart_id)


def search_qa(chart_id: str, needle: str) -> list[dict[str, Any]]:
    """Simple case-insensitive substring search over a chart's logged Q&A --
    a repeated or closely related question should surface a prior answer
    instead of triggering a fresh re-derivation."""
    needle_lower = needle.lower()
    return [
        row for row in models.list_case_qa(chart_id)
        if needle_lower in row["question"].lower() or needle_lower in row["answer"].lower()
    ]


def list_all_cases() -> list[dict[str, Any]]:
    """Every chart currently ingested, for a 'which cases do we even have
    wired' index view."""
    return models.list_charts()
