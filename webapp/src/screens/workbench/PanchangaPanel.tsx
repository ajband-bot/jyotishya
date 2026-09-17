import type { FullContext } from "../../lib/api";

interface PanchangaLimb {
  number: number;
  name: string;
  percentage_complete: number;
  [key: string]: unknown;
}

function LimbCard({ title, limb, extra }: { title: string; limb: PanchangaLimb; extra?: React.ReactNode }) {
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
 * Panchanga tab -- the 5 classical limbs (Vara/Tithi/Nakshatra/Yoga/
 * Karana) at the birth moment, straight from app.astro.panchanga. Broken
 * out as its own tab per Ajay's ask, rather than folded into the generic
 * Strength & Timing evidence grid.
 */
export function PanchangaPanel({ fullContext }: { fullContext: FullContext }) {
  const panchanga = fullContext.panchanga as
    | {
        vara: { number: number; name: string; lord: string; day_boundary: string };
        tithi: PanchangaLimb & { paksha: string };
        nakshatra: PanchangaLimb & { lord: string; pada: number };
        yoga: PanchangaLimb;
        karana: PanchangaLimb;
      }
    | undefined;

  if (!panchanga) return <p className="text-ink-muted">Panchanga data unavailable.</p>;

  return (
    <div>
      <p className="mb-3 text-xs text-ink-muted">
        Instant-in-time values at the birth moment (civil-midnight Vara boundary, not sunrise-anchored --
        see app/astro/panchanga.py's own disclosed data_gap).
      </p>
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        <div className="rounded-lg border border-ink/10 bg-surface p-4 shadow-sm">
          <p className="mb-1 text-xs font-semibold uppercase tracking-wide text-ink-muted">Vara (Weekday)</p>
          <p className="text-lg font-semibold font-scripture text-indigo">{panchanga.vara.name}</p>
          <p className="text-xs text-ink-muted">Lord: {panchanga.vara.lord}</p>
        </div>
        <LimbCard
          title="Tithi"
          limb={panchanga.tithi}
          extra={<p className="text-xs text-ink-muted">{panchanga.tithi.paksha} Paksha</p>}
        />
        <LimbCard
          title="Nakshatra"
          limb={panchanga.nakshatra}
          extra={<p className="text-xs text-ink-muted">Lord: {panchanga.nakshatra.lord} -- Pada {panchanga.nakshatra.pada}</p>}
        />
        <LimbCard title="Yoga" limb={panchanga.yoga} />
        <LimbCard title="Karana" limb={panchanga.karana} />
      </div>
    </div>
  );
}
