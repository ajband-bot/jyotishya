import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Orbit, CalendarDays } from "lucide-react";
import { api } from "../lib/api";

function todayIso(): string {
  return new Date().toISOString().slice(0, 10);
}

const PLANET_ORDER = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"];

/**
 * Generic Transits -- Phase 8 follow-up ask: a chart-INDEPENDENT view of
 * today's (or any date's) real sidereal planetary positions, no
 * case/native selection required. Reuses GET /api/v2/today/transits
 * (app.astro.transits.transit_chart -- location-independent, real Swiss
 * Ephemeris positions). House-from-Lagna and Sade Sati are inherently
 * natal-specific and remain on the Chart Workbench's per-chart Transits
 * tab, not here.
 */
export function TodayTransits() {
  const [onDate, setOnDate] = useState(todayIso());
  const { data, isLoading } = useQuery({
    queryKey: ["today-transits", onDate],
    queryFn: () => api.getTodayTransits(onDate),
  });

  return (
    <div>
      <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <Orbit size={18} className="text-indigo" aria-hidden="true" />
          <h2 className="font-scripture text-xl font-semibold text-indigo">Planet Transits</h2>
        </div>
        <label className="flex items-center gap-2 text-sm text-ink-muted">
          <CalendarDays size={14} />
          <input
            type="date"
            className="rounded-md border border-ink/20 bg-surface px-2 py-1 text-sm"
            value={onDate}
            onChange={(e) => setOnDate(e.target.value)}
          />
        </label>
      </div>
      <p className="mb-4 text-xs text-ink-muted">
        Real sidereal positions (Lahiri) at local noon -- not tied to any birth chart. Retrograde,
        nakshatra/pada, and daily motion shown for all 9 grahas.
      </p>

      {isLoading && <p className="text-ink-muted">Computing...</p>}
      {data && (
        <div className="overflow-x-auto rounded-lg border border-ink/10 bg-surface p-4 shadow-sm">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-xs uppercase tracking-wide text-ink-muted">
                <th className="pb-2 pr-3">Planet</th>
                <th className="pb-2 pr-3">Sign</th>
                <th className="pb-2 pr-3">Degree</th>
                <th className="pb-2 pr-3">Nakshatra</th>
                <th className="pb-2 pr-3">Pada</th>
                <th className="pb-2 pr-3">Motion</th>
                <th className="pb-2">Speed (deg/day)</th>
              </tr>
            </thead>
            <tbody>
              {PLANET_ORDER.filter((p) => data.planets[p]).map((planet) => {
                const p = data.planets[planet];
                return (
                  <tr key={planet} className="border-b border-ink/5 last:border-0">
                    <td className="py-1.5 pr-3 font-medium">{planet}</td>
                    <td className="py-1.5 pr-3">{p.sign_en}</td>
                    <td className="py-1.5 pr-3">{p.deg_in_sign.toFixed(2)}°</td>
                    <td className="py-1.5 pr-3">{p.nakshatra}</td>
                    <td className="py-1.5 pr-3">{p.pada}</td>
                    <td className={`py-1.5 pr-3 ${p.retrograde ? "text-amber font-medium" : "text-ink-muted"}`}>
                      {p.retrograde ? "Retrograde" : "Direct"}
                    </td>
                    <td className="py-1.5 text-ink-muted">{p.speed.toFixed(4)}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
