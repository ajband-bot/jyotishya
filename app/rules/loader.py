from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


def load_yaml(path: str | Path) -> Any:
    with open(path, "r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def load_rule_pack(path: str | Path | None = None) -> dict:
    target = Path(path) if path else Path(__file__).with_name("bphs_top20_rule_cards_v1.yaml")
    data = load_yaml(target)
    if not isinstance(data, dict):
        raise ValueError(f"Rule pack at {target} did not load as a mapping")
    return data


def load_generic_rule_pack(path: str | Path | None = None) -> list:
    """Load a Rule Engine v2 structured pack (list of Rule-shaped dicts) and
    validate every entry against app.rules.schema.Rule.

    Unlike load_rule_pack() (v1, rich prose format), this returns a list of
    validated Rule objects ready for app.rules.generic_evaluator.
    """
    from app.rules.schema import Rule

    target = Path(path) if path else Path(__file__).with_name("generic_rules_pilot.yaml")
    data = load_yaml(target)
    if not isinstance(data, list):
        raise ValueError(f"Generic rule pack at {target} must be a list of rule entries")
    return [Rule.model_validate(entry) for entry in data]


def load_compiled_rule_packs(directory: str | Path | None = None) -> list:
    """Load every generated v2 rule pack under app/rules/compiled/ (build_plan.md
    Phase 2: planet-in-house, house-lord-placement, planet-in-sign, dosha).

    Each file is produced by app.rules.generators.emit_all and validated the
    same way as load_generic_rule_pack -- this is purely an aggregation
    convenience so callers (tests, the future Narrative Composer) don't need
    to know the individual filenames.
    """
    from app.rules.schema import Rule

    target_dir = Path(directory) if directory else Path(__file__).with_name("compiled")
    rules: list = []
    for yaml_path in sorted(target_dir.glob("*.yaml")):
        data = load_yaml(yaml_path)
        if not isinstance(data, list):
            raise ValueError(f"Compiled rule pack at {yaml_path} must be a list of rule entries")
        rules.extend(Rule.model_validate(entry) for entry in data)
    return rules
