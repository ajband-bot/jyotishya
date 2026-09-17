"""Phase 7 DB sync CLI -- run this whenever chart fixtures, rule packs, or
the cheatsheet concept registry change.

Usage:
    .venv/bin/python scripts/sync_db.py

Does three things, in order:
  1. Ingests every data/charts/*.yaml fixture into the case_* tables
     (app.db.ingest) -- so every case we're running has DB-backed facts.
  2. Resyncs rule_versions from the compiled rule packs.
  3. Resyncs cheatsheet_claims (fresh extractor+differ pass) and
     cheatsheet_concepts (the learning registry) tables.

Idempotent -- safe to run repeatedly; every table here is a full
delete-then-insert per its own scope (per chart_id for case_*, full wipe
for the three engine-state tables), never an accumulating append.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.db.ingest import ingest_all_fixtures
from app.db.sync import sync_all


def main() -> None:
    print("Ingesting case facts for every fixture...")
    case_counts = ingest_all_fixtures()
    for chart_id, counts in case_counts.items():
        print(f"  {chart_id}: {counts}")

    print("\nSyncing engine-state tables (rule_versions, cheatsheet_claims, cheatsheet_concepts)...")
    engine_counts = sync_all()
    for table, count in engine_counts.items():
        print(f"  {table}: {count} rows")

    print("\nDone. Query via app.db.query or the /api/v2/cheatsheet/* and /api/v2/cases/* endpoints.")


if __name__ == "__main__":
    main()
