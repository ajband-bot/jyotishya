"""Marriage Compatibility screen API (build_plan.md Phase 8 follow-up --
this closes the one item Phase 8's own note left explicitly undone: "a
dedicated Marriage Compatibility comparison screen").

Single endpoint, GET /api/v2/marriage-compatibility/{groom_chart_id}/{bride_chart_id},
composing every already-built Phase 4a/6 primitive into ONE response so the
frontend never has to orchestrate several separate calls (DRY -- and it
never reimplements anything: this module calls the exact same functions
app/api/v2/routes.py's own GET /compatibility/{groom}/{bride} and
GET /charts/{id}/marriage-timing already call).

`already_married` is a pure PRESENTATION switch (query param, no new
astrology): true -> each partner gets `married_life_status` (strengths/
cautions for an existing marriage, app.derived.marriage_analysis); false ->
each partner gets `marriage_timing` (upcoming Dasha/Transit/D9 Triple-
Agreement windows with a heuristic probability_percent + reason,
app.derived.marriage_timing -- its own disclosed "not a statistically
validated probability" caveat travels with it, per Cardinal Rule 9).
Ashtakuta/Mangal-Dosha/Synastry/D9-cross-compatibility are always returned
either way -- they are pure inter-chart compatibility metrics, not
marital-status-dependent.
"""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException

from app.api.v2.routes import _load_context
from app.derived.compatibility import ashtakuta_report
from app.derived.synastry import synastry_report, d9_cross_compatibility
from app.derived.marriage_timing import marriage_timing_report
from app.derived.marriage_analysis import married_life_status

router = APIRouter(prefix="/api/v2", tags=["marriage-compatibility"])


def _person_view(ctx: dict[str, Any], chart_id: str, already_married: bool, gender: str) -> dict[str, Any]:
    view: dict[str, Any] = {"chart_id": chart_id, "name": ctx["fixture"].get("name", chart_id)}
    if already_married:
        view["married_life_status"] = married_life_status(ctx)
    else:
        view["marriage_timing"] = marriage_timing_report(ctx, gender=gender)
    return view


@router.get("/marriage-compatibility/{groom_chart_id}/{bride_chart_id}")
async def api_marriage_compatibility(
    groom_chart_id: str, bride_chart_id: str, already_married: bool = False,
) -> dict[str, Any]:
    """Full Marriage Compatibility screen payload for two charts.

    `groom`/`bride` naming follows this codebase's existing convention
    (app.derived.compatibility, app.derived.synastry) -- it is a role label
    for which natural marriage karaka applies (Venus vs. Jupiter per
    BPHS Ch.32), not a claim about either native's actual gender identity.
    """
    if groom_chart_id == bride_chart_id:
        raise HTTPException(status_code=400, detail="groom_chart_id and bride_chart_id must refer to different charts")
    groom_ctx = _load_context(groom_chart_id)
    bride_ctx = _load_context(bride_chart_id)

    return {
        "groom_chart_id": groom_chart_id,
        "bride_chart_id": bride_chart_id,
        "already_married": already_married,
        "ashtakuta": ashtakuta_report(groom_ctx, bride_ctx),
        "synastry": synastry_report(groom_ctx, bride_ctx),
        "d9_cross_compatibility": d9_cross_compatibility(groom_ctx, bride_ctx),
        "groom": _person_view(groom_ctx, groom_chart_id, already_married, gender="male"),
        "bride": _person_view(bride_ctx, bride_chart_id, already_married, gender="female"),
    }
