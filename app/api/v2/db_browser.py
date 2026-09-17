"""SQL DB Browser API (build_plan.md Phase 8 -- "check the SQL DB data"
workbench ask).

Generic, read-only, and safe: table names are only ever resolved through
`app.db.models.metadata.tables` (the SAME SQLAlchemy Core metadata the
rest of the app uses to create/query these tables) -- never through a raw,
user-supplied SQL string. There is no way to reach a table this app didn't
itself define, and no way to inject SQL through a table or column name.
"""
from __future__ import annotations

from datetime import date, datetime
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlalchemy import func, select

from app.db.models import get_engine, metadata

router = APIRouter(prefix="/api/v2/db", tags=["db-browser"])


def _json_safe(value: Any) -> Any:
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, (bytes, bytearray)):
        return value.decode("utf-8", errors="replace")
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return str(value)


def list_tables_data() -> dict[str, Any]:
    engine = get_engine()
    tables = []
    with engine.connect() as conn:
        for name, table in sorted(metadata.tables.items()):
            row_count = conn.execute(select(func.count()).select_from(table)).scalar_one()
            tables.append({
                "name": name,
                "columns": [c.name for c in table.columns],
                "row_count": row_count,
            })
    return {"tables": tables, "count": len(tables), "database_url": str(engine.url)}


def get_table_rows_data(table_name: str, limit: int = 50, offset: int = 0) -> dict[str, Any]:
    if table_name not in metadata.tables:
        raise KeyError(table_name)
    if not 1 <= limit <= 500:
        raise ValueError("limit must be between 1 and 500")
    if offset < 0:
        raise ValueError("offset must be >= 0")
    table = metadata.tables[table_name]
    engine = get_engine()
    with engine.connect() as conn:
        total = conn.execute(select(func.count()).select_from(table)).scalar_one()
        rows = conn.execute(select(table).limit(limit).offset(offset)).mappings().all()
    return {
        "table": table_name,
        "columns": [c.name for c in table.columns],
        "total_rows": total,
        "limit": limit,
        "offset": offset,
        "rows": [{k: _json_safe(v) for k, v in dict(row).items()} for row in rows],
    }


@router.get("/tables")
async def api_list_tables() -> dict[str, Any]:
    """Every table this app has ever defined (app.db.models.metadata),
    with column names and live row counts."""
    return list_tables_data()


@router.get("/tables/{table_name}/rows")
async def api_get_table_rows(table_name: str, limit: int = 50, offset: int = 0) -> dict[str, Any]:
    """Paginated raw rows for one table -- the literal 'let me check the
    SQL DB data' escape hatch, without opening a separate DB client."""
    try:
        return get_table_rows_data(table_name, limit=limit, offset=offset)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Unknown table: {table_name}")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
