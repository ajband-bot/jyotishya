import { useState } from "react";
import type { SandboxAnalysis } from "../../lib/api";
import { PLANET_COLOR } from "./layout";

const TAG_COLOR: Record<string, string> = {
  YK: "bg-gold text-white",
  "++": "bg-sage text-white",
  "+": "bg-sage/60 text-white",
  "0": "bg-ink/10 text-ink",
  "-": "bg-amber/60 text-white",
  "--": "bg-red-muted text-white",
  M: "bg-red-muted/70 text-white",
  LL: "bg-indigo text-white",
};

const DOSHA_LABELS: Record<string, string> = {
  mangal_dosha: "Mangal Dosha",
  kala_sarpa: "Kala Sarpa",
  pitru_dosha: "Pitru Dosha",
  guru_chandala: "Guru Chandala",
  kemadruma: "Kemadruma",
  papakartari: "Papakartari",
};

function SectionCard({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="rounded-lg border border-ink/10 bg-surface p-4 shadow-sm mb-4">
      <h4 className="font-semibold font-scripture mb-2">{title}</h4>
      {children}
    </div>
  );
}

export function ObservationsPanel({
  result,
  onSelectPlanet,
  onSelectHouse,
  selectedHouse,
}: {
  result: SandboxAnalysis;
  onSelectPlanet: (planet: string) => void;
  onSelectHouse: (house: number) => void;
  selectedHouse: number | null;
}) {
  const [tab, setTab] = useState<"planets" | "houses" | "yogas" | "doshas">("planets");

  const activeDoshas = Object.entries(result.doshas).filter(([, d]) => d.present);

  return (
    <div>
      <SectionCard title="Snapshot">
        <p className="text-sm">
          Lagna: <span className="font-semibold">{result.lagna_sign_en}</span>
          {result.yoga_karakas.length > 0 && (
            <span className="ml-3">
              Yoga Karaka(s): <span className="font-semibold text-gold">{result.yoga_karakas.join(", ")}</span>
            </span>
          )}
        </p>
        {activeDoshas.length > 0 ? (
          <p className="text-xs text-red-muted mt-1">
            Doshas present: {activeDoshas.map(([k]) => DOSHA_LABELS[k] ?? k).join(", ")}
          </p>
        ) : (
          <p className="text-xs text-sage mt-1">No doshas flagged (of the 6 checked).</p>
        )}
        {result.yogas.length > 0 && (
          <p className="text-xs text-indigo mt-1">
            Yogas detected: {result.yogas.map((y) => y.name).join(", ")}
          </p>
        )}
      </SectionCard>

      <div className="mb-3 flex gap-2">
        {(["planets", "houses", "yogas", "doshas"] as const).map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            role="tab"
            aria-selected={tab === t}
            className={`rounded-md px-3 py-1.5 text-sm font-medium capitalize transition-colors ${
              tab === t ? "bg-indigo text-white" : "bg-surface border border-ink/20"
            }`}
          >
            {t}
          </button>
        ))}
      </div>

      {tab === "planets" && (
        <div className="grid gap-2 md:grid-cols-2">
          {Object.entries(result.planets).map(([planet, p]) => (
            <div
              key={planet}
              onClick={() => onSelectPlanet(planet)}
              className="cursor-pointer rounded-lg border border-ink/10 bg-surface p-3 text-xs hover:border-indigo/40"
            >
              <div className="flex items-center justify-between mb-1">
                <span className="font-semibold flex items-center gap-1">
                  <span
                    className="inline-block h-2.5 w-2.5 rounded-full"
                    style={{ background: PLANET_COLOR[planet] }}
                  />
                  {planet}
                </span>
                {p.functional && (
                  <span className={`px-1.5 py-0.5 rounded text-[10px] font-semibold ${TAG_COLOR[p.functional.tag] ?? "bg-ink/10"}`}>
                    {p.functional.tag}
                  </span>
                )}
              </div>
              <p className="text-ink-muted">
                {p.sign_en} H{p.house} -- {p.dignity !== "n/a" ? p.dignity : "node"}
                {p.retrograde && " (R)"}
                {p.vargottama && " -- Vargottama"}
              </p>
              {p.territory !== "n/a" && <p className="text-ink-muted">{p.territory.replace("_", " ")}</p>}
              {p.combust && <p className="text-red-muted">combust</p>}
              {p.shadbala && (
                <p className="mt-1">
                  Shadbala: <span className="font-medium">{p.shadbala.total_score}</span> ({p.shadbala.verdict})
                </p>
              )}
              {p.ishta_kashta && (
                <p className="text-ink-muted">
                  Ishta {p.ishta_kashta.ishta} / Kashta {p.ishta_kashta.kashta} ({p.ishta_kashta.verdict})
                </p>
              )}
              <p className="text-ink-muted">Aspects houses: {p.aspects_houses.join(", ")}</p>
            </div>
          ))}
        </div>
      )}

      {tab === "houses" && (
        <div className="grid gap-2 md:grid-cols-2">
          {Object.entries(result.houses).map(([house, h]) => {
            const conn = result.house_connections[house];
            return (
              <button
                key={house}
                onClick={() => onSelectHouse(Number(house))}
                className={`w-full rounded-lg border p-3 text-left text-xs transition-colors ${selectedHouse === Number(house) ? "border-gold bg-gold/10 ring-1 ring-gold/50" : "border-ink/10 bg-surface hover:border-gold/50"}`}
              >
                <p className="font-semibold mb-1">
                  H{house} ({h.theme.core}) -- Lord: {h.lord}
                </p>
                <p className="text-ink-muted">Occupants: {h.occupants.join(", ") || "empty"}</p>
                <p className="text-ink-muted">Aspected by: {h.aspected_by.join(", ") || "none"}</p>
                {conn && (
                  <p className="mt-1 text-indigo">
                    H{house} -&gt; H{conn.lord_house} ({conn.lord}
                    {conn.is_self_placed ? " in its own house" : ""}): {conn.connection}
                  </p>
                )}
              </button>
            );
          })}
        </div>
      )}

      {tab === "yogas" && (
        <div className="space-y-2">
          {result.yogas.length === 0 && <p className="text-ink-muted text-sm">No yogas detected for this placement.</p>}
          {result.yogas.map((y, i) => (
            <div key={i} className="rounded-lg border border-indigo/20 bg-indigo/5 p-3 text-sm">
              <p className="font-semibold">{y.name}</p>
              <p className="text-ink-muted text-xs">{y.effect}</p>
              <p className="text-[10px] text-ink-muted mt-1">strength: {y.strength}</p>
            </div>
          ))}
        </div>
      )}

      {tab === "doshas" && (
        <div className="grid gap-2 md:grid-cols-2">
          {Object.entries(result.doshas).map(([key, d]) => (
            <div
              key={key}
              className={`rounded-lg border p-3 text-xs ${
                d.present ? "border-red-muted/30 bg-red-muted/5" : "border-sage/30 bg-sage/5"
              }`}
            >
              <p className="font-semibold">{DOSHA_LABELS[key] ?? key}</p>
              <p className={d.present ? "text-red-muted" : "text-sage"}>
                {d.present ? "Present" : "Not present"}
              </p>
              <p className="text-ink-muted mt-1">{String(d.citation)}</p>
            </div>
          ))}
        </div>
      )}

      <details className="mt-4 text-xs text-ink-muted">
        <summary className="cursor-pointer">Data gaps (what this sandbox can't compute)</summary>
        <ul className="list-disc list-inside mt-2 space-y-1">
          {result.data_gaps.map((gap, i) => (
            <li key={i}>{gap}</li>
          ))}
        </ul>
      </details>
    </div>
  );
}
