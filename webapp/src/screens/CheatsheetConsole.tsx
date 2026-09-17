import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { AlertTriangle, CheckCircle2, HelpCircle, XCircle } from "lucide-react";
import { api, type CheatsheetResult } from "../lib/api";

const VERDICTS = ["match", "mismatch", "unverifiable", "data_gap"] as const;

function verdictColor(verdict: string): string {
  if (verdict === "match") return "text-sage border-sage/30 bg-sage/5";
  if (verdict === "mismatch") return "text-red-muted border-red-muted/30 bg-red-muted/5";
  if (verdict === "data_gap") return "text-amber border-amber/30 bg-amber/5";
  return "text-ink-muted border-ink/20 bg-ink/5";
}

function verdictLabel(verdict: string): string {
  if (verdict === "match") return "Match";
  if (verdict === "mismatch") return "Mismatch";
  if (verdict === "data_gap") return "Data Gap";
  return "Unverifiable";
}

function VerdictIcon({ verdict }: { verdict: string }) {
  if (verdict === "match") return <CheckCircle2 size={16} />;
  if (verdict === "mismatch") return <XCircle size={16} />;
  if (verdict === "data_gap") return <AlertTriangle size={16} />;
  return <HelpCircle size={16} />;
}

function ClaimRow({ result }: { result: CheatsheetResult }) {
  const claim = result.claim;
  return (
    <div className={`rounded-lg border p-4 shadow-sm ${verdictColor(result.verdict)}`}>
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2 text-sm font-semibold">
          <VerdictIcon verdict={result.verdict} />
          {verdictLabel(result.verdict)}
        </div>
        <span className="text-xs text-ink-muted">
          {claim.source_file} -- {claim.section}
        </span>
      </div>
      <p className="text-sm text-ink mb-2 italic">&ldquo;{claim.claim_text}&rdquo;</p>
      {claim.applies_to_chart && (
        <p className="text-xs text-ink-muted mb-1">Chart: {claim.applies_to_chart}</p>
      )}
      {result.computed_value !== null && (
        <p className="text-xs text-ink-muted mb-1">
          Computed: <code className="text-ink">{JSON.stringify(result.computed_value)}</code>
        </p>
      )}
      <p className="text-xs">{result.diff_detail}</p>
    </div>
  );
}

/**
 * Cheat-Sheet Cross-Validation Console (docs/technical-architecture.md 4.4)
 * -- Ajay's explicit ask: run every cheat sheet against computed output
 * side by side. Never silently reconciles a mismatch -- it stays flagged
 * until a human re-audits the source document.
 */
export function CheatsheetConsole() {
  const [filter, setFilter] = useState<string | undefined>(undefined);
  const { data, isLoading } = useQuery({
    queryKey: ["cheatsheet-claims", filter],
    queryFn: () => api.getCheatsheetClaims(filter),
  });

  if (isLoading) return <p className="text-ink-muted">Extracting + validating corpus claims...</p>;
  if (!data) return null;

  return (
    <div>
      <p className="text-sm text-ink-muted mb-4">
        {data.total_claims} claims extracted from the rule-card corpus and doctrine registry,
        validated live against computed truth. Mismatches stay flagged, never silently fixed.
      </p>

      <div className="mb-4 flex flex-wrap gap-2">
        <button
          onClick={() => setFilter(undefined)}
          className={`rounded-md px-3 py-1.5 text-sm font-medium ${!filter ? "bg-indigo text-white" : "bg-surface border border-ink/20"}`}
        >
          All ({data.total_claims})
        </button>
        {VERDICTS.map((v) => (
          <button
            key={v}
            onClick={() => setFilter(v)}
            className={`rounded-md px-3 py-1.5 text-sm font-medium border ${filter === v ? "bg-indigo text-white border-indigo" : verdictColor(v)}`}
          >
            {verdictLabel(v)} ({data.verdict_counts[v] ?? 0})
          </button>
        ))}
      </div>

      <div className="grid gap-3">
        {data.results.map((r) => (
          <ClaimRow key={r.claim.claim_id} result={r} />
        ))}
      </div>
    </div>
  );
}
