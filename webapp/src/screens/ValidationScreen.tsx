import { CheckCircle2, AlertTriangle, Gauge } from "lucide-react";
import type { ValidationScreenData, CoverageData, DoshasData } from "../lib/api";

function MetricCard({ label, value, tone }: { label: string; value: string; tone?: "sage" | "amber" | "red" }) {
  const toneClass = tone === "sage" ? "text-sage" : tone === "red" ? "text-red-muted" : tone === "amber" ? "text-amber" : "text-indigo";
  return (
    <div className="rounded-lg border border-ink/10 bg-surface p-4 text-center shadow-sm">
      <div className={`text-2xl font-semibold ${toneClass}`}>{value}</div>
      <div className="mt-1 text-xs uppercase tracking-wide text-ink-muted">{label}</div>
    </div>
  );
}

function toneForPct(pct: number): "sage" | "amber" | "red" {
  if (pct >= 90) return "sage";
  if (pct >= 60) return "amber";
  return "red";
}

/**
 * Validate tab -- Chart Integrity Screen (spec 15) PLUS Phase 8's "validate
 * what is generated" ask: the Rule Coverage %% / Evidence Traceability %% /
 * Unsupported Claim Count metrics build_plan.md names explicitly
 * (app.rules.priority.coverage_report), and a doshas-present summary --
 * shown before any narrative interpretation is trusted.
 */
export function ValidationScreen({
  data,
  coverage,
  doshas,
}: {
  data: ValidationScreenData;
  coverage?: CoverageData;
  doshas?: DoshasData;
}) {
  const rows: Array<[string, string]> = [
    ["Birth data", data.checks.birth_data ? "Confirmed" : "Missing"],
    ["Ayanamsha", String(data.checks.ayanamsha)],
    ["House system", String(data.checks.house_system)],
    ["Node type", String(data.checks.node_type)],
    ["D1 chart", data.checks.d1 ? "Computed" : "Missing"],
    ["D9 chart", data.checks.d9 ? "Computed" : "Missing"],
    ["Vimshottari Dasha", data.checks.vimshottari ? "Computed" : "Missing"],
    ["Current Mahadasha", String(data.checks.current_mahadasha ?? "-")],
  ];

  const activeDoshas = doshas
    ? Object.entries(doshas.doshas).filter(([, d]) => (d as Record<string, unknown>).present === true)
    : [];

  return (
    <div className="space-y-4">
      {coverage && (
        <div>
          <div className="mb-2 flex items-center gap-2 text-sm font-semibold text-ink-muted">
            <Gauge size={16} /> Internal validation metrics (rule coverage)
          </div>
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
            <MetricCard label="Rule Coverage" value={`${coverage.rule_coverage_pct}%`} tone={toneForPct(coverage.rule_coverage_pct)} />
            <MetricCard
              label="Evidence Traceability"
              value={`${coverage.evidence_traceability_pct}%`}
              tone={toneForPct(coverage.evidence_traceability_pct)}
            />
            <MetricCard
              label="Unsupported Claims"
              value={String(coverage.unsupported_claim_count)}
              tone={coverage.unsupported_claim_count === 0 ? "sage" : "amber"}
            />
            <MetricCard label="Rules Evaluated" value={`${coverage.total_matched}/${coverage.total_rules_evaluated}`} />
          </div>
        </div>
      )}

      <div className="rounded-lg border border-ink/10 bg-surface p-6 shadow-sm">
        <h2 className="mb-4 text-xl font-semibold text-ink font-scripture">Chart Integrity</h2>
        <table className="w-full text-sm">
          <tbody>
            {rows.map(([label, value]) => (
              <tr key={label} className="border-b border-ink/5 last:border-0">
                <td className="py-2 pr-4 text-ink-muted">{label}</td>
                <td className="py-2 flex items-center gap-2 font-medium">
                  <CheckCircle2 size={16} className="text-sage shrink-0" />
                  {value}
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        {data.warnings.length > 0 && (
          <div className="mt-5 space-y-2">
            {data.warnings.map((w) => (
              <div
                key={w}
                className="flex items-start gap-2 rounded-md border border-amber/30 bg-amber/5 p-3 text-sm text-amber"
              >
                <AlertTriangle size={16} className="mt-0.5 shrink-0" />
                <span>{w}</span>
              </div>
            ))}
          </div>
        )}
      </div>

      {doshas && (
        <div className="rounded-lg border border-ink/10 bg-surface p-6 shadow-sm">
          <h3 className="mb-3 text-base font-semibold font-scripture">Doshas currently present</h3>
          {activeDoshas.length === 0 ? (
            <p className="text-sm text-sage">None of the 8 mandatory checks flagged an uncancelled dosha.</p>
          ) : (
            <ul className="space-y-1 text-sm">
              {activeDoshas.map(([name]) => (
                <li key={name} className="flex items-center gap-2 text-red-muted">
                  <AlertTriangle size={14} /> {name.replace(/_/g, " ")}
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
}
