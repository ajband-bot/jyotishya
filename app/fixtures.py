from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


FIXTURE_DIR = Path(__file__).resolve().parents[1] / "data" / "charts"


def load_chart_fixture(chart_id: str) -> dict[str, Any]:
    path = FIXTURE_DIR / f"{chart_id}.yaml"
    with open(path, "r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"Chart fixture {chart_id} is invalid")
    return data


def list_fixture_ids() -> list[str]:
    """All chart_ids with a fixture file, for name-matching (e.g. the
    Cheat-Sheet extractor resolving 'Ajay' -> 'ajay_kumar')."""
    return sorted(p.stem for p in FIXTURE_DIR.glob("*.yaml"))


def resolve_chart_id_by_name(mentioned_name: str) -> str | None:
    """Fuzzy-match a first-name mention (e.g. 'Ajay', 'Sandeep') against
    fixture 'name' fields. Returns the chart_id or None if no unambiguous
    match is found."""
    mentioned_lower = mentioned_name.strip().lower()
    matches = []
    for chart_id in list_fixture_ids():
        try:
            fixture = load_chart_fixture(chart_id)
        except Exception:
            continue
        full_name = str(fixture.get("name", "")).lower()
        if mentioned_lower and mentioned_lower in full_name.split():
            matches.append(chart_id)
    if len(matches) == 1:
        return matches[0]
    return None
