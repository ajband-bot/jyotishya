import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { api } from "../lib/api";
import { DashaReferencePanel } from "./learning/DashaReferencePanel";
import { TransitReferencePanel } from "./learning/TransitReferencePanel";
import { TopRulesPanel } from "./learning/TopRulesPanel";
import { PlanetRelationshipGraphPanel } from "./learning/PlanetRelationshipGraphPanel";
import { LordPlacementDiagram } from "./learning/LordPlacementDiagram";
import { ConceptLibraryPanel } from "./learning/ConceptLibraryPanel";
import { ArrowRight, BookOpen } from "lucide-react";

const SIGN_NAMES = [
  "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
  "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
];
const PLANETS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"];

const NATURE_COLOR: Record<string, string> = {
  trikona: "bg-sage/15 text-sage border-sage/30",
  kendra: "bg-indigo/10 text-indigo border-indigo/30",
  dusthana: "bg-red-muted/10 text-red-muted border-red-muted/30",
  upachaya: "bg-gold/10 text-gold border-gold/30",
  neutral: "bg-ink/5 text-ink-muted border-ink/10",
};

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

type SubTab =
  | "house-themes"
  | "functional-nature"
  | "relationships"
  | "relationship-graph"
  | "dignity"
  | "lord-placement"
  | "dasha"
  | "transits"
  | "top-rules"
  | "concept-library";

const SUB_TABS: Array<{ id: SubTab; label: string }> = [
  { id: "house-themes", label: "House Themes" },
  { id: "functional-nature", label: "Functional Nature Grid" },
  { id: "relationship-graph", label: "Friends / Enemies Graph" },
  { id: "relationships", label: "Friends / Enemies Table" },
  { id: "dignity", label: "Dignity Table" },
  { id: "lord-placement", label: "Lord Placement Connections" },
  { id: "dasha", label: "Vimsottari Dasha" },
  { id: "transits", label: "Transit Impacts" },
  { id: "top-rules", label: "Top 30 Rules" },
  { id: "concept-library", label: "Concept Library (Cheat Sheet)" },
];

function HouseThemesPanel() {
  const { data } = useQuery({ queryKey: ["ref-house-themes"], queryFn: api.getHouseThemes });
  if (!data) return <p className="text-ink-muted">Loading...</p>;
  return (
    <div className="grid gap-3 md:grid-cols-2">
      {Object.values(data.houses).map((h) => (
        <div key={h.house} className="rounded-lg border border-ink/10 bg-surface p-4 shadow-sm">
          <div className="flex items-center justify-between mb-1">
            <h4 className="font-semibold font-scripture">
              H{h.house} -- {h.name_en}
            </h4>
            <span
              className={`text-[11px] px-2 py-0.5 rounded-full border ${NATURE_COLOR[h.nature]}`}
            >
              {h.nature}
              {h.is_maraka_house ? " / maraka" : ""}
            </span>
          </div>
          <p className="text-xs text-ink-muted mb-2">{h.name_tel} -- Karakas: {h.karakas.join(", ")}</p>
          <table className="w-full text-xs">
            <tbody>
              <tr><td className="pr-2 text-ink-muted w-20">Core</td><td>{h.core}</td></tr>
              <tr><td className="pr-2 text-ink-muted">Material</td><td>{h.material}</td></tr>
              <tr><td className="pr-2 text-ink-muted">Higher</td><td>{h.higher}</td></tr>
            </tbody>
          </table>
        </div>
      ))}
    </div>
  );
}

function FunctionalNatureGridPanel() {
  const { data } = useQuery({ queryKey: ["ref-functional-nature"], queryFn: api.getFunctionalNatureGrid });
  if (!data) return <p className="text-ink-muted">Loading...</p>;
  return (
    <div>
      <p className="text-sm text-amber mb-3 rounded-md border border-amber/30 bg-amber/5 p-2">
        {data.disclaimer}
      </p>
      <div className="overflow-x-auto rounded-lg border border-ink/10 bg-surface shadow-sm">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-ink/10">
              <th className="p-2 text-left text-xs text-ink-muted">Lagna</th>
              {PLANETS.map((p) => (
                <th key={p} className="p-2 text-xs text-ink-muted">{p}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {Object.entries(data.grid).map(([lagnaSign, row]) => (
              <tr key={lagnaSign} className="border-b border-ink/5 last:border-0">
                <td className="p-2 font-medium">{row.lagna_sign_en}</td>
                {PLANETS.map((p) => {
                  const cell = row.planets[p];
                  return (
                    <td key={p} className="p-2 text-center">
                      <span
                        title={`${cell.classification} (H${cell.houses_owned.join(",")})`}
                        className={`inline-block min-w-[2rem] rounded-md px-2 py-1 text-xs font-semibold ${TAG_COLOR[cell.tag] ?? "bg-ink/10"}`}
                      >
                        {cell.tag}
                      </span>
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="mt-3 flex flex-wrap gap-3 text-xs text-ink-muted">
        {Object.entries(data.legend).map(([tag, label]) => (
          <span key={tag} className="flex items-center gap-1">
            <span className={`inline-block rounded px-1.5 py-0.5 font-semibold ${TAG_COLOR[tag] ?? "bg-ink/10"}`}>
              {tag}
            </span>
            {label}
          </span>
        ))}
      </div>
    </div>
  );
}

function RelationshipsPanel() {
  const { data } = useQuery({ queryKey: ["ref-relationships"], queryFn: api.getNaturalRelationships });
  if (!data) return <p className="text-ink-muted">Loading...</p>;
  return (
    <div>
      <p className="text-xs text-ink-muted mb-3">Source: {data.source} (status: {data.citation_status})</p>
      <div className="grid gap-3 md:grid-cols-2">
        {PLANETS.map((planet) => {
          const rel = data.table[planet];
          return (
            <div key={planet} className="rounded-lg border border-ink/10 bg-surface p-4 shadow-sm">
              <h4 className="font-semibold mb-2 font-scripture">{planet}</h4>
              <div className="space-y-1 text-sm">
                <p><span className="text-sage font-medium">Friends: </span>{rel.friends.join(", ") || "None"}</p>
                <p><span className="text-ink-muted font-medium">Neutral: </span>{rel.neutral.join(", ") || "None"}</p>
                <p><span className="text-red-muted font-medium">Enemies: </span>{rel.enemies.join(", ") || "None"}</p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function DignityPanel() {
  const { data } = useQuery({ queryKey: ["ref-dignity"], queryFn: api.getDignityTable });
  if (!data) return <p className="text-ink-muted">Loading...</p>;
  return (
    <div className="overflow-x-auto rounded-lg border border-ink/10 bg-surface shadow-sm">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-ink/10 text-xs text-ink-muted">
            <th className="p-2 text-left">Planet</th>
            <th className="p-2 text-left">Exalted</th>
            <th className="p-2 text-left">Debilitated</th>
            <th className="p-2 text-left">Own Sign(s)</th>
            <th className="p-2 text-left">Moolatrikona</th>
          </tr>
        </thead>
        <tbody>
          {PLANETS.map((planet) => {
            const d = data.dignity[planet];
            return (
              <tr key={planet} className="border-b border-ink/5 last:border-0">
                <td className="p-2 font-medium">{planet}</td>
                <td className="p-2 text-sage">{d.exalted_sign} ({d.exalted_degree}°)</td>
                <td className="p-2 text-red-muted">{d.debilitated_sign}</td>
                <td className="p-2">{d.own_signs.join(", ")}</td>
                <td className="p-2">
                  {d.moolatrikona_sign} ({d.moolatrikona_range_deg[0]}-{d.moolatrikona_range_deg[1]}°)
                  {d.moolatrikona_citation_status === "pending_audit" && (
                    <span className="ml-1 text-[10px] text-amber border border-amber/30 rounded px-1">
                      pending audit
                    </span>
                  )}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

function LordPlacementPanel() {
  const [lagna, setLagna] = useState(1);
  const [showFullMatrix, setShowFullMatrix] = useState(false);
  const { data } = useQuery({
    queryKey: ["ref-lord-placement", lagna],
    queryFn: () => api.getLordPlacementConnections(lagna),
  });

  return (
    <div>
      <div className="mb-3 flex items-center gap-2">
        <label className="text-sm text-ink-muted">Lagna:</label>
        <select
          className="rounded-md border border-ink/20 bg-surface px-2 py-1 text-sm"
          value={lagna}
          onChange={(e) => setLagna(Number(e.target.value))}
        >
          {SIGN_NAMES.map((s, i) => (
            <option key={s} value={i + 1}>{s}</option>
          ))}
        </select>
      </div>
      {data && (
        <>
          <p className="text-xs text-ink-muted mb-3">{data.note}</p>
          <LordPlacementDiagram data={data} />
          <button
            onClick={() => setShowFullMatrix(!showFullMatrix)}
            className="mt-4 mb-2 text-xs text-indigo underline"
          >
            {showFullMatrix ? "Hide" : "Show"} full 12x12 numeric matrix
          </button>
          {showFullMatrix && (
            <div className="overflow-x-auto rounded-lg border border-ink/10 bg-surface shadow-sm">
              <table className="w-full text-[11px]">
                <thead>
                  <tr className="border-b border-ink/10">
                    <th className="p-2 text-left">Lord of...</th>
                    {Array.from({ length: 12 }, (_, i) => i + 1).map((h) => (
                      <th key={h} className="p-1 text-left">H{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(data.matrix).map(([sourceHouse, row]) => (
                    <tr key={sourceHouse} className="border-b border-ink/5 last:border-0">
                      <td className="p-2 font-medium">H{sourceHouse} ({row.lord})</td>
                      {Array.from({ length: 12 }, (_, i) => i + 1).map((destHouse) => (
                        <td key={destHouse} className="p-1 text-ink-muted">
                          {row.destinations[String(destHouse)]?.dest_nature}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </>
      )}
    </div>
  );
}

/**
 * Learning / Cheat-Sheet tab -- the "fundamentals" reference Ajay asked for:
 * house ownerships, lagna functional benefics/malefics, house themes,
 * lord-placement connections, friends/enemies, exalted/debilitated.
 * All chart-INDEPENDENT -- this is the doctrine every chart gets read against.
 */
export function LearningTab() {
  const [subTab, setSubTab] = useState<SubTab>("house-themes");
  const activeSubTab = SUB_TABS.find((item) => item.id === subTab);

  return (
    <div className="space-y-5">
      <div className="border-b border-ink/10 pb-4">
        <div className="flex items-start gap-3">
          <div className="mt-0.5 rounded-lg bg-gold/15 p-2 text-gold"><BookOpen size={20} aria-hidden="true" /></div>
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.14em] text-gold">Reference library</p>
            <h2 className="mt-1 font-scripture text-2xl font-semibold text-indigo">Learn the rules behind the reading</h2>
            <p className="mt-1 max-w-2xl text-sm text-ink-muted">Use these doctrine views as a quick reference before you interpret a chart. Each panel keeps the source structure visible and scannable.</p>
          </div>
        </div>
      </div>
      <div className="rounded-xl border border-ink/10 bg-surface p-2 shadow-sm">
        <div className="flex gap-1 overflow-x-auto" role="tablist" aria-label="Learning reference sections">
        {SUB_TABS.map((t) => (
          <button
            key={t.id}
            onClick={() => setSubTab(t.id)}
            role="tab"
            aria-selected={subTab === t.id}
            className={`flex shrink-0 items-center gap-1.5 rounded-lg px-3 py-2 text-sm font-semibold transition-colors ${
              subTab === t.id ? "bg-indigo text-white shadow-sm" : "text-ink-muted hover:bg-bg hover:text-ink"
            }`}
          >
            {t.label}
            {subTab === t.id && <ArrowRight size={13} aria-hidden="true" />}
          </button>
        ))}
        </div>
      </div>
      <div className="flex items-center justify-between gap-3">
        <div>
          <h3 className="font-scripture text-xl font-semibold text-indigo">{activeSubTab?.label}</h3>
          <p className="text-xs text-ink-muted">Chart-independent reference material</p>
        </div>
        <span className="hidden rounded-full bg-bg px-3 py-1 text-xs font-medium text-ink-muted sm:block">{SUB_TABS.findIndex((item) => item.id === subTab) + 1} / {SUB_TABS.length}</span>
      </div>

      {subTab === "house-themes" && <HouseThemesPanel />}
      {subTab === "functional-nature" && <FunctionalNatureGridPanel />}
      {subTab === "relationship-graph" && <PlanetRelationshipGraphPanel />}
      {subTab === "relationships" && <RelationshipsPanel />}
      {subTab === "dignity" && <DignityPanel />}
      {subTab === "lord-placement" && <LordPlacementPanel />}
      {subTab === "dasha" && <DashaReferencePanel />}
      {subTab === "transits" && <TransitReferencePanel />}
      {subTab === "top-rules" && <TopRulesPanel />}
      {subTab === "concept-library" && <ConceptLibraryPanel />}
    </div>
  );
}
