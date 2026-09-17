"""Case ingestion pipeline (build_plan.md Phase 7 -- "DB wiring for every
case we are running").

Populates the case_* tables in app/db/models.py from a freshly computed
build_chart_context() -- so a follow-up question about a specific person's
chart ("what's the current dasha", "does this dosha still apply", "was a
gemstone cleared for Saturn") is a SQL SELECT (app.db.query) instead of a
re-read of a multi-hundred-KB output/*.html reading file.

Delete-then-insert per chart_id, same "regenerate, never hand-edit compiled
state" discipline as app/rules/generators/emit_all.py -- running this twice
for the same chart_id never accumulates duplicate rows. This module never
invents a fact; every row here traces to a field already present in
build_chart_context()'s output.
"""
from __future__ import annotations

import json
from typing import Any

from app.db import models
from app.derived.factors import build_chart_context
from app.fixtures import list_fixture_ids, load_chart_fixture


def _bool_to_int(value: Any) -> int:
    return 1 if bool(value) else 0


ALL_PLANET_NAMES = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]


def _planet_rows(chart_id: str, ctx: dict[str, Any]) -> list[dict[str, Any]]:
    chart = ctx["chart"]
    combustion = ctx["combustion"]
    functional_nature = ctx["functional_nature"].get("planets", {})
    nakshatras = ctx["nakshatra_analysis"]
    rows = []
    for planet in ALL_PLANET_NAMES:
        if planet not in chart:
            continue
        data = chart[planet]
        nk = nakshatras.get(planet, {})
        fn = functional_nature.get(planet, {})
        rows.append({
            "chart_id": chart_id,
            "planet": planet,
            "sign": data["sign"],
            "house": data["house"],
            "deg_in_sign": data["deg_in_sign"],
            "retrograde": _bool_to_int(data.get("retrograde", False)),
            "combust": _bool_to_int(combustion.get(planet, {}).get("combust", False)),
            "nakshatra": nk.get("nakshatra_en"),
            "pada": nk.get("pada"),
            "functional_classification": fn.get("classification"),
        })
    return rows


def _dasha_rows(chart_id: str, ctx: dict[str, Any]) -> list[dict[str, Any]]:
    current = ctx["current_dasha"] or {}
    current_md = current.get("mahadasha") or {}
    current_ad = current.get("antardasha") or {}
    current_pd = current.get("pratyantardasha") or {}

    def _row(level: str, entry: dict[str, Any], current_entry: dict[str, Any]) -> dict[str, Any]:
        is_current = bool(current_entry) and entry.get("planet") == current_entry.get("planet") \
            and entry.get("start") == current_entry.get("start")
        return {
            "chart_id": chart_id, "level": level, "lord": entry["planet"],
            "start_date": entry["start"], "end_date": entry["end"],
            "is_current": _bool_to_int(is_current),
        }

    rows = [_row("MD", d, current_md) for d in ctx["dashas"]]
    rows += [_row("AD", a, current_ad) for a in current.get("all_antars", [])]
    rows += [_row("PD", p, current_pd) for p in current.get("all_pratyantaras", [])]
    return rows


def _summarize_presence(detail: Any) -> int | None:
    """Best-effort boolean summary for the case_doshas/case_yogas 'present'
    column -- some checks (e.g. Pancha Mahapurusha) nest per-planet results
    under 'any_present' instead of a bare top-level 'present'. Returns None
    (SQL NULL) rather than guessing when neither key exists -- the full
    detail_json column is always the source of truth for anything nuanced,
    this column is a query-convenience shortcut only."""
    if not isinstance(detail, dict):
        return None
    if "present" in detail:
        return _bool_to_int(detail["present"])
    if "any_present" in detail:
        return _bool_to_int(detail["any_present"])
    return None


def _dosha_rows(chart_id: str, ctx: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for name, detail in ctx["doshas"].items():
        rows.append({
            "chart_id": chart_id,
            "dosha_name": name,
            "present": _summarize_presence(detail),
            "severity": detail.get("severity") if isinstance(detail, dict) else None,
            "citation": detail.get("citation") if isinstance(detail, dict) else None,
            "detail_json": json.dumps(detail, default=str),
        })
    return rows


def _yoga_rows(chart_id: str, ctx: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for name, detail in ctx["yogas"].items():
        rows.append({
            "chart_id": chart_id,
            "yoga_name": name,
            "present": _summarize_presence(detail),
            "detail_json": json.dumps(detail, default=str),
        })
    return rows


def _remedy_rows(chart_id: str, ctx: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for planet, entry in ctx["remedies"]["planets"].items():
        rows.append({
            "chart_id": chart_id,
            "planet": planet,
            "classification": entry.get("classification"),
            "gemstone_appropriate": _bool_to_int(entry.get("gemstone_appropriate", False)),
            "gemstone_contraindicated": _bool_to_int(entry.get("gemstone_contraindicated", False)),
            "remedy_note": entry.get("remedy_note"),
        })
    return rows


def _snapshot_summary(ctx: dict[str, Any]) -> dict[str, Any]:
    """A compact, JSON-safe audit summary for analysis_snapshots -- not the
    entire context (which is large and not all of it round-trips cleanly
    through json.dumps). Good enough to answer "what did the engine compute
    on date X" without re-running the whole pipeline."""
    return {
        "lagna_sign": ctx["lagna_sign"],
        "current_dasha": ctx["current_dasha"],
        "doshas_present": {k: _summarize_presence(v) for k, v in ctx["doshas"].items()},
        "yogas_present": {k: _summarize_presence(v) for k, v in ctx["yogas"].items()},
        "yoga_karakas": ctx["yoga_karakas"],
    }


def ingest_case(chart_id: str, ctx: dict[str, Any] | None = None) -> dict[str, int]:
    """(Re)compute (unless ctx is supplied) and (re)populate every case_*
    table for one chart_id. Safe to call repeatedly."""
    fixture = load_chart_fixture(chart_id)
    ctx = ctx if ctx is not None else build_chart_context(fixture)
    location = fixture["location"]

    models.upsert_chart({
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

    counts = {
        "planets": models.replace_case_rows("planets", chart_id, _planet_rows(chart_id, ctx)),
        "dashas": models.replace_case_rows("dashas", chart_id, _dasha_rows(chart_id, ctx)),
        "doshas": models.replace_case_rows("doshas", chart_id, _dosha_rows(chart_id, ctx)),
        "yogas": models.replace_case_rows("yogas", chart_id, _yoga_rows(chart_id, ctx)),
        "remedies": models.replace_case_rows("remedies", chart_id, _remedy_rows(chart_id, ctx)),
    }
    models.save_analysis_snapshot(chart_id, rule_pack_version="phase7-v1", result=_snapshot_summary(ctx))
    return counts


def ingest_all_fixtures() -> dict[str, dict[str, int]]:
    """Ingest every chart under data/charts/*.yaml -- the golden fixtures
    plus every named person's chart that has been promoted to a fixture.
    Run via `scripts/sync_db.py`, never automatically on every API request
    (ingestion is a deliberate, logged act, not an implicit side effect)."""
    return {chart_id: ingest_case(chart_id) for chart_id in list_fixture_ids()}
