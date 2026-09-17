import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Database, ChevronLeft, ChevronRight } from "lucide-react";
import { api } from "../lib/api";

const PAGE_SIZE = 25;

/**
 * DB Browser -- Phase 8 "check the SQL DB data" ask. Read-only, generic
 * over every table app.db.models defines (never a raw SQL box -- table
 * names are only ever chosen from this list, matching the API's own
 * allowlist-by-metadata safety design).
 */
export function DbBrowser() {
  const [selectedTable, setSelectedTable] = useState<string | null>(null);
  const [page, setPage] = useState(0);

  const tablesQuery = useQuery({ queryKey: ["db-tables"], queryFn: api.listDbTables });
  const rowsQuery = useQuery({
    queryKey: ["db-rows", selectedTable, page],
    queryFn: () => api.getDbTableRows(selectedTable!, PAGE_SIZE, page * PAGE_SIZE),
    enabled: !!selectedTable,
  });

  const totalPages = rowsQuery.data ? Math.max(1, Math.ceil(rowsQuery.data.total_rows / PAGE_SIZE)) : 1;

  return (
    <div className="grid gap-4 md:grid-cols-[260px_1fr]">
      <div>
        <div className="mb-2 flex items-center justify-between text-sm font-semibold text-ink-muted">
          <span className="flex items-center gap-2"><Database size={16} /> Tables</span>
        </div>
        {tablesQuery.data && (
          <p className="mb-2 text-xs text-ink-muted break-all">{tablesQuery.data.database_url}</p>
        )}
        <div className="space-y-1.5">
          {tablesQuery.data?.tables.map((t) => (
            <button
              key={t.name}
              onClick={() => {
                setSelectedTable(t.name);
                setPage(0);
              }}
              className={`w-full rounded-md border px-3 py-2 text-left text-sm transition-colors ${
                selectedTable === t.name ? "border-indigo bg-indigo/5 font-semibold" : "border-ink/10 bg-surface hover:bg-bg"
              }`}
            >
              <div className="flex items-center justify-between">
                <span>{t.name}</span>
                <span className="text-xs text-ink-muted">{t.row_count} rows</span>
              </div>
            </button>
          ))}
        </div>
      </div>

      <div>
        {!selectedTable && <p className="text-ink-muted">Pick a table on the left to see its live rows.</p>}
        {selectedTable && rowsQuery.data && (
          <div className="rounded-lg border border-ink/10 bg-surface p-4 shadow-sm">
            <div className="mb-3 flex items-center justify-between">
              <h3 className="text-base font-semibold font-scripture">{rowsQuery.data.table}</h3>
              <div className="flex items-center gap-2 text-xs text-ink-muted">
                <button
                  onClick={() => setPage((p) => Math.max(0, p - 1))}
                  disabled={page === 0}
                  className="rounded border border-ink/15 p-1 disabled:opacity-30"
                >
                  <ChevronLeft size={14} />
                </button>
                Page {page + 1} / {totalPages} ({rowsQuery.data.total_rows} rows)
                <button
                  onClick={() => setPage((p) => (p + 1 < totalPages ? p + 1 : p))}
                  disabled={page + 1 >= totalPages}
                  className="rounded border border-ink/15 p-1 disabled:opacity-30"
                >
                  <ChevronRight size={14} />
                </button>
              </div>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-xs">
                <thead>
                  <tr className="text-left uppercase tracking-wide text-ink-muted">
                    {rowsQuery.data.columns.map((c) => (
                      <th key={c} className="pb-2 pr-3 whitespace-nowrap">{c}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {rowsQuery.data.rows.map((row, i) => (
                    <tr key={i} className="border-b border-ink/5 last:border-0">
                      {rowsQuery.data!.columns.map((c) => (
                        <td key={c} className="py-1.5 pr-3 max-w-xs truncate" title={String(row[c] ?? "")}>
                          {String(row[c] ?? "")}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
              {rowsQuery.data.rows.length === 0 && <p className="py-4 text-center text-ink-muted">No rows.</p>}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
