import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Sun, CalendarDays } from "lucide-react";
import { api } from "../lib/api";

function todayIso(): string {
  return new Date().toISOString().slice(0, 10);
}

interface Limb {
  number: number;
  name: string;
  percentage_complete: number;
}

function LimbCard({ title, limb, extra }: { title: string; limb: Limb; extra?: React.ReactNode }) {
  return (
    <div className="rounded-lg border border-ink/10 bg-surface p-4 shadow-sm">
      <p className="mb-1 text-xs font-semibold uppercase tracking-wide text-ink-muted">{title}</p>
      <p className="text-lg font-semibold font-scripture text-indigo">{limb.name}</p>
      <p className="text-xs text-ink-muted">#{limb.number} -- {limb.percentage_complete}% complete</p>
      {extra}
    </div>
  );
}

/**
 * Generic Panchanga -- Phase 8 follow-up ask: a chart-INDEPENDENT view of
 * today's (or any date's) 5 classical limbs, no case/native selection
 * required. Reuses GET /api/v2/today/panchanga, which itself reuses the
 * exact same app.astro.panchanga engine the per-chart Workbench tab uses,
 * just fed today's Sun/Moon longitude instead of a birth-moment one.
 */
export function TodayPanchanga() {
  const [onDate, setOnDate] = useState(todayIso());
  const { data, isLoading } = useQuery({
    queryKey: ["today-panchanga", onDate],
    queryFn: () => api.getTodayPanchanga(onDate),
  });

  return (
    <div>
      <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <Sun size={18} className="text-gold" aria-hidden="true" />
          <h2 className="font-scripture text-xl font-semibold text-indigo">Panchanga</h2>
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
        Instant-in-time values at local noon (civil-midnight Vara boundary, not sunrise-anchored -- see
        app/astro/panchanga.py's own disclosed data_gap). Not tied to any birth chart.
      </p>

      {isLoading && <p className="text-ink-muted">Computing...</p>}
      {data && (
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          <div className="rounded-lg border border-ink/10 bg-surface p-4 shadow-sm">
            <p className="mb-1 text-xs font-semibold uppercase tracking-wide text-ink-muted">Vara (Weekday)</p>
            <p className="text-lg font-semibold font-scripture text-indigo">{data.vara.name}</p>
            <p className="text-xs text-ink-muted">Lord: {data.vara.lord}</p>
          </div>
          <LimbCard title="Tithi" limb={data.tithi} extra={<p className="text-xs text-ink-muted">{data.tithi.paksha} Paksha</p>} />
          <LimbCard
            title="Nakshatra"
            limb={data.nakshatra}
            extra={<p className="text-xs text-ink-muted">Lord: {data.nakshatra.lord} -- Pada {data.nakshatra.pada}</p>}
          />
          <LimbCard title="Yoga" limb={data.yoga} />
          <LimbCard title="Karana" limb={data.karana} />
        </div>
      )}
    </div>
  );
}
