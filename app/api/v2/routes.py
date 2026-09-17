"""Workbench API v2 -- the interactive-app surface described in
docs/technical-architecture.md 4.8.

Additive only: app/api/routes.py (Jinja2-serving, narrative-pipeline-facing)
is untouched. This router is mounted separately in app/main.py under
/api/v2/ and returns JSON only -- the frontend never computes Jyotisha
logic itself (spec non-negotiable, repeated in architecture.md 3).
"""
from __future__ import annotations

from datetime import date
from typing import Any

from fastapi import APIRouter, HTTPException

from app.astro.vargas import SUPPORTED_VARGAS, VARGA_META, compute_all_vargas, compute_varga
from app.db.models import get_chart, list_charts, seed_charts_from_fixtures
from app.derived.factors import build_chart_context
from app.derived.reference_tables import (
    get_dignity_table,
    get_functional_nature_grid,
    get_house_themes,
    get_lord_placement_connections,
    get_natural_relationships,
    get_planet_lab,
    get_dasha_reference,
    get_transit_reference,
    get_top_rules,
    get_planet_relationship_graph,
)
from app.derived.doshas import compute_all_doshas
from app.derived.compatibility import ashtakuta_report
from app.derived.synastry import synastry_report, d9_cross_compatibility
from app.derived.marriage_timing import marriage_timing_report
from app.derived.sandbox import SandboxRequest, analyze_sandbox
from app.derived.chartlab_time import SandboxDashaRequest, SandboxTransitRequest, sandbox_dasha, sandbox_transits
from app.engine.cheatsheet.differ import validate_claims
from app.engine.cheatsheet.extractor import extract_all_claims
from app.engine.cheatsheet.concepts import CONCEPTS, concepts_by_category
from app.fixtures import load_chart_fixture
from app.db import query as db_query
from pydantic import BaseModel
from app.rules.generic_evaluator import evaluate_rule_set
from app.rules.loader import load_generic_rule_pack

router = APIRouter(prefix="/api/v2", tags=["workbench-v2"])


def _load_context(chart_id: str) -> dict[str, Any]:
    try:
        fixture = load_chart_fixture(chart_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Unknown chart_id: {chart_id}")
    return build_chart_context(fixture)


@router.get("/charts")
async def api_list_charts() -> dict[str, Any]:
    """List all persisted charts. Seeds from data/charts/*.yaml on first call."""
    charts = list_charts()
    if not charts:
        seed_charts_from_fixtures()
        charts = list_charts()
    return {"charts": charts, "count": len(charts)}


@router.get("/charts/{chart_id}")
async def api_get_chart(chart_id: str) -> dict[str, Any]:
    """Full D1 + all vargas + dashas + transits for one chart."""
    ctx = _load_context(chart_id)
    vargas = compute_all_vargas(ctx["chart"])
    return {
        "chart_id": chart_id,
        "settings": {
            "ayanamsha": ctx["fixture"].get("settings", {}).get("ayanamsha", "lahiri"),
            "node_type": ctx["fixture"].get("settings", {}).get("node_type", "mean"),
            "house_system": ctx["fixture"].get("settings", {}).get("house_system", "whole_sign"),
        },
        "d1": ctx["chart"],
        "vargas": vargas,
        "dashas": ctx["dashas"],
        "current_dasha": ctx["current_dasha"],
        "transits": ctx["transits"],
        "house_lords": ctx["house_lords"],
        "yoga_karakas": ctx["yoga_karakas"],
    }


@router.get("/charts/{chart_id}/vargas/{n}")
async def api_get_varga(chart_id: str, n: int) -> dict[str, Any]:
    if n not in VARGA_META:
        raise HTTPException(
            status_code=400,
            detail=f"D{n} is not supported. Supported vargas: {list(SUPPORTED_VARGAS)}",
        )
    ctx = _load_context(chart_id)
    return compute_varga(ctx["chart"], n)


@router.get("/charts/{chart_id}/rules")
async def api_get_rules(chart_id: str) -> dict[str, Any]:
    """Rule Engine v2 evaluation -- the generic, data-driven path.

    Note: this runs the NEW pilot pack (app/rules/generic_rules_pilot.yaml).
    The legacy rich rule pack stays reachable at the original
    /api/rules/{chart_id} endpoint (app/api/routes.py) unchanged.
    """
    ctx = _load_context(chart_id)
    rules = load_generic_rule_pack()
    evaluations = evaluate_rule_set(rules, ctx)
    return {
        "chart_id": chart_id,
        "engine": "rule_engine_v2_generic",
        "evaluations": [e.model_dump() for e in evaluations],
    }


@router.get("/charts/{chart_id}/validation-screen")
async def api_validation_screen(chart_id: str) -> dict[str, Any]:
    """Chart Integrity screen data (spec 15) -- shown before any interpretation."""
    ctx = _load_context(chart_id)
    settings = ctx["fixture"].get("settings", {})
    warnings = []
    if not settings.get("ayanamsha"):
        warnings.append("Ayanamsha not explicitly set -- defaulting to Lahiri.")
    warnings.append("D60 is highly time-sensitive -- verify birth time precision before trusting D60-only claims.")
    return {
        "chart_id": chart_id,
        "checks": {
            "birth_data": True,
            "ayanamsha": settings.get("ayanamsha", "lahiri"),
            "house_system": settings.get("house_system", "whole_sign"),
            "node_type": settings.get("node_type", "mean"),
            "d1": True,
            "d9": True,
            "vimshottari": bool(ctx["dashas"]),
            "current_mahadasha": ctx["current_dasha"].get("mahadasha", {}).get("planet"),
        },
        "warnings": warnings,
    }


@router.get("/charts/{chart_id}/coverage")
async def api_chart_coverage(chart_id: str) -> dict[str, Any]:
    """Rule Coverage %% / Evidence Traceability %% / Unsupported Claim Count
    (build_plan.md §9's "Internal document should generate these metrics"
    ask) for one chart, evaluated against every compiled v2 rule pack.
    `app.rules.priority.coverage_report()` already computed all of this --
    it was simply never wired to an API endpoint until now. Powers the
    Workbench's Validate tab alongside the existing validation-screen and
    doshas endpoints."""
    from app.rules.loader import load_compiled_rule_packs
    from app.rules.priority import coverage_report

    ctx = _load_context(chart_id)
    rules = load_compiled_rule_packs()
    return {"chart_id": chart_id, **coverage_report(rules, ctx)}


@router.get("/charts/{chart_id}/full-context")
async def api_full_context(chart_id: str) -> dict[str, Any]:
    """Every derived layer build_chart_context() computes for one chart, in
    a single response -- powers the Chart Workbench's tabbed sections
    (Vargas, Vimsottari, Aspects, Ashtakavarga, Doshas/Yogas, Panchanga,
    Graha Maitri, Argala, Nakshatras, Shadbala, Vimsopaka, Bhava Bala,
    Gochara, Marriage/Career/Remedies) as pure client-side views over ONE
    already-computed context, instead of one bespoke endpoint per section
    (DRY -- this project's context dict is already the single source of
    truth; the tabs should read it, not re-derive a parallel shape of it).
    """
    ctx = _load_context(chart_id)
    keys = [
        "lagna_sign", "house_lords", "maraka_lords", "karakas", "lagna_pada",
        "upapada", "combustion", "shadbala", "shadbala_classical",
        "varga_quality", "ishta_kashta", "ishta_kashta_classical", "argala",
        "ashtakavarga", "panchanga", "aspects", "graha_maitri", "yoga_karakas",
        "house_graph", "functional_nature", "dispositors", "lord_placements",
        "doshas", "avasthas", "bhava_bala", "yogas", "nakshatra_analysis",
        "bhavapada", "dasha_synthesis", "gochara", "vimsopaka",
        "marriage_analysis", "career_analysis", "remedies",
    ]
    return {"chart_id": chart_id, **{k: ctx[k] for k in keys if k in ctx}}


@router.get("/vargas/meta")
async def api_vargas_meta() -> dict[str, Any]:
    """Static metadata for all supported vargas -- powers the Cross-Varga Heat Map."""
    return {"supported": list(SUPPORTED_VARGAS), "meta": VARGA_META}


# --------------------------------------------------------------------------
# Learning / Cheat-Sheet reference endpoints -- chart-INDEPENDENT fundamentals
# (spec 7.1 Functional Nature Heat Map, 7.2 House Theme Explorer,
# 7.3 Lord Placement Matrix, classical dignity + friend/enemy tables).
# --------------------------------------------------------------------------

@router.get("/reference/house-themes")
async def api_house_themes() -> dict[str, Any]:
    return {"houses": get_house_themes()}


@router.get("/reference/natural-relationships")
async def api_natural_relationships() -> dict[str, Any]:
    return get_natural_relationships()


@router.get("/reference/dignity-table")
async def api_dignity_table() -> dict[str, Any]:
    return {"dignity": get_dignity_table()}


@router.get("/reference/functional-nature-grid")
async def api_functional_nature_grid() -> dict[str, Any]:
    return get_functional_nature_grid()


@router.get("/reference/lord-placement-connections/{lagna_sign}")
async def api_lord_placement_connections(lagna_sign: int) -> dict[str, Any]:
    if not 1 <= lagna_sign <= 12:
        raise HTTPException(status_code=400, detail="lagna_sign must be 1-12")
    return get_lord_placement_connections(lagna_sign)


@router.get("/reference/dasha-system")
async def api_dasha_system() -> dict[str, Any]:
    """Vimsottari order, durations, and full Antardasha tables for every
    Mahadasha planet -- chart-independent doctrine reference."""
    return get_dasha_reference()


@router.get("/reference/transit-impacts")
async def api_transit_impacts() -> dict[str, Any]:
    """Classical Jupiter/Saturn Gochara doctrine from Moon, plus Sade Sati
    phase structure -- chart-independent doctrine reference."""
    return get_transit_reference()


@router.get("/reference/top-rules")
async def api_top_rules() -> dict[str, Any]:
    """The structured BPHS rule-card corpus (20 of a planned 30), grouped
    by domain for the Learning tab's mindmap/card view."""
    return get_top_rules()


@router.get("/reference/planet-relationship-graph")
async def api_planet_relationship_graph() -> dict[str, Any]:
    """Nodes/edges shape of the natural friend/enemy table for graph
    (React Flow) rendering."""
    return get_planet_relationship_graph()


@router.post("/sandbox/analyze")
async def api_sandbox_analyze(req: SandboxRequest) -> dict[str, Any]:
    """Chart Lab -- analyze a hypothetical (non-birth-data) chart built by
    dragging Lagna + planets onto a South Indian grid. Never persisted;
    every response is a fresh computation from the exact same engine real
    charts use, honestly flagging what a hypothetical chart cannot know
    (dashas, real transits) as data_gap."""
    try:
        return analyze_sandbox(req)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/sandbox/dasha")
async def api_sandbox_dasha(req: SandboxDashaRequest) -> dict[str, Any]:
    """Chart Lab v2 Sprint 2 -- Vimsottari MD/AD/PD for a hypothetical
    Moon position + user-supplied birth date. Refuses to compute (mode:
    manual_required) if no birth date is given, rather than fabricating
    dates -- frontend falls back to manual MD/AD/PD dropdowns."""
    return sandbox_dasha(req)


@router.post("/sandbox/transits")
async def api_sandbox_transits(req: SandboxTransitRequest) -> dict[str, Any]:
    """Chart Lab v2 Sprint 3 -- real Swiss Ephemeris transit positions for
    a calendar date, with house-from-Lagna/house-from-Moon/dignity/aspects
    computed against the user's hypothetical chart. No birth data needed."""
    return sandbox_transits(req)


@router.get("/charts/{chart_id}/planet-lab")
async def api_planet_lab(chart_id: str) -> dict[str, Any]:
    """Planet Lab (spec 7.4) -- transparent per-graha profile for ONE real
    chart: sign/house/dignity/combustion/D9-state/functional-role/Shadbala
    breakdown/Ishta-Kashta, all reusing the same context every other
    endpoint uses."""
    ctx = _load_context(chart_id)
    result = get_planet_lab(ctx)
    return {"chart_id": chart_id, **result}


@router.get("/charts/{chart_id}/doshas")
async def api_doshas(chart_id: str) -> dict[str, Any]:
    """Full doṣa register (docs/dosha-registry.md) for one chart -- the 8
    mandatory checks that previously existed only as prose."""
    ctx = _load_context(chart_id)
    return {"chart_id": chart_id, "doshas": compute_all_doshas(ctx), "sade_sati": ctx["transits"].get("saturn_assessment", {}).get("sade_sati")}


@router.get("/compatibility/{groom_chart_id}/{bride_chart_id}")
async def api_compatibility(groom_chart_id: str, bride_chart_id: str) -> dict[str, Any]:
    """Full marriage-compatibility report for two charts (build_plan.md
    Phase 4a): Ashtakuta (8-kuta Guna Milan) + Mangal Dosha matching,
    7-indicator synastry, and D9 cross-compatibility. Marriage TIMING for
    a single chart is a separate endpoint (needs a gender, not a second
    chart) -- see GET /charts/{chart_id}/marriage-timing."""
    groom_ctx = _load_context(groom_chart_id)
    bride_ctx = _load_context(bride_chart_id)
    return {
        "groom_chart_id": groom_chart_id, "bride_chart_id": bride_chart_id,
        "ashtakuta": ashtakuta_report(groom_ctx, bride_ctx),
        "synastry": synastry_report(groom_ctx, bride_ctx),
        "d9_cross_compatibility": d9_cross_compatibility(groom_ctx, bride_ctx),
    }


@router.get("/charts/{chart_id}/marriage-timing")
async def api_marriage_timing(chart_id: str, gender: str = "male", years: int = 30) -> dict[str, Any]:
    """Dasha/Transit/D9 Triple Agreement marriage-timing windows
    (build_plan.md Phase 4a, Marriage_Guide_Part3.md) for one chart.
    `gender` selects the natural marriage karaka (Venus for male, Jupiter
    for female, per BPHS Ch.32) -- required since it cannot be inferred
    from chart data alone."""
    if gender not in ("male", "female"):
        raise HTTPException(status_code=400, detail="gender must be 'male' or 'female'")
    ctx = _load_context(chart_id)
    return {"chart_id": chart_id, **marriage_timing_report(ctx, gender=gender, years=years)}


@router.get("/cheatsheet/claims")
async def api_cheatsheet_claims(verdict: str | None = None, source_file: str | None = None) -> dict[str, Any]:
    """Cheat-Sheet Cross-Validation Console (docs/technical-architecture.md
    4.4): every extracted claim from the corpus, validated against computed
    truth, filterable by verdict/source."""
    claims = extract_all_claims()
    results = validate_claims(claims)
    if verdict:
        results = [r for r in results if r.verdict == verdict]
    if source_file:
        results = [r for r in results if source_file in r.claim.source_file]
    counts: dict[str, int] = {}
    for r in validate_claims(claims):
        counts[r.verdict] = counts.get(r.verdict, 0) + 1
    return {
        "total_claims": len(claims),
        "verdict_counts": counts,
        "results": [r.model_dump() for r in results],
    }


@router.get("/cheatsheet/concepts")
async def api_cheatsheet_concepts(category: str | None = None) -> dict[str, Any]:
    """The Phase 7 learning-platform concept registry
    (app/engine/cheatsheet/concepts.py) -- every classical Jyotisha concept
    this project implements, with citation, code_ref, quality_label, and
    caveats. This is the same data rendered into docs/JYOTISHA_CHEATSHEET.md
    by scripts/generate_cheatsheet.py, and mirrored into the queryable
    `cheatsheet_concepts` DB table by scripts/sync_db.py -- three views of
    one source, never three sources to keep in sync by hand."""
    grouped = concepts_by_category()
    if category:
        entries = grouped.get(category, [])
        return {"category": category, "count": len(entries), "concepts": [c.model_dump() for c in entries]}
    return {
        "categories": sorted(grouped.keys()),
        "total_concepts": len(CONCEPTS),
        "concepts": [c.model_dump() for c in CONCEPTS],
    }


# --------------------------------------------------------------------------
# Case facts (build_plan.md Phase 7 "DB wiring for every case") -- every
# follow-up question about a specific person's chart answered via SQL
# (app/db/query.py) against app/db/ingest.py's pre-computed case_* tables,
# never by re-opening output/*.html reading files.
# --------------------------------------------------------------------------

class CaseQARequest(BaseModel):
    question: str
    answer: str
    source_refs: str = ""


@router.get("/cases")
async def api_list_cases() -> dict[str, Any]:
    """Every chart currently ingested into the case_* DB tables -- run
    `scripts/sync_db.py` to (re)populate after adding/changing a fixture."""
    cases = db_query.list_all_cases()
    return {"cases": cases, "count": len(cases)}


@router.get("/cases/{chart_id}")
async def api_case_summary(chart_id: str) -> dict[str, Any]:
    """DB-backed case summary: metadata + planets + dashas + doshas + yogas
    + remedies, straight from SQL -- the literal answer to 'don't make me
    read a long HTML file to check this person's case details.'"""
    summary = db_query.get_case_summary(chart_id)
    if not summary["chart"]:
        raise HTTPException(status_code=404, detail=f"'{chart_id}' has not been ingested yet -- run scripts/sync_db.py")
    return summary


@router.get("/cases/{chart_id}/current-dasha")
async def api_case_current_dasha(chart_id: str) -> dict[str, Any]:
    return {"chart_id": chart_id, "current": db_query.get_current_dasha(chart_id)}


@router.get("/cases/{chart_id}/active-doshas")
async def api_case_active_doshas(chart_id: str) -> dict[str, Any]:
    return {"chart_id": chart_id, "active_doshas": db_query.get_active_doshas(chart_id)}


@router.get("/cases/{chart_id}/active-yogas")
async def api_case_active_yogas(chart_id: str) -> dict[str, Any]:
    return {"chart_id": chart_id, "active_yogas": db_query.get_active_yogas(chart_id)}


@router.get("/cases/{chart_id}/qa")
async def api_case_qa_list(chart_id: str, search: str | None = None) -> dict[str, Any]:
    """Every follow-up Q&A ever logged for this case -- a repeated or
    closely related question should surface a prior answer here instead of
    triggering a fresh re-derivation. `search` does a simple substring
    match over both question and answer text."""
    entries = db_query.search_qa(chart_id, search) if search else db_query.list_qa(chart_id)
    return {"chart_id": chart_id, "qa": entries, "count": len(entries)}


@router.post("/cases/{chart_id}/qa")
async def api_case_qa_log(chart_id: str, req: CaseQARequest) -> dict[str, Any]:
    """Persist a follow-up question + its answer for this case (e.g. once
    an LLM session or human resolves a question by re-checking computed
    output), so the NEXT time the same question comes up it's a SQL lookup,
    not a re-read of the original reading files."""
    qa_id = db_query.log_qa(chart_id, req.question, req.answer, req.source_refs)
    return {"chart_id": chart_id, "qa_id": qa_id, "logged": True}
