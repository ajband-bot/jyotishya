"""Full-resync helpers for the ENGINE-state tables (build_plan.md Phase 7:
"wire cheatsheet_claims, rule_versions, analysis_snapshots tables live").

Unlike app/db/ingest.py (per-chart_id case facts), these three describe the
state of the ENGINE itself -- what rules exist, what claims the corpus
makes and whether they currently hold, what concepts the learning registry
covers -- so each sync here is a full wipe+reload, run explicitly via
`scripts/sync_db.py`, never as an implicit side effect of an API request.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from app.db import models
from app.engine.cheatsheet.differ import validate_claims
from app.engine.cheatsheet.extractor import extract_all_claims


def sync_cheatsheet_claims() -> int:
    """Run the full extractor+differ pass and persist every result into the
    `cheatsheet_claims` table, with a live-validated timestamp -- moves the
    Cross-Validation Console from compute-on-every-request to a queryable,
    audited table (the literal Phase 7 checklist item)."""
    claims = extract_all_claims()
    results = validate_claims(claims)
    now = datetime.now(timezone.utc)
    rows = [
        {
            "source_file": r.claim.source_file,
            "section": r.claim.section,
            "claim_text": r.claim.claim_text,
            "formula_ref": r.claim.formula_ref,
            "applies_to_chart": r.claim.applies_to_chart,
            "last_validated_at": now,
            "last_verdict": r.verdict,
        }
        for r in results
    ]
    return models.replace_cheatsheet_claims(rows)


def sync_rule_versions() -> int:
    """One row per compiled v2 rule (all 10 packs under app/rules/compiled/
    plus the generic_rules_pilot.yaml pack) -- gives every rule a queryable
    (rule_id, version, status) row instead of requiring a fresh YAML parse
    every time someone asks 'what status is rule X at'."""
    from app.rules.loader import load_compiled_rule_packs, load_generic_rule_pack

    rules = load_compiled_rule_packs() + load_generic_rule_pack()
    rows = [
        {
            "rule_id": rule.id,
            "version": 1,
            "status": rule.status,
            "payload_json": json.dumps(rule.model_dump(), default=str),
            "created_by": "sync_db",
        }
        for rule in rules
    ]
    return models.replace_rule_versions(rows)


def sync_cheatsheet_concepts() -> int:
    """One row per app.engine.cheatsheet.concepts.CONCEPTS entry -- the
    learning-platform registry, made queryable (e.g. 'show me every
    data_gap concept', 'show me every dosha with a pending citation audit')
    without importing Python or re-reading concepts.py."""
    from app.engine.cheatsheet.concepts import CONCEPTS

    rows = [
        {
            "concept_id": c.concept_id,
            "category": c.category,
            "sanskrit_term": c.sanskrit_term,
            "english_gloss": c.english_gloss,
            "classical_definition": c.classical_definition,
            "primary_citation": c.primary_citation,
            "code_ref": c.code_ref,
            "quality_label": c.quality_label,
            "caveats": "; ".join(c.caveats),
            "cross_check_note": c.cross_check_note,
        }
        for c in CONCEPTS
    ]
    return models.replace_cheatsheet_concepts(rows)


def sync_all() -> dict[str, int]:
    return {
        "rule_versions": sync_rule_versions(),
        "cheatsheet_claims": sync_cheatsheet_claims(),
        "cheatsheet_concepts": sync_cheatsheet_concepts(),
    }
