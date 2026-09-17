"""Narrative Composer v1 (build_plan.md §4 / Phase 3).

Replaces LLM steps 3-6 of AGENTS.md's Process (load style reference ->
generate Parts -> verify -> summarize) for the sections it covers: for
every matched, ACTIVE rule, render its outputs[] payload through the
category's Jinja template -- deterministic, byte-identical for the same
chart on every run (AD-2/AD-3: no non-deterministic LLM prose for content
that must never vary for a fixed chart+rule-set).

Phase 3 v1 scope is deliberately 3 sections (lagna, dosha, yoga), per
build_plan.md's own checklist -- NOT all 7 sections sketched in build_plan
§4.1's design diagram (marriage/career/remedy/dasha_period are later
Composer iterations, gated on their own rule content existing in
meaningful volume first). Every section the composer does NOT yet cover is
exactly what `gap_report.py` is for -- it is not silently absent, it is a
reported gap.

Composed vs. gap: for every rule that DID match, the template renders it.
For every rule that COULD have mattered but hit `data_gap`, `gap_report`
surfaces it as a ticket. Nothing is invented to fill space -- an empty
section with zero matched rules renders as exactly that (see templates),
never papered over with placeholder prose.
"""
from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any

import jinja2

from app.astro.constants import SIGNS
from app.derived.factors import build_chart_context
from app.engine.narrative.gap_report import build_gap_report
from app.fixtures import load_chart_fixture
from app.rules.loader import load_compiled_rule_packs, load_generic_rule_pack
from app.rules.priority import evaluate_and_prioritize
from app.rules.schema import Rule

TEMPLATE_DIR = Path(__file__).with_name("templates")
_ENV = jinja2.Environment(
    loader=jinja2.FileSystemLoader(TEMPLATE_DIR),
    autoescape=True,
    trim_blocks=True,
    lstrip_blocks=True,
)


def _default_rules() -> list[Rule]:
    return load_compiled_rule_packs() + load_generic_rule_pack()


def _sign_en(sign_no: int) -> str:
    return SIGNS[sign_no - 1]["en"]


def _display_context(ctx: dict[str, Any]) -> dict[str, Any]:
    """Precompute human-readable labels once, in Python -- templates stay
    dumb (no astrology lookups inside Jinja, matching build_plan §4.2's
    reasoning that ALL Jyotisha knowledge belongs in data/engines, not
    scattered into template logic)."""
    lagna_sign = ctx["lagna_sign"]
    lagna_lord = ctx["house_lords"][1]
    return {
        "lagna_sign_en": _sign_en(lagna_sign),
        "lagna_lord": lagna_lord,
        "lagna_lord_house": ctx["chart"][lagna_lord]["house"],
        "lagna_lord_classification": ctx["functional_nature"]["planets"].get(lagna_lord, {}).get("classification"),
        "moon_sign_en": _sign_en(ctx["chart"]["Moon"]["sign"]),
    }


def _matched_records(records: list[dict[str, Any]], category: str, extra_filter=None) -> list[dict[str, Any]]:
    out = []
    for record in records:
        if record["rule"].category != category or not record["evaluation"].matched:
            continue
        if extra_filter and not extra_filter(record):
            continue
        out.append(record)
    return out


def render_lagna_section(display: dict[str, Any], records: list[dict[str, Any]]) -> str:
    lagna_records = _matched_records(
        records, "lord_placement",
        extra_filter=lambda r: r["evaluation"].outputs and r["evaluation"].outputs[0].payload.get("source_house") == 1,
    )
    template = _ENV.get_template("lagna.jinja")
    return template.render(display=display, records=[r["evaluation"] for r in lagna_records])


def render_dosha_section(records: list[dict[str, Any]]) -> str:
    dosha_records = _matched_records(records, "dosha")
    # Sade Sati (DSH-015) is category "transit" (see generate_dosha_rules.py's
    # own honest note), but the Validation Document's doṣa register section
    # (docs/validation-document-spec.md §1 item 9/15) reports it alongside
    # the other doṣas -- fold it in for rendering purposes only, without
    # reclassifying its actual RuleCategory.
    sade_sati_records = [r for r in records if r["rule"].id == "DSH-015" and r["evaluation"].matched]
    template = _ENV.get_template("dosha.jinja")
    return template.render(records=[r["evaluation"] for r in (dosha_records + sade_sati_records)])


def render_yoga_section(records: list[dict[str, Any]]) -> str:
    yoga_records = _matched_records(records, "yoga")
    template = _ENV.get_template("yoga.jinja")
    return template.render(records=[r["evaluation"] for r in yoga_records])


def compose_chart_narrative(chart_id: str, rules: list[Rule] | None = None, today: date | None = None) -> dict[str, Any]:
    fixture = load_chart_fixture(chart_id)
    context = build_chart_context(fixture, today=today)
    rules = rules if rules is not None else _default_rules()
    records = evaluate_and_prioritize(rules, context)
    display = _display_context(context)

    sections = {
        "lagna": render_lagna_section(display, records),
        "dosha": render_dosha_section(records),
        "yoga": render_yoga_section(records),
    }
    gap_report = build_gap_report(rules, context, chart_id)

    return {
        "chart_id": chart_id,
        "sections": sections,
        "gap_report": gap_report,
        "rule_count_evaluated": len(records),
        "rule_count_matched": sum(1 for r in records if r["evaluation"].matched),
    }
