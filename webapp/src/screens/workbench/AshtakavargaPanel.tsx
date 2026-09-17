import type { FullContext } from "../../lib/api";

const HOUSES = Array.from({ length: 12 }, (_, i) => i + 1);

function bindusColor(value: number): string {
  if (value >= 5) return "bg-sage/20 text-sage";
  if (value >= 3) return "bg-amber/15 text-amber";
  return "bg-red-muted/10 text-red-muted";
}

/**
 * Ashtakavarga tab -- Sarvashtakavarga (SAV) row + full Bhinnashtakavarga
 * (BAV) grid, straight from app.astro.ashtakavarga (chart-invariant totals
 * cross-checked at import time -- see that module's own self-check).
 */
export function AshtakavargaPanel({ fullContext }: { fullContext: FullContext }) {
  const av = fullContext.ashtakavarga as
    | { sarva: Record<string, number>; bhinna: Record<string, Record<string, number>>; sav_total: number }
    | undefined;

  if (!av) return <p className="text-ink-muted">Ashtakavarga data unavailable.</p>;

  const planets = Object.keys(av.bhinna);

  return (
    <div className="space-y-4">
      <div className="rounded-lg border border-ink/10 bg-surface p-5 shadow-sm">
        <div className="mb-3 flex items-center justify-between">
          <h3 className="text-base font-semibold font-scripture">Sarvashtakavarga (SAV)</h3>
          <span className="text-xs text-ink-muted">Total: {av.sav_total} (chart-invariant, always 337)</span>
        </div>
        <div className="grid grid-cols-6 gap-2 sm:grid-cols-12">
          {HOUSES.map((h) => (
            <div key={h} className={`rounded-md p-2 text-center ${bindusColor(av.sarva[String(h)] ?? 0)}`}>
              <div className="text-[10px] uppercase tracking-wide">H{h}</div>
              <div className="text-lg font-semibold">{av.sarva[String(h)] ?? "-"}</div>
            </div>
          ))}
        </div>
      </div>

      <div className="rounded-lg border border-ink/10 bg-surface p-5 shadow-sm overflow-x-auto">
        <h3 className="mb-3 text-base font-semibold font-scripture">Bhinnashtakavarga (BAV) -- per planet</h3>
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-xs uppercase tracking-wide text-ink-muted">
              <th className="pb-2 pr-3">Planet</th>
              {HOUSES.map((h) => (
                <th key={h} className="pb-2 px-1 text-center">H{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {planets.map((planet) => (
              <tr key={planet} className="border-b border-ink/5 last:border-0">
                <td className="py-1.5 pr-3 font-medium">{planet}</td>
                {HOUSES.map((h) => (
                  <td key={h} className="py-1.5 px-1 text-center">
                    {av.bhinna[planet]?.[String(h)] ?? "-"}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
