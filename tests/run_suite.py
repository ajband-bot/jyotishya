from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from dataclasses import dataclass
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.derived.factors import build_chart_context
from app.fixtures import load_chart_fixture
from app.rules.evaluator import evaluate_chart_fixture


BASELINE_PATH = ROOT / "tests" / "baselines" / "fixture_regression_baseline.json"
CRITICAL_DATE = date(2026, 4, 11)
LOCKED_FIXTURES = ("ajay_kumar", "sandeep_0700")
ALLOWED_QUALITIES = {"computed", "computed_simplified", "computed_with_conflict", "data_gap"}


@dataclass
class CheckResult:
    name: str
    passed: bool
    details: str


def _rule_map(evaluations: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {row["rule_id"]: row for row in evaluations}


def _quality_counts(evaluations: list[dict[str, str]]) -> dict[str, int]:
    return dict(Counter(row["quality"] for row in evaluations))


def build_snapshot(chart_id: str, on_date: date) -> dict[str, Any]:
    fixture = load_chart_fixture(chart_id)
    context = build_chart_context(fixture, today=on_date)
    evaluation = evaluate_chart_fixture(chart_id, today=on_date)
    rules = _rule_map(evaluation["evaluations"])

    return {
        "chart_id": chart_id,
        "date": on_date.isoformat(),
        "dasha": {
            "mahadasha": evaluation["current_dasha"].get("mahadasha", {}).get("planet"),
            "antardasha": evaluation["current_dasha"].get("antardasha", {}).get("planet"),
            "pratyantardasha": evaluation["current_dasha"].get("pratyantardasha", {}).get("planet"),
        },
        "quality_counts": _quality_counts(evaluation["evaluations"]),
        "rule_qualities": {
            "RC-013": rules["RC-013"]["quality"],
            "RC-015": rules["RC-015"]["quality"],
            "RC-018": rules["RC-018"]["quality"],
            "RC-020": rules["RC-020"]["quality"],
        },
        "upapada": {
            "canonical": context["upapada"]["canonical"]["pada_sign_en"],
            "guide_formula": context["upapada"]["project_guides"]["pada_sign_en"],
            "matches": context["upapada"]["matches"],
        },
        "combustion": {
            "Mercury": context["combustion"]["Mercury"]["combust"],
            "Saturn": context["combustion"]["Saturn"]["combust"],
        },
        "aspects": {
            "jupiter_to_h1": 1 in context["aspect_map"]["Jupiter"],
            "mars_to_h7": 7 in context["aspect_map"]["Mars"],
        },
        "transits": {
            "jupiter_from_moon": context["transits"]["references"]["from_moon"]["Jupiter"],
            "saturn_from_moon": context["transits"]["references"]["from_moon"]["Saturn"],
        },
    }


def critical_checks(snapshots: dict[str, dict[str, Any]]) -> list[CheckResult]:
    checks: list[CheckResult] = []

    for chart_id, snapshot in snapshots.items():
        unknown = set(snapshot["quality_counts"].keys()) - ALLOWED_QUALITIES
        checks.append(
            CheckResult(
                name=f"{chart_id}:allowed-quality-labels",
                passed=not unknown,
                details="ok" if not unknown else f"unexpected labels: {sorted(unknown)}",
            )
        )

        checks.append(
            CheckResult(
                name=f"{chart_id}:rc013-not-datagap",
                passed=snapshot["rule_qualities"]["RC-013"] != "data_gap",
                details=f"RC-013={snapshot['rule_qualities']['RC-013']}",
            )
        )

        checks.append(
            CheckResult(
                name=f"{chart_id}:rc020-not-datagap",
                passed=snapshot["rule_qualities"]["RC-020"] != "data_gap",
                details=f"RC-020={snapshot['rule_qualities']['RC-020']}",
            )
        )

    ajay = snapshots["ajay_kumar"]
    sandeep = snapshots["sandeep_0700"]

    checks.extend(
        [
            CheckResult(
                name="ajay:h10-aspect-integrity",
                passed=ajay["aspects"]["jupiter_to_h1"],
                details=f"jupiter_to_h1={ajay['aspects']['jupiter_to_h1']}",
            ),
            CheckResult(
                name="ajay:combustion-mercury-saturn",
                passed=ajay["combustion"]["Mercury"] and ajay["combustion"]["Saturn"],
                details=f"Mercury={ajay['combustion']['Mercury']} Saturn={ajay['combustion']['Saturn']}",
            ),
            CheckResult(
                name="ajay:upapada-conflict-preserved",
                passed=(not ajay["upapada"]["matches"]) and ajay["rule_qualities"]["RC-015"] == "computed_with_conflict",
                details=f"matches={ajay['upapada']['matches']} rc015={ajay['rule_qualities']['RC-015']}",
            ),
            CheckResult(
                name="sandeep:upapada-conflict-preserved",
                passed=(not sandeep["upapada"]["matches"]) and sandeep["rule_qualities"]["RC-015"] == "computed_with_conflict",
                details=f"matches={sandeep['upapada']['matches']} rc015={sandeep['rule_qualities']['RC-015']}",
            ),
            CheckResult(
                name="timing:expected-dasha-chains",
                passed=(
                    ajay["dasha"] == {"mahadasha": "Rahu", "antardasha": "Moon", "pratyantardasha": "Rahu"}
                    and sandeep["dasha"] == {"mahadasha": "Mercury", "antardasha": "Jupiter", "pratyantardasha": "Venus"}
                ),
                details=f"ajay={ajay['dasha']} sandeep={sandeep['dasha']}",
            ),
        ]
    )

    return checks


def _diff(expected: Any, actual: Any, path: str = "") -> list[str]:
    diffs: list[str] = []
    if isinstance(expected, dict) and isinstance(actual, dict):
        all_keys = sorted(set(expected.keys()) | set(actual.keys()))
        for key in all_keys:
            p = f"{path}.{key}" if path else key
            if key not in expected:
                diffs.append(f"+ {p}={actual[key]!r}")
            elif key not in actual:
                diffs.append(f"- {p}={expected[key]!r}")
            else:
                diffs.extend(_diff(expected[key], actual[key], p))
        return diffs
    if isinstance(expected, list) and isinstance(actual, list):
        if expected != actual:
            diffs.append(f"~ {path}: expected={expected!r} actual={actual!r}")
        return diffs
    if expected != actual:
        diffs.append(f"~ {path}: expected={expected!r} actual={actual!r}")
    return diffs


def _load_baseline(path: Path) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def _write_baseline(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def run(mode: str, baseline_path: Path, on_date: date) -> int:
    snapshots = {chart_id: build_snapshot(chart_id, on_date) for chart_id in LOCKED_FIXTURES}

    checks = critical_checks(snapshots)
    failed = [c for c in checks if not c.passed]
    for c in checks:
        status = "PASS" if c.passed else "FAIL"
        print(f"[{status}] {c.name} :: {c.details}")

    if failed:
        print(f"\nCritical checks failed: {len(failed)}")
        return 1

    payload = {
        "meta": {
            "generated_at": datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z"),
            "date_anchor": on_date.isoformat(),
            "fixtures": list(LOCKED_FIXTURES),
            "mode": "baseline",
        },
        "snapshots": snapshots,
    }

    if mode == "accept-baseline":
        _write_baseline(baseline_path, payload)
        print(f"\nBaseline updated: {baseline_path}")
        return 0

    if not baseline_path.exists():
        print(f"\nBaseline file missing: {baseline_path}")
        print("Run with --mode accept-baseline to create it.")
        return 1

    expected = _load_baseline(baseline_path)
    diffs = _diff(expected.get("snapshots", {}), snapshots)
    if diffs:
        print("\nRegression mismatch detected:")
        for line in diffs[:200]:
            print(line)
        if len(diffs) > 200:
            print(f"... truncated ({len(diffs) - 200} more differences)")
        print("\nIf this change is intentional, run: --mode accept-baseline")
        return 1

    print("\nRegression baseline matched.")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Jyotisha robust suite engine")
    parser.add_argument("--mode", choices=["verify", "accept-baseline"], default="verify")
    parser.add_argument("--baseline", default=str(BASELINE_PATH))
    parser.add_argument("--date", default=CRITICAL_DATE.isoformat(), help="Date anchor in YYYY-MM-DD")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    exit_code = run(args.mode, Path(args.baseline), date.fromisoformat(args.date))
    raise SystemExit(exit_code)