import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { api, type PlanetLabProfile } from "../lib/api";

const PLANETS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"];

const VERDICT_COLOR: Record<string, string> = {
  very_strong: "text-sage", strong: "text-sage",
  moderate: "text-amber", weak: "text-red-muted",
  high_ishta: "text-sage", balanced: "text-amber", high_kashta: "text-red-muted",
};

const COMPONENT_LABELS: Record<string, string> = {
  sthana_bala: "Positional (Sthana)",
  dig_bala: "Directional (Dig)",
  kala_bala: "Temporal (Kala)",
  chesta_bala: "Motional (Chesta)",
  naisargika_bala: "Natural (Naisargika)",
  drik_bala: "Aspectual (Drik)",
};

function ComponentBar({ label, value }: { label: string; value: number }) {
  return (
    <div className="flex items-center gap-2 text-xs">
      <span className="w-40 text-ink-muted shrink-0">{label}</span>
      <div className="flex-1 h-2 rounded-full bg-ink/10 overflow-hidden">
        <div className="h-full bg-indigo" style={{ width: `${value * 100}%` }} />
      </div>
      <span className="w-10 text-right text-ink-muted">{(value * 100).toFixed(0)}%</span>
    </div>
  );
}

function PlanetCard({ planet, profile }: { planet: string; profile: PlanetLabProfile }) {
  return (
    <div className="rounded-lg border border-ink/10 bg-surface p-4 shadow-sm">
      <div className="flex items-center justify-between mb-2">
        <h4 className="font-semibold font-scripture text-lg">{planet}</h4>
        <span className="text-xs px-2 py-0.5 rounded-full border border-indigo/30 bg-indigo/10 text-indigo">
          {profile.functional.tag} -- {profile.functional.classification}
        </span>
      </div>

      <div className="grid grid-cols-2 gap-2 text-xs text-ink-muted mb-3">
        <span>Sign: <b className="text-ink">{profile.sign_en}</b> ({profile.deg_in_sign.toFixed(2)}°)</span>
        <span>House: <b className="text-ink">{profile.house}</b></span>
        <span>D9: <b className="text-ink">{profile.d9_sign_en}</b> ({profile.d9_state}){profile.vargottama && " -- Vargottama"}</span>
        <span>{profile.retrograde ? "Retrograde" : "Direct"}{profile.combust ? ` -- Combust (${profile.combustion_orb_deg?.toFixed(1)}°)` : ""}</span>
      </div>

      <div className="space-y-1 mb-3">
        {Object.entries(profile.shadbala.components).map(([key, value]) => (
          <ComponentBar key={key} label={COMPONENT_LABELS[key] ?? key} value={value} />
        ))}
      </div>

      <div className="flex items-center justify-between text-sm border-t border-ink/5 pt-2">
        <span>
          Shadbala: <b className={VERDICT_COLOR[profile.shadbala.verdict]}>{profile.shadbala.verdict}</b>{" "}
          ({profile.shadbala.total_score.toFixed(1)})
        </span>
        <span>
          Ishta/Kashta: <b className={VERDICT_COLOR[profile.ishta_kashta.verdict]}>{profile.ishta_kashta.verdict}</b>
        </span>
      </div>

      {profile.aspected_by.length > 0 && (
        <p className="mt-2 text-xs text-ink-muted">Aspected by: {profile.aspected_by.join(", ")}</p>
      )}
    </div>
  );
}

/**
 * Planet Lab (spec 7.4) -- transparent per-graha profile for the selected
 * chart. Every number here comes straight from the same build_chart_context
 * every other screen uses -- this IS the "Why?" evidence for functional
 * nature, Shadbala, and Ishta/Kashta verdicts, laid out for teaching.
 */
export function PlanetLab({ chartId }: { chartId: string }) {
  const [focused, setFocused] = useState<string | null>(null);
  const { data, isLoading } = useQuery({
    queryKey: ["planet-lab", chartId],
    queryFn: () => api.getPlanetLab(chartId),
  });

  if (isLoading) return <p className="text-ink-muted">Computing Shadbala + Ishta/Kashta for all 9 grahas...</p>;
  if (!data) return null;

  const shown = focused ? [focused] : PLANETS;

  return (
    <div>
      <div className="mb-4 flex flex-wrap gap-2">
        <button
          onClick={() => setFocused(null)}
          className={`rounded-md px-3 py-1 text-xs font-medium ${!focused ? "bg-indigo text-white" : "bg-surface border border-ink/20"}`}
        >
          All
        </button>
        {PLANETS.map((p) => (
          <button
            key={p}
            onClick={() => setFocused(p)}
            className={`rounded-md px-3 py-1 text-xs font-medium ${focused === p ? "bg-indigo text-white" : "bg-surface border border-ink/20"}`}
          >
            {p}
          </button>
        ))}
      </div>
      <div className="grid gap-4 md:grid-cols-2">
        {shown.map((p) => (
          <PlanetCard key={p} planet={p} profile={data.planets[p]} />
        ))}
      </div>
    </div>
  );
}
