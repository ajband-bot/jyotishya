import { useQuery } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import { api } from "../../lib/api";
import { MermaidDiagram } from "../../components/MermaidDiagram";

function buildCycleDiagram(sequence: Array<{ planet: string; years: number }>, selected: string | null): string {
  const lines = ["graph LR"];
  sequence.forEach((s, i) => {
    const next = sequence[(i + 1) % sequence.length];
    lines.push(`  ${s.planet}["${s.planet}\\n${s.years}y"] --> ${next.planet}`);
  });
  if (selected) {
    lines.push(`  style ${selected} fill:#6366f1,color:#fff,stroke:#4338ca,stroke-width:2px`);
  }
  return lines.join("\n");
}

/**
 * Vimsottari Dasha Reference -- the fixed 9-planet cycle (order + years) as
 * a graphical cycle diagram, plus a click-to-drill Antardasha duration
 * table for whichever Mahadasha planet is selected. Chart-independent --
 * durations only, no fabricated calendar dates.
 */
export function DashaReferencePanel() {
  const { data } = useQuery({ queryKey: ["ref-dasha"], queryFn: api.getDashaReference });
  const [selected, setSelected] = useState<string | null>(null);
  const [selectedAd, setSelectedAd] = useState<string | null>(null);

  const diagram = useMemo(() => {
    if (!data) return "";
    return buildCycleDiagram(data.sequence, selected);
  }, [data, selected]);

  if (!data) return <p className="text-ink-muted">Loading...</p>;

  const activePlanet = selected ?? data.sequence[0].planet;
  const adRows = data.antardasha_tables[activePlanet];
  const activeAd = selectedAd ?? adRows[0].planet;
  const pdRows = data.pratyantardasha_tables[activePlanet][activeAd];

  return (
    <div>
      <p className="text-sm text-ink-muted mb-3">
        Total cycle: {data.total_years} years -- click a planet below to see its Antardasha (AD) breakdown.
        {" "}Formula: {data.pratyantardasha_formula}
      </p>
      <div className="mb-4 rounded-lg border border-ink/10 bg-surface p-4 shadow-sm">
        <MermaidDiagram definition={diagram} />
      </div>
      <div className="mb-4 flex flex-wrap gap-2">
        {data.sequence.map((s) => (
          <button
            key={s.planet}
            onClick={() => {
              setSelected(s.planet);
              setSelectedAd(null);
            }}
            className={`rounded-md px-3 py-1.5 text-sm font-medium ${
              activePlanet === s.planet ? "bg-indigo text-white" : "bg-surface border border-ink/20"
            }`}
          >
            {s.planet} ({s.years}y)
          </button>
        ))}
      </div>
      <div className="overflow-x-auto rounded-lg border border-ink/10 bg-surface shadow-sm mb-4">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-ink/10 text-xs text-ink-muted">
              <th className="p-2 text-left">Antardasha (AD) lord within {activePlanet} Mahadasha -- click a row for its Pratyantardasha (PD)</th>
              <th className="p-2 text-left">Years</th>
              <th className="p-2 text-left">Months</th>
            </tr>
          </thead>
          <tbody>
            {adRows.map((row) => (
              <tr
                key={row.planet}
                onClick={() => setSelectedAd(row.planet)}
                className={`cursor-pointer border-b border-ink/5 last:border-0 ${
                  activeAd === row.planet ? "bg-indigo/10" : "hover:bg-ink/5"
                }`}
              >
                <td className="p-2 font-medium">{row.planet}</td>
                <td className="p-2">{row.years}</td>
                <td className="p-2">{row.months}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="overflow-x-auto rounded-lg border border-indigo/20 bg-indigo/5 shadow-sm">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-indigo/20 text-xs text-ink-muted">
              <th className="p-2 text-left">Pratyantardasha (PD) lord within {activePlanet}/{activeAd} AD</th>
              <th className="p-2 text-left">Years</th>
              <th className="p-2 text-left">Days</th>
            </tr>
          </thead>
          <tbody>
            {pdRows.map((row) => (
              <tr key={row.planet} className="border-b border-indigo/10 last:border-0">
                <td className="p-2 font-medium">{row.planet}</td>
                <td className="p-2">{row.years}</td>
                <td className="p-2">{row.days}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="mt-2 text-[11px] text-ink-muted">
        {data.note} Pratyantardasha (PD) tables follow the same proportional rule one level deeper -- see a
        specific chart's Chart Dashboard for real dated PD timelines.
      </p>
    </div>
  );
}
