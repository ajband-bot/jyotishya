import { useState } from "react";
import type { ChartDetail } from "../../lib/api";

/**
 * Vimsottari Dasha tab -- full Mahadasha timeline plus a drill-in
 * Antardasha table for whichever MD row the user selects (defaults to
 * the currently-running one). All data already comes back on the plain
 * GET /charts/{id} response -- no extra fetch needed for this tab.
 */
export function VimsottariPanel({ chart }: { chart: ChartDetail }) {
  const currentMd = chart.current_dasha.mahadasha?.planet;
  const [selected, setSelected] = useState<string | null>(currentMd ?? null);

  const antars = (chart.current_dasha.all_antars ?? []).filter(
    () => selected === currentMd,
  );

  return (
    <div className="grid gap-4 md:grid-cols-2">
      <div className="rounded-lg border border-ink/10 bg-surface p-5 shadow-sm">
        <h3 className="mb-3 text-base font-semibold font-scripture">Vimsottari Mahadasha Timeline</h3>
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-xs uppercase tracking-wide text-ink-muted">
              <th className="pb-2">Lord</th>
              <th className="pb-2">Years</th>
              <th className="pb-2">Start</th>
              <th className="pb-2">End</th>
            </tr>
          </thead>
          <tbody>
            {chart.dashas.map((d) => (
              <tr
                key={d.start}
                onClick={() => setSelected(d.planet)}
                className={`cursor-pointer border-b border-ink/5 last:border-0 hover:bg-bg ${
                  d.planet === currentMd ? "bg-gold/5" : ""
                } ${selected === d.planet ? "font-semibold" : ""}`}
              >
                <td className="py-1.5">{d.planet}{d.planet === currentMd && <span className="ml-2 text-[10px] text-gold uppercase">current</span>}</td>
                <td className="py-1.5">{d.years}</td>
                <td className="py-1.5">{d.start}</td>
                <td className="py-1.5">{d.end}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="rounded-lg border border-ink/10 bg-surface p-5 shadow-sm">
        <h3 className="mb-1 text-base font-semibold font-scripture">
          Antardasha -- {selected ?? "select a Mahadasha"}
        </h3>
        <p className="mb-3 text-xs text-ink-muted">
          {selected === currentMd
            ? "Antardasha breakdown for the currently-running Mahadasha."
            : "Antardasha breakdown is only pre-computed for the current Mahadasha in this response."}
        </p>
        {antars.length > 0 ? (
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-xs uppercase tracking-wide text-ink-muted">
                <th className="pb-2">Lord</th>
                <th className="pb-2">Start</th>
                <th className="pb-2">End</th>
              </tr>
            </thead>
            <tbody>
              {antars.map((a) => (
                <tr
                  key={a.start}
                  className={`border-b border-ink/5 last:border-0 ${
                    a.planet === chart.current_dasha.antardasha?.planet ? "bg-gold/5 font-semibold" : ""
                  }`}
                >
                  <td className="py-1.5">{a.planet}</td>
                  <td className="py-1.5">{a.start}</td>
                  <td className="py-1.5">{a.end}</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p className="text-sm text-ink-muted">No Antardasha rows available for this Mahadasha.</p>
        )}

        {chart.current_dasha.pratyantardasha && selected === currentMd && (
          <div className="mt-4 rounded-md border border-indigo/20 bg-indigo/5 p-3 text-sm">
            <span className="font-medium text-indigo">Current Pratyantardasha: </span>
            {chart.current_dasha.pratyantardasha.planet} ({chart.current_dasha.pratyantardasha.start} -&gt;{" "}
            {chart.current_dasha.pratyantardasha.end})
          </div>
        )}
      </div>
    </div>
  );
}
