"""Chart creation API (build_plan.md Phase 8 -- "generate a new horoscope
from DOB/TOB/lat/lon" workbench ask).

Mirrors AGENTS.md Step 0 (Input Lock): name/dob/tob/utc_offset/lat/lon are
the mandatory fields -- FastAPI/pydantic rejects a request missing any of
them with a 422 before `create_chart_fixture` ever runs.

Writes exactly the same data/charts/{id}.yaml fixture format every other
chart in this repo already uses (never a second, parallel storage format --
DRY), upserts the `charts` DB row via the existing app.db.models helpers,
and immediately runs the Phase 7 case-ingestion pipeline so the new chart
is queryable via /api/v2/cases/* and the DB Browser right away.

Business logic lives in plain functions (`create_chart_fixture`) so it can
be unit-tested directly, without spinning up an HTTP client -- same
testing style already used for the rest of this codebase's `app/derived/*`
modules.
"""
from __future__ import annotations

import re
from datetime import date
from pathlib import Path
from typing import Any

import yaml
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.db import models
from app.db.ingest import ingest_case
from app.derived.factors import build_chart_context
from app.fixtures import FIXTURE_DIR, list_fixture_ids

router = APIRouter(prefix="/api/v2/charts", tags=["chart-create"])


class NewChartRequest(BaseModel):
    name: str = Field(min_length=1, description="Native's full name")
    dob: date = Field(description="Birth date, YYYY-MM-DD")
    tob: str = Field(pattern=r"^\d{2}:\d{2}(:\d{2})?$", description="Local birth time, HH:MM or HH:MM:SS")
    utc_offset: float = Field(ge=-12, le=14, description="Hours east of UTC, e.g. 5.5 for IST")
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    place: str = ""
    ayanamsha: str = "lahiri"
    node_type: str = "mean"
    house_system: str = "whole_sign"
    notes: list[str] = Field(default_factory=list)


def _slugify(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", name.strip().lower()).strip("_")
    return slug or "chart"


def _unique_chart_id(base: str) -> str:
    """Never silently overwrite an existing chart -- append a numeric
    suffix until the id is free, same discipline as everywhere else in
    this codebase that refuses to guess/clobber (Cardinal Rule 2)."""
    existing = set(list_fixture_ids())
    if base not in existing:
        return base
    suffix = 2
    while f"{base}_{suffix}" in existing:
        suffix += 1
    return f"{base}_{suffix}"


def create_chart_fixture(req: NewChartRequest) -> dict[str, Any]:
    """Full create pipeline: write fixture YAML -> compute a real chart
    context (fails loudly and cleans up if computation errors, never
    leaves a half-written unusable fixture behind) -> upsert DB row ->
    ingest into the Phase 7 case_* tables. Returns a small preview, not
    the full context -- the caller re-fetches via the normal chart
    endpoints (single source of truth, no duplicate response shape)."""
    tob_full = req.tob if len(req.tob) == 8 else f"{req.tob}:00"
    chart_id = _unique_chart_id(_slugify(req.name))
    fixture: dict[str, Any] = {
        "chart_id": chart_id,
        "name": req.name,
        "dob": req.dob.isoformat(),
        "time_local": tob_full,
        "timezone": f"UTC{req.utc_offset:+g}",
        "utc_offset": req.utc_offset,
        "location": {
            "place": req.place or "Unspecified",
            "latitude": req.latitude,
            "longitude": req.longitude,
        },
        "settings": {
            "ayanamsha": req.ayanamsha,
            "node_type": req.node_type,
            "house_system": req.house_system,
        },
        "notes": req.notes or ["Created via Workbench chart-creation form."],
    }

    path = FIXTURE_DIR / f"{chart_id}.yaml"
    with open(path, "w", encoding="utf-8") as handle:
        yaml.safe_dump(fixture, handle, allow_unicode=True, sort_keys=False)

    try:
        ctx = build_chart_context(fixture)
    except Exception as exc:  # noqa: BLE001 -- surfaced to caller as a 400, never swallowed
        path.unlink(missing_ok=True)
        raise ValueError(f"Chart computation failed for the given inputs: {exc}") from exc

    models.upsert_chart({
        "id": chart_id,
        "name": req.name,
        "dob": fixture["dob"],
        "tob": tob_full,
        "utc_offset": req.utc_offset,
        "latitude": req.latitude,
        "longitude": req.longitude,
        "ayanamsha": req.ayanamsha,
        "node_type": req.node_type,
        "house_system": req.house_system,
        "notes": "; ".join(fixture["notes"]),
    })
    ingested = ingest_case(chart_id, ctx=ctx)

    return {
        "chart_id": chart_id,
        "fixture_path": str(Path("data/charts") / f"{chart_id}.yaml"),
        "lagna_sign": ctx["lagna_sign"],
        "current_dasha": ctx["current_dasha"],
        "ingested": ingested,
    }


@router.post("")
async def create_chart(req: NewChartRequest) -> dict[str, Any]:
    """Generate a brand-new horoscope from DOB/TOB/lat/lon (AGENTS.md Step
    0 Input Lock). On success, the chart is immediately available at every
    other /api/v2/charts/{chart_id}/* endpoint and in /api/v2/cases/*."""
    try:
        return create_chart_fixture(req)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
