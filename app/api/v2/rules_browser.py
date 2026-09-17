"""Rule Pack Browser API (build_plan.md Phase 8 -- "check any rule.yaml"
workbench ask).

Read-only. Every v2 rule pack (app/rules/generic_rules_pilot.yaml +
app/rules/compiled/*.yaml) is loaded through the SAME validated path the
rule engine itself uses (`app.rules.schema.Rule`) -- so what the browser
shows is guaranteed to be exactly what the evaluator would execute, never
a second hand-parsed view that could silently drift. The legacy v1 rich
rule-card pack (bphs_top20_rule_cards_v1.yaml) is listed for completeness
with a pointer to the existing GET /api/v2/reference/top-rules endpoint,
which already renders its full prose/citation detail -- no need to
duplicate that here (DRY).
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from fastapi import APIRouter, HTTPException

from app.rules.schema import Rule

router = APIRouter(prefix="/api/v2/rules", tags=["rule-packs"])

RULES_DIR = Path(__file__).resolve().parents[2] / "rules"
COMPILED_DIR = RULES_DIR / "compiled"
REPO_ROOT = RULES_DIR.parents[1]


def _v2_pack_paths() -> dict[str, Path]:
    packs = {"generic_rules_pilot": RULES_DIR / "generic_rules_pilot.yaml"}
    for path in sorted(COMPILED_DIR.glob("*.yaml")):
        packs[path.stem] = path
    return packs


def _load_v2_rules(path: Path) -> list[Rule]:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or []
    if not isinstance(data, list):
        raise ValueError(f"{path} is not a v2 rule pack (expected a YAML list)")
    return [Rule.model_validate(entry) for entry in data]


def list_rule_packs_data() -> dict[str, Any]:
    packs: list[dict[str, Any]] = []
    for pack_id, path in _v2_pack_paths().items():
        try:
            rules = _load_v2_rules(path)
        except Exception as exc:  # noqa: BLE001 -- surfaced as data, not a 500
            packs.append({
                "pack_id": pack_id, "kind": "v2_generic",
                "file": str(path.relative_to(REPO_ROOT)),
                "rule_count": 0, "categories": [], "status_counts": {},
                "size_bytes": path.stat().st_size, "error": str(exc),
            })
            continue
        status_counts: dict[str, int] = {}
        for rule in rules:
            status_counts[rule.status] = status_counts.get(rule.status, 0) + 1
        packs.append({
            "pack_id": pack_id, "kind": "v2_generic",
            "file": str(path.relative_to(REPO_ROOT)),
            "rule_count": len(rules),
            "categories": sorted({rule.category for rule in rules}),
            "status_counts": status_counts,
            "size_bytes": path.stat().st_size,
        })

    v1_path = RULES_DIR / "bphs_top20_rule_cards_v1.yaml"
    v1_data = yaml.safe_load(v1_path.read_text(encoding="utf-8")) or {}
    v1_cards = v1_data.get("rule_cards", [])
    packs.append({
        "pack_id": "bphs_top20_rule_cards_v1", "kind": "v1_legacy",
        "file": str(v1_path.relative_to(REPO_ROOT)),
        "rule_count": len(v1_cards), "categories": [], "status_counts": {},
        "size_bytes": v1_path.stat().st_size,
        "note": "Rich prose/citation format -- browse full detail via GET /api/v2/reference/top-rules.",
    })
    return {"packs": packs, "count": len(packs)}


def get_rule_pack_data(
    pack_id: str, category: str | None = None, status: str | None = None, search: str | None = None,
) -> dict[str, Any]:
    paths = _v2_pack_paths()
    if pack_id not in paths:
        raise KeyError(pack_id)
    rules = _load_v2_rules(paths[pack_id])
    if category:
        rules = [r for r in rules if r.category == category]
    if status:
        rules = [r for r in rules if r.status == status]
    if search:
        needle = search.lower()
        rules = [r for r in rules if needle in r.id.lower() or needle in r.title.lower()]
    return {"pack_id": pack_id, "rule_count": len(rules), "rules": [r.model_dump() for r in rules]}


@router.get("/packs")
async def api_list_rule_packs() -> dict[str, Any]:
    """Every rule YAML file this project ships, v1 and v2 alike, with rule
    counts and status/category breakdowns -- so a rule pack can be
    inspected without opening a 100-200KB file in an editor."""
    return list_rule_packs_data()


@router.get("/packs/{pack_id}")
async def api_get_rule_pack(
    pack_id: str, category: str | None = None, status: str | None = None, search: str | None = None,
) -> dict[str, Any]:
    """Full rule list (id/title/category/status/confidence/conditions/
    outputs/source_ref/notes) for one v2 pack, optionally filtered."""
    try:
        return get_rule_pack_data(pack_id, category=category, status=status, search=search)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Unknown v2 rule pack: {pack_id}")
