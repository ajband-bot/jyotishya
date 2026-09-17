import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  LayoutDashboard, Clock, Compass, Grid3x3, AlertTriangle, Sparkles, BarChart3,
  Sun, Orbit, Database,
} from "lucide-react";
import { api } from "../../lib/api";
import { ChartDashboard } from "../ChartDashboard";
import { VimsottariPanel } from "./VimsottariPanel";
import { AshtakavargaPanel } from "./AshtakavargaPanel";
import { AspectsPanel } from "./AspectsPanel";
import { DoshaYogaPanel } from "./DoshaYogaPanel";
import { EvidenceSectionsPanel } from "./EvidenceSectionsPanel";
import { PanchangaPanel } from "./PanchangaPanel";
import { TransitsPanel } from "./TransitsPanel";
import { CaseFactsPanel } from "./CaseFactsPanel";

type Section =
  | "overview" | "vimsottari" | "aspects" | "ashtakavarga" | "doshas-yogas"
  | "panchanga" | "transits" | "strength" | "domains" | "case-facts";

const SECTIONS: Array<{ id: Section; label: string; icon: React.ReactNode }> = [
  { id: "overview", label: "Overview & Vargas", icon: <LayoutDashboard size={14} /> },
  { id: "vimsottari", label: "Vimsottari Dasha", icon: <Clock size={14} /> },
  { id: "aspects", label: "Aspects", icon: <Compass size={14} /> },
  { id: "ashtakavarga", label: "Ashtakavarga", icon: <Grid3x3 size={14} /> },
  { id: "doshas-yogas", label: "Doshas & Yogas", icon: <AlertTriangle size={14} /> },
  { id: "panchanga", label: "Panchanga", icon: <Sun size={14} /> },
  { id: "transits", label: "Transits (Gochara)", icon: <Orbit size={14} /> },
  { id: "strength", label: "Strength & Timing", icon: <BarChart3 size={14} /> },
  { id: "domains", label: "Marriage / Career / Remedies", icon: <Sparkles size={14} /> },
  { id: "case-facts", label: "Case Facts (DB)", icon: <Database size={14} /> },
];

const STRENGTH_SECTIONS = [
  { key: "shadbala_classical", title: "Shadbala (classical)", subtitle: "app/derived/shadbala.py" },
  { key: "vimsopaka", title: "Vimsopaka Bala", subtitle: "app/derived/vimsopaka.py" },
  { key: "bhava_bala", title: "Bhava Bala", subtitle: "app/derived/bhava_bala.py" },
  { key: "graha_maitri", title: "Graha Maitri", subtitle: "app/derived/dignities.py" },
  { key: "argala", title: "Argala", subtitle: "app/derived/interventions.py (BPHS Ch.31)" },
  { key: "nakshatra_analysis", title: "Nakshatra Analysis", subtitle: "app/derived/nakshatra_analysis.py" },
];

const DOMAIN_SECTIONS = [
  { key: "marriage_analysis", title: "Marriage (Five-Pillar Framework)", subtitle: "app/derived/marriage_analysis.py" },
  { key: "career_analysis", title: "Career", subtitle: "app/derived/career_analysis.py" },
  { key: "remedies", title: "Remedies", subtitle: "app/derived/remedies.py -- gemstone gate" },
  { key: "dasha_synthesis", title: "Dasha Synthesis", subtitle: "app/derived/dasha_synthesis.py" },
];

/**
 * Chart Workbench -- Phase 8's "tab-based view for each section of
 * analysis" ask, replacing the single-view Chart Dashboard with a proper
 * tabbed workbench over ONE full-context fetch. Every sub-tab is a pure
 * view over already-computed data -- no client-side astrology logic.
 * Panchanga and Transits (Gochara) are dedicated tabs (not folded into
 * the generic Strength & Timing grid) per explicit request.
 */
export function ChartWorkbench({ chartId }: { chartId: string }) {
  const [section, setSection] = useState<Section>("overview");

  const chartQuery = useQuery({ queryKey: ["chart", chartId], queryFn: () => api.getChart(chartId) });
  const fullContextQuery = useQuery({
    queryKey: ["full-context", chartId],
    queryFn: () => api.getFullContext(chartId),
  });

  if (chartQuery.isLoading || fullContextQuery.isLoading) {
    return <p className="text-ink-muted">Computing full chart + every derived layer...</p>;
  }
  if (!chartQuery.data || !fullContextQuery.data) return null;

  const chart = chartQuery.data;
  const fullContext = fullContextQuery.data;

  return (
    <div>
      <div className="mb-4 flex gap-1 overflow-x-auto rounded-lg border border-ink/10 bg-surface p-1.5" role="tablist" aria-label="Chart Workbench sections">
        {SECTIONS.map((s) => (
          <button
            key={s.id}
            role="tab"
            aria-selected={section === s.id}
            onClick={() => setSection(s.id)}
            className={`flex shrink-0 items-center gap-1.5 rounded-md px-3 py-2 text-xs font-semibold transition-colors ${
              section === s.id ? "bg-indigo text-white" : "text-ink-muted hover:bg-bg hover:text-ink"
            }`}
          >
            {s.icon}
            {s.label}
          </button>
        ))}
      </div>

      {section === "overview" && <ChartDashboard chart={chart} />}
      {section === "vimsottari" && <VimsottariPanel chart={chart} />}
      {section === "aspects" && <AspectsPanel fullContext={fullContext} />}
      {section === "ashtakavarga" && <AshtakavargaPanel fullContext={fullContext} />}
      {section === "doshas-yogas" && <DoshaYogaPanel fullContext={fullContext} />}
      {section === "panchanga" && <PanchangaPanel fullContext={fullContext} />}
      {section === "transits" && <TransitsPanel fullContext={fullContext} />}
      {section === "strength" && <EvidenceSectionsPanel fullContext={fullContext} sections={STRENGTH_SECTIONS} />}
      {section === "domains" && <EvidenceSectionsPanel fullContext={fullContext} sections={DOMAIN_SECTIONS} />}
      {section === "case-facts" && <CaseFactsPanel chartId={chartId} />}
    </div>
  );
}
