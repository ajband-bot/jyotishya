import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Heart, Users, AlertTriangle, CheckCircle2, Clock, Gauge } from "lucide-react";
import {
  api,
  type ChartSummary,
  type MarriageTimingWindow,
  type MarriedLifeStatusItem,
  type MarriageCompatibilityPerson,
} from "../lib/api";
import { EvidenceCard } from "../components/JsonTree";

const INTERPRETATION_TONE: Record<string, string> = {
  perfect: "text-sage",
  excellent: "text-sage",
  good: "text-sage",
  average: "text-amber",
  challenging: "text-red-muted",
  requires_strong_overriding_factors: "text-red-muted",
};

const VERDICT_TONE: Record<string, string> = {
  certain: "border-sage/40 bg-sage/5 text-sage",
  confirmed: "border-amber/40 bg-amber/5 text-amber",
  possible: "border-ink/15 bg-bg text-ink-muted",
};

function ChartPicker({
  label,
  charts,
  value,
  onChange,
}: {
  label: string;
  charts: ChartSummary[];
  value: string;
  onChange: (id: string) => void;
}) {
  return (
    <div>
      <label className="mb-1 block text-xs font-semibold uppercase tracking-wide text-ink-muted">{label}</label>
      <select
        className="w-full rounded-md border border-ink/20 bg-surface px-3 py-2 text-sm focus:border-indigo focus:outline-none"
        value={value}
        onChange={(e) => onChange(e.target.value)}
      >
        <option value="">Select a chart...</option>
        {charts.map((c) => (
          <option key={c.id} value={c.id}>
            {c.name} ({c.id})
          </option>
        ))}
      </select>
    </div>
  );
}

function KutaTable({ kutas, effectiveTotal, maxTotal, interpretation, mangalVerdict }: {
  kutas: Record<string, { raw_score: number; effective_score: number; max_score: number }>;
  effectiveTotal: number;
  maxTotal: number;
  interpretation: string;
  mangalVerdict: string;
}) {
  return (
    <div className="rounded-lg border border-ink/10 bg-surface p-5 shadow-sm">
      <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
        <h3 className="text-base font-semibold font-scripture">Ashtakuta (Guna Milan) -- pure compatibility metric</h3>
        <span className={`rounded-full border px-3 py-1 text-xs font-semibold uppercase tracking-wide ${INTERPRETATION_TONE[interpretation] ?? "text-ink"}`}>
          {effectiveTotal}/{maxTotal} -- {interpretation.replace(/_/g, " ")}
        </span>
      </div>
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-ink/10 text-left text-xs uppercase tracking-wide text-ink-muted">
            <th className="py-1">Kuta</th>
            <th className="py-1 text-right">Effective</th>
            <th className="py-1 text-right">Max</th>
          </tr>
        </thead>
        <tbody>
          {Object.entries(kutas).map(([name, k]) => (
            <tr key={name} className="border-b border-ink/5 last:border-0">
              <td className="py-1.5 capitalize">{name.replace(/_/g, " ")}</td>
              <td className="py-1.5 text-right font-medium">{k.effective_score}</td>
              <td className="py-1.5 text-right text-ink-muted">{k.max_score}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <p className="mt-3 text-xs text-ink-muted">
        Mangal Dosha match: <b className="text-ink">{mangalVerdict.replace(/_/g, " ")}</b>
      </p>
    </div>
  );
}

function StrengthCautionColumn({ title, items, tone }: { title: string; items: MarriedLifeStatusItem[]; tone: "strength" | "caution" }) {
  const Icon = tone === "strength" ? CheckCircle2 : AlertTriangle;
  const colorClass = tone === "strength" ? "text-sage border-sage/30 bg-sage/5" : "text-amber border-amber/30 bg-amber/5";
  return (
    <div>
      <h4 className="mb-2 text-xs font-semibold uppercase tracking-wide text-ink-muted">{title}</h4>
      {items.length === 0 ? (
        <p className="text-xs italic text-ink-muted">None flagged.</p>
      ) : (
        <div className="space-y-2">
          {items.map((item, i) => (
            <div key={i} className={`rounded-md border p-2.5 text-xs ${colorClass}`}>
              <div className="mb-0.5 flex items-center gap-1.5 font-semibold">
                <Icon size={13} /> {item.area}
              </div>
              <p className="text-ink">{item.note}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function TimingWindowsTable({ windows, caveat }: { windows: MarriageTimingWindow[]; caveat: string }) {
  if (windows.length === 0) {
    return <p className="text-xs italic text-ink-muted">No upcoming Dasha/Transit/D9 agreement windows found in the scanned range.</p>;
  }
  return (
    <div>
      <div className="space-y-2">
        {windows.map((w, i) => (
          <div key={i} className={`rounded-md border p-3 text-xs ${VERDICT_TONE[w.verdict]}`}>
            <div className="mb-1 flex flex-wrap items-center justify-between gap-2">
              <span className="flex items-center gap-1.5 font-semibold">
                <Clock size={13} /> {w.start} &rarr; {w.end}
              </span>
              <span className="flex items-center gap-1 rounded-full border border-current px-2 py-0.5 font-semibold">
                <Gauge size={12} /> {w.probability_percent}% ({w.verdict})
              </span>
            </div>
            <p className="text-ink">{w.reason}</p>
          </div>
        ))}
      </div>
      <p className="mt-3 text-[11px] italic text-ink-muted">{caveat}</p>
    </div>
  );
}

function PersonPanel({ person, alreadyMarried }: { person: MarriageCompatibilityPerson; alreadyMarried: boolean }) {
  return (
    <div className="rounded-lg border border-ink/10 bg-surface p-5 shadow-sm">
      <h3 className="mb-3 flex items-center gap-2 text-base font-semibold font-scripture">
        <Users size={16} className="text-indigo" /> {person.name}
        <span className="font-mono text-xs font-normal text-ink-muted">({person.chart_id})</span>
      </h3>

      {alreadyMarried && person.married_life_status && (
        <div className="space-y-4">
          <StrengthCautionColumn title="Strengths" items={person.married_life_status.strengths} tone="strength" />
          <StrengthCautionColumn title="Cautions" items={person.married_life_status.cautions} tone="caution" />
          <p className="text-xs text-ink-muted">
            Current dasha: <b className="text-ink">{person.married_life_status.current_dasha.mahadasha ?? "-"}</b>
            {" / "}
            <b className="text-ink">{person.married_life_status.current_dasha.antardasha ?? "-"}</b>
            {Boolean(person.married_life_status.sade_sati?.active) && (
              <span className="ml-2 text-amber">-- Sade Sati active ({String(person.married_life_status.sade_sati?.label)})</span>
            )}
          </p>
        </div>
      )}

      {!alreadyMarried && person.marriage_timing && (
        <TimingWindowsTable
          windows={person.marriage_timing.upcoming_windows}
          caveat={person.marriage_timing.probability_caveat}
        />
      )}
    </div>
  );
}

/**
 * Marriage Compatibility screen (build_plan.md Phase 8 follow-up -- the one
 * item Phase 8's own note left explicitly undone). Picks two charts
 * independently of the app-wide chart selector (same pattern as Case
 * Lookup), toggles an "Already Married?" checkbox that is a pure
 * presentation switch (no new astrology, see app/api/v2/marriage_compatibility.py):
 * unmarried -> per-person upcoming marriage-timing windows with a heuristic
 * probability_percent + reason; already married -> per-person strengths/
 * cautions for the existing marriage. Ashtakuta/Synastry/D9-cross-
 * compatibility are always shown -- pure inter-chart compatibility metrics.
 */
export function MarriageCompatibility() {
  const [groomId, setGroomId] = useState("");
  const [brideId, setBrideId] = useState("");
  const [alreadyMarried, setAlreadyMarried] = useState(false);
  const [submitted, setSubmitted] = useState(false);

  const chartsQuery = useQuery({ queryKey: ["charts"], queryFn: api.listCharts });
  const sameChart = !!groomId && !!brideId && groomId === brideId;
  const canSubmit = !!groomId && !!brideId && !sameChart;

  const compatQuery = useQuery({
    queryKey: ["marriage-compatibility", groomId, brideId, alreadyMarried],
    queryFn: () => api.getMarriageCompatibility(groomId, brideId, alreadyMarried),
    enabled: submitted && canSubmit,
  });

  return (
    <div className="space-y-5">
      <div className="rounded-lg border border-ink/10 bg-surface p-5 shadow-sm">
        <h2 className="mb-1 flex items-center gap-2 text-xl font-semibold font-scripture text-indigo">
          <Heart size={18} /> Marriage Compatibility
        </h2>
        <p className="mb-4 text-sm text-ink-muted">
          Pick two charts. Ashtakuta, Mangal Dosha matching, synastry, and D9 cross-compatibility are always
          computed. Check "Already married" for strengths/cautions on the existing marriage instead of a
          when-might-this-happen timing forecast.
        </p>

        <div className="grid gap-4 sm:grid-cols-2">
          <ChartPicker label="Groom / Partner A (Venus karaka)" charts={chartsQuery.data?.charts ?? []} value={groomId} onChange={setGroomId} />
          <ChartPicker label="Bride / Partner B (Jupiter karaka)" charts={chartsQuery.data?.charts ?? []} value={brideId} onChange={setBrideId} />
        </div>

        {sameChart && <p className="mt-2 text-xs text-red-muted">Pick two different charts.</p>}

        <label className="mt-4 flex items-center gap-2 text-sm">
          <input type="checkbox" checked={alreadyMarried} onChange={(e) => setAlreadyMarried(e.target.checked)} className="h-4 w-4 rounded border-ink/30" />
          Already married (show strengths/cautions instead of timing predictions)
        </label>

        <button
          onClick={() => setSubmitted(true)}
          disabled={!canSubmit}
          className="mt-4 rounded-md bg-indigo px-4 py-2 text-sm font-semibold text-white shadow-sm disabled:cursor-not-allowed disabled:opacity-40"
        >
          Run Compatibility Analysis
        </button>
      </div>

      {compatQuery.isLoading && <p className="text-ink-muted">Computing compatibility...</p>}
      {compatQuery.isError && <p className="text-red-muted">Failed to load: {(compatQuery.error as Error).message}</p>}

      {compatQuery.data && (
        <div className="space-y-5">
          <KutaTable
            kutas={compatQuery.data.ashtakuta.kutas}
            effectiveTotal={compatQuery.data.ashtakuta.effective_total}
            maxTotal={compatQuery.data.ashtakuta.max_total}
            interpretation={compatQuery.data.ashtakuta.interpretation}
            mangalVerdict={compatQuery.data.ashtakuta.mangal_dosha.verdict}
          />

          <div className="grid gap-4 sm:grid-cols-2">
            <EvidenceCard title="Synastry (7 indicators)" subtitle="Marriage_Guide_Part4.md Step 15" data={compatQuery.data.synastry} />
            <EvidenceCard title="D9 Cross-Compatibility" subtitle="Marriage_Guide_Part4.md 16.1" data={compatQuery.data.d9_cross_compatibility} />
          </div>

          <div className="grid gap-4 lg:grid-cols-2">
            <PersonPanel person={compatQuery.data.groom} alreadyMarried={alreadyMarried} />
            <PersonPanel person={compatQuery.data.bride} alreadyMarried={alreadyMarried} />
          </div>
        </div>
      )}
    </div>
  );
}
