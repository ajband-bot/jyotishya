import { AlertTriangle, CheckCircle2 } from "lucide-react";
import type { FullContext } from "../../lib/api";

const PLANET_ORDER = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"];

interface TransitPlanetEntry {
  transit_sign_en: string;
  simple_gochara: { house_from_moon: number; favorable: boolean };
  ashtakavarga_gochara: { transit_house: number; sav_bindus: number; pav_bindus: number; verdict: string } | { data_gap: string };
  methods_agree: boolean;
  combined_verdict: string;
}

const VERDICT_TONE: Record<string, string> = {
  favorable_both_methods_agree: "text-sage",
  unfavorable_both_methods_agree: "text-red-muted",
};

/**
 * Transits (Gochara) tab -- current planetary transits vs. natal Moon,
 * combining the simple good-house-from-Moon heuristic with the classical
 * Ashtakavarga bindu verdict (app.derived.gochara), plus Sade Sati status.
 * Broken out as its own tab per Ajay's ask.
 */
export function TransitsPanel({ fullContext }: { fullContext: FullContext }) {
  const gochara = fullContext.gochara as
    | { planets: Record<string, TransitPlanetEntry>; sade_sati: { active: boolean; phase?: number; label?: string } }
    | undefined;

  if (!gochara) return <p className="text-ink-muted">Transit data unavailable.</p>;

  return (
    <div className="space-y-4">
      <div
        className={`flex items-center gap-2 rounded-lg border p-4 text-sm shadow-sm ${
          gochara.sade_sati.active ? "border-amber/30 bg-amber/5 text-amber" : "border-sage/30 bg-sage/5 text-sage"
        }`}
      >
        {gochara.sade_sati.active ? <AlertTriangle size={16} /> : <CheckCircle2 size={16} />}
        <span>
          Sade Sati: <b>{gochara.sade_sati.active ? `Active -- ${gochara.sade_sati.label}` : "Not active"}</b>
        </span>
      </div>

      <div className="overflow-x-auto rounded-lg border border-ink/10 bg-surface p-4 shadow-sm">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-xs uppercase tracking-wide text-ink-muted">
              <th className="pb-2 pr-3">Planet</th>
              <th className="pb-2 pr-3">Transit Sign</th>
              <th className="pb-2 pr-3">House from Moon</th>
              <th className="pb-2 pr-3">SAV Bindus</th>
              <th className="pb-2 pr-3">Methods Agree</th>
              <th className="pb-2">Verdict</th>
            </tr>
          </thead>
          <tbody>
            {PLANET_ORDER.filter((p) => gochara.planets[p]).map((planet) => {
              const entry = gochara.planets[planet];
              const av = entry.ashtakavarga_gochara as { sav_bindus?: number };
              return (
                <tr key={planet} className="border-b border-ink/5 last:border-0">
                  <td className="py-1.5 pr-3 font-medium">{planet}</td>
                  <td className="py-1.5 pr-3">{entry.transit_sign_en}</td>
                  <td className="py-1.5 pr-3">H{entry.simple_gochara.house_from_moon}</td>
                  <td className="py-1.5 pr-3">{av.sav_bindus ?? "--"}</td>
                  <td className="py-1.5 pr-3">{entry.methods_agree ? "Yes" : "No"}</td>
                  <td className={`py-1.5 font-medium ${VERDICT_TONE[entry.combined_verdict] ?? "text-ink-muted"}`}>
                    {entry.combined_verdict.replace(/_/g, " ")}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
