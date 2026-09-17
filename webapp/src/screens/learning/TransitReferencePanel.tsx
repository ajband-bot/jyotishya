import { useQuery } from "@tanstack/react-query";
import { api, type TransitHouseEffect } from "../../lib/api";

const QUALITY_COLOR: Record<string, string> = {
  auspicious: "bg-sage/15 border-sage/30 text-sage",
  mixed: "bg-ink/5 border-ink/10 text-ink-muted",
  challenging: "bg-red-muted/10 border-red-muted/30 text-red-muted",
  sade_sati: "bg-red-muted/10 border-red-muted/30 text-red-muted",
  kantaka: "bg-amber/10 border-amber/30 text-amber",
  neutral: "bg-ink/5 border-ink/10 text-ink-muted",
};

function HouseGrid({ title, houses }: { title: string; houses: Record<string, TransitHouseEffect> }) {
  return (
    <div className="mb-6">
      <h4 className="font-semibold font-scripture mb-2">{title}</h4>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
        {Object.entries(houses).map(([house, info]) => (
          <div
            key={house}
            className={`rounded-lg border p-3 text-xs ${QUALITY_COLOR[info.quality] ?? "bg-ink/5 border-ink/10"}`}
          >
            <div className="flex items-center justify-between mb-1">
              <span className="font-semibold">H{house}</span>
              <span className="uppercase text-[10px] tracking-wide">{info.quality.replace("_", " ")}</span>
            </div>
            <p>{info.effect}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

function SadeSatiTimeline({ phases }: { phases: Array<{ phase: number; label: string; house_from_moon: number; duration_years: number }> }) {
  return (
    <div className="rounded-lg border border-ink/10 bg-surface p-4 shadow-sm">
      <h4 className="font-semibold font-scripture mb-3">Sade Sati -- 3-Phase Timeline (~7.5 years total)</h4>
      <div className="flex items-stretch gap-1">
        {phases.map((p) => (
          <div key={p.phase} className="flex-1 rounded-md border border-red-muted/30 bg-red-muted/5 p-3 text-center">
            <p className="text-xs text-ink-muted">Phase {p.phase}</p>
            <p className="font-semibold text-red-muted">{p.label}</p>
            <p className="text-xs mt-1">House {p.house_from_moon} from Moon</p>
            <p className="text-xs text-ink-muted">~{p.duration_years} years</p>
          </div>
        ))}
      </div>
    </div>
  );
}

/**
 * Transit (Gochara) Impacts Reference -- Jupiter/Saturn house-from-Moon
 * effect doctrine + Sade Sati 3-phase timeline. Chart-independent; reuses
 * the exact classification sets the live transit engine computes with.
 */
export function TransitReferencePanel() {
  const { data } = useQuery({ queryKey: ["ref-transits"], queryFn: api.getTransitReference });
  if (!data) return <p className="text-ink-muted">Loading...</p>;

  return (
    <div>
      <p className="text-xs text-ink-muted mb-4">Source: {data.citation}</p>
      <SadeSatiTimeline phases={data.sade_sati_phases} />
      <div className="mt-6">
        <HouseGrid title="Jupiter Transit from Moon (Gochara)" houses={data.jupiter_from_moon} />
        <HouseGrid title="Saturn Transit from Moon (Gochara)" houses={data.saturn_from_moon} />
      </div>
    </div>
  );
}
