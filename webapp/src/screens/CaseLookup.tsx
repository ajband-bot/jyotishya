import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Database, Search, ArrowRight } from "lucide-react";
import { api } from "../lib/api";

/**
 * Case Lookup -- landing screen listing every ingested case. Picking one
 * hands the chart_id back to App.tsx, which selects it and switches to
 * the Chart Workbench's tabbed view (Overview/Vimsottari/Aspects/
 * Ashtakavarga/Doshas & Yogas/Panchanga/Transits/Strength/Domains/Case
 * Facts) -- this screen is purely the entry point, never a dead end.
 */
export function CaseLookup({ onSelect }: { onSelect: (chartId: string) => void }) {
  const [search, setSearch] = useState("");
  const casesQuery = useQuery({ queryKey: ["cases"], queryFn: api.listCases });

  const cases = (casesQuery.data?.cases ?? []).filter((c) => {
    const needle = search.trim().toLowerCase();
    if (!needle) return true;
    return c.name.toLowerCase().includes(needle) || c.id.toLowerCase().includes(needle);
  });

  return (
    <div>
      <div className="mb-4 flex items-center gap-2">
        <Database size={18} className="text-indigo" aria-hidden="true" />
        <h2 className="font-scripture text-xl font-semibold text-indigo">All Cases</h2>
      </div>
      <p className="mb-4 text-sm text-ink-muted">
        Every chart already ingested into the DB-backed case tables (build_plan.md Phase 7). Pick one
        to open its full tabbed Chart Workbench.
      </p>

      <div className="relative mb-4 max-w-sm">
        <Search size={14} className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-ink-muted" />
        <input
          className="w-full rounded-md border border-ink/20 bg-surface py-2 pl-8 pr-3 text-sm focus:border-indigo focus:outline-none"
          placeholder="Search by name or chart id..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      {casesQuery.isLoading && <p className="text-ink-muted">Loading cases...</p>}
      {casesQuery.data && cases.length === 0 && (
        <p className="text-ink-muted">
          No cases match. If you just created a chart under New Horoscope it should already be here --
          otherwise run <code>.venv/bin/python scripts/sync_db.py</code>.
        </p>
      )}

      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {cases.map((c) => (
          <button
            key={c.id}
            onClick={() => onSelect(c.id)}
            className="group flex flex-col items-start gap-1 rounded-lg border border-ink/10 bg-surface p-4 text-left shadow-sm transition-colors hover:border-indigo hover:bg-indigo/5"
          >
            <div className="flex w-full items-center justify-between">
              <span className="font-semibold">{c.name}</span>
              <ArrowRight size={14} className="text-ink-muted transition-transform group-hover:translate-x-0.5 group-hover:text-indigo" />
            </div>
            <span className="font-mono text-xs text-ink-muted">{c.id}</span>
            <span className="text-xs text-ink-muted">
              {c.dob} {c.tob} (UTC{c.utc_offset >= 0 ? "+" : ""}{c.utc_offset})
            </span>
          </button>
        ))}
      </div>
    </div>
  );
}
