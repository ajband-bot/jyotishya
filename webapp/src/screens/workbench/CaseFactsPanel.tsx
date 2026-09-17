import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { api } from "../../lib/api";
import { Database, MessageSquarePlus, Search } from "lucide-react";

/**
 * Case Facts (DB) -- Phase 7's "DB wiring for every case" surfaced as a
 * Chart Workbench tab. Shows the SQL-backed case_* facts for the selected
 * chart (planets/dashas/doshas/yogas/remedies) plus its logged follow-up
 * Q&A -- everything here comes from `GET /api/v2/cases/{chart_id}` and its
 * siblings, backed by app/db/query.py's plain SQL SELECTs, never a
 * re-parse of a reading document.
 *
 * Requires `scripts/sync_db.py` (or the New Horoscope form, which ingests
 * automatically) to have run at least once for this chart_id.
 */
export function CaseFactsPanel({ chartId }: { chartId: string }) {
  const queryClient = useQueryClient();
  const [search, setSearch] = useState("");
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");

  const summaryQuery = useQuery({
    queryKey: ["case-summary", chartId],
    queryFn: () => api.getCaseSummary(chartId),
  });
  const qaQuery = useQuery({
    queryKey: ["case-qa", chartId, search],
    queryFn: () => api.getCaseQA(chartId, search || undefined),
  });

  async function handleLogQA() {
    if (!question.trim() || !answer.trim()) return;
    await api.postCaseQA(chartId, { question, answer });
    setQuestion("");
    setAnswer("");
    queryClient.invalidateQueries({ queryKey: ["case-qa", chartId] });
  }

  if (summaryQuery.isLoading) return <p className="text-ink-muted">Loading case facts from DB...</p>;
  if (summaryQuery.isError || !summaryQuery.data?.chart) {
    return (
      <p className="rounded-md border border-amber/30 bg-amber/5 p-3 text-sm text-amber">
        '{chartId}' has not been ingested into the case DB yet -- run{" "}
        <code>.venv/bin/python scripts/sync_db.py</code> and reload.
      </p>
    );
  }

  const { doshas, yogas, dashas, remedies } = summaryQuery.data;
  const currentDashas = dashas.filter((d) => d.is_current === 1);
  const activeDoshas = doshas.filter((d) => d.present === 1);
  const activeYogas = yogas.filter((y) => y.present === 1);

  return (
    <div className="space-y-5">
      <div className="flex items-center gap-2">
        <Database size={18} className="text-indigo" aria-hidden="true" />
        <h3 className="font-scripture text-xl font-semibold text-indigo">DB-backed case facts -- {chartId}</h3>
      </div>

      <div className="grid gap-3 md:grid-cols-3">
        <div className="rounded-lg border border-ink/10 bg-surface p-4 shadow-sm">
          <p className="mb-2 text-xs font-semibold uppercase text-ink-muted">Current Dasha</p>
          {currentDashas.map((d) => (
            <p key={String(d.level)} className="text-sm">
              {String(d.level)}: <span className="font-medium">{String(d.lord)}</span> ({String(d.start_date)} - {String(d.end_date)})
            </p>
          ))}
        </div>
        <div className="rounded-lg border border-ink/10 bg-surface p-4 shadow-sm">
          <p className="mb-2 text-xs font-semibold uppercase text-ink-muted">Active Doshas ({activeDoshas.length})</p>
          {activeDoshas.map((d) => (
            <p key={String(d.dosha_name)} className="text-sm">
              {String(d.dosha_name)} -- <span className="text-ink-muted">{String(d.severity ?? "n/a")}</span>
            </p>
          ))}
          {activeDoshas.length === 0 && <p className="text-sm text-ink-muted">None flagged present.</p>}
        </div>
        <div className="rounded-lg border border-ink/10 bg-surface p-4 shadow-sm">
          <p className="mb-2 text-xs font-semibold uppercase text-ink-muted">Active Yogas ({activeYogas.length})</p>
          {activeYogas.map((y) => (
            <p key={String(y.yoga_name)} className="text-sm">{String(y.yoga_name)}</p>
          ))}
          {activeYogas.length === 0 && <p className="text-sm text-ink-muted">None flagged present.</p>}
        </div>
      </div>

      <div className="rounded-lg border border-ink/10 bg-surface p-4 shadow-sm">
        <p className="mb-2 text-xs font-semibold uppercase text-ink-muted">Remedies (gemstone gate)</p>
        <div className="grid gap-1 text-sm md:grid-cols-3">
          {remedies.map((r) => (
            <p key={String(r.planet)}>
              {String(r.planet)}:{" "}
              <span className={r.gemstone_appropriate ? "text-sage" : "text-red-muted"}>
                {r.gemstone_appropriate ? "gemstone OK" : "gemstone not indicated"}
              </span>
            </p>
          ))}
        </div>
      </div>

      <div className="rounded-lg border border-ink/10 bg-surface p-4 shadow-sm">
        <div className="mb-2 flex items-center gap-2">
          <MessageSquarePlus size={16} className="text-indigo" aria-hidden="true" />
          <p className="text-xs font-semibold uppercase text-ink-muted">Follow-up Q&amp;A log</p>
        </div>
        <div className="mb-3 flex items-center gap-2">
          <Search size={14} className="text-ink-muted" aria-hidden="true" />
          <input
            className="w-full rounded-md border border-ink/20 bg-bg px-2 py-1 text-sm"
            placeholder="Search prior Q&A for this case..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        <div className="mb-4 space-y-2">
          {qaQuery.data?.qa.map((entry) => (
            <div key={entry.id} className="rounded-md border border-ink/10 p-2 text-sm">
              <p className="font-medium">{entry.question}</p>
              <p className="text-ink-muted">{entry.answer}</p>
              {entry.source_refs && <p className="text-[11px] text-ink-muted/70">source: {entry.source_refs}</p>}
            </div>
          ))}
          {qaQuery.data?.qa.length === 0 && <p className="text-sm text-ink-muted">No Q&A logged yet for this case.</p>}
        </div>
        <div className="space-y-2 border-t border-ink/10 pt-3">
          <input
            className="w-full rounded-md border border-ink/20 bg-bg px-2 py-1 text-sm"
            placeholder="New follow-up question..."
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
          />
          <textarea
            className="w-full rounded-md border border-ink/20 bg-bg px-2 py-1 text-sm"
            placeholder="Answer (once resolved against computed output)..."
            value={answer}
            onChange={(e) => setAnswer(e.target.value)}
          />
          <button
            onClick={handleLogQA}
            className="rounded-md bg-indigo px-3 py-1.5 text-sm font-medium text-white disabled:opacity-40"
            disabled={!question.trim() || !answer.trim()}
          >
            Log to DB
          </button>
        </div>
      </div>
    </div>
  );
}
