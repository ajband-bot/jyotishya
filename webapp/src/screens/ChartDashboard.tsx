import { Sparkles, Compass, Clock, Network } from "lucide-react";
import type { ChartDetail } from "../lib/api";

const SIGN_NAMES = [
  "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
  "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
];

function StatCard({
  icon,
  label,
  value,
  sub,
}: {
  icon: React.ReactNode;
  label: string;
  value: string;
  sub?: string;
}) {
  return (
    <div className="rounded-lg border border-ink/10 bg-surface p-4 shadow-sm">
      <div className="flex items-center gap-2 text-ink-muted text-xs uppercase tracking-wide">
        {icon}
        {label}
      </div>
      <div className="mt-1 text-lg font-semibold text-indigo">{value}</div>
      {sub && <div className="text-xs text-ink-muted mt-0.5">{sub}</div>}
    </div>
  );
}

/**
 * Chart Dashboard -- spec 17.1 / 30.
 * Within 10 seconds the user should see: Lagna, current Dasha, and the
 * house-lord / yoga-karaka summary. Deeper heat maps / Sankey / Planet Lab
 * views are later Phase-2 screens per docs/technical-architecture.md 11.
 */
export function ChartDashboard({ chart }: { chart: ChartDetail }) {
  const lagna = chart.d1.Lagna;
  const moon = chart.d1.Moon;
  const md = chart.current_dasha.mahadasha;
  const ad = chart.current_dasha.antardasha;
  const pd = chart.current_dasha.pratyantardasha;
  const d9 = chart.vargas.D9;

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
        <StatCard
          icon={<Compass size={14} />}
          label="Lagna"
          value={SIGN_NAMES[lagna.sign - 1]}
          sub={`${lagna.deg_in_sign.toFixed(2)} deg`}
        />
        <StatCard
          icon={<Sparkles size={14} />}
          label="Moon"
          value={SIGN_NAMES[moon.sign - 1]}
          sub={`House ${moon.house}`}
        />
        <StatCard
          icon={<Clock size={14} />}
          label="Current Dasha"
          value={md ? `${md.planet} / ${ad?.planet ?? "-"}` : "-"}
          sub={pd ? `PD: ${pd.planet}` : undefined}
        />
        <StatCard
          icon={<Network size={14} />}
          label="Yoga Karakas"
          value={chart.yoga_karakas.length > 0 ? chart.yoga_karakas.join(", ") : "None"}
        />
      </div>

      <div className="rounded-lg border border-ink/10 bg-surface p-5 shadow-sm">
        <h3 className="mb-3 text-base font-semibold font-scripture">House Lordship (D1, Whole Sign)</h3>
        <div className="grid grid-cols-6 gap-2 text-sm">
          {Object.entries(chart.house_lords).map(([house, lord]) => (
            <div key={house} className="rounded-md bg-bg p-2 text-center border border-ink/5">
              <div className="text-[10px] text-ink-muted">H{house}</div>
              <div className="font-medium">{lord}</div>
            </div>
          ))}
        </div>
      </div>

      <div className="rounded-lg border border-ink/10 bg-surface p-5 shadow-sm">
        <h3 className="mb-3 text-base font-semibold font-scripture">
          D9 Navamsha -- Lagna: {d9.lagna_sign_en}
        </h3>
        <p className="text-sm text-ink-muted mb-3">{d9.significance}</p>
        {d9.vargottama.length > 0 && (
          <div className="rounded-md border border-gold/30 bg-gold/5 p-3 text-sm">
            <span className="font-medium text-gold">Vargottama: </span>
            {d9.vargottama.join(", ")} (same sign in D1 and D9 -- maximum strength signature)
          </div>
        )}
      </div>
    </div>
  );
}
