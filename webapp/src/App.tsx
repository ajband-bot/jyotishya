import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { api } from "./lib/api";
import { ValidationScreen } from "./screens/ValidationScreen";
import { LearningTab } from "./screens/LearningTab";
import { PlanetLab } from "./screens/PlanetLab";
import { CheatsheetConsole } from "./screens/CheatsheetConsole";
import { ChartLabTab } from "./screens/chartlab/ChartLabTab";
import { CaseLookup } from "./screens/CaseLookup";
import { ChartCreate } from "./screens/ChartCreate";
import { TodayPanchanga } from "./screens/TodayPanchanga";
import { TodayTransits } from "./screens/TodayTransits";
import { ChartWorkbench } from "./screens/workbench/ChartWorkbench";
import { RuleBrowser } from "./screens/RuleBrowser";
import { DbBrowser } from "./screens/DbBrowser";
import { ApiConsole } from "./screens/ApiConsole";
import { MarriageCompatibility } from "./screens/MarriageCompatibility";
import {
  BookOpen, CheckCircle2, FlaskConical, LayoutDashboard, ShieldCheck, Sparkles, Database,
  PlusCircle, FileCode2, Terminal, Sun, Orbit, Heart,
} from "lucide-react";

type Tab =
  | "learning" | "cheatsheet" | "chart-lab"
  | "today-panchanga" | "today-transits"
  | "new-chart" | "workbench" | "validation" | "planet-lab" | "case-lookup" | "marriage-compatibility"
  | "api-console" | "rule-browser" | "db-browser";

const CHART_AGNOSTIC_TABS: Tab[] = [
  "learning", "cheatsheet", "chart-lab", "today-panchanga", "today-transits",
  "new-chart", "case-lookup", "marriage-compatibility", "api-console", "rule-browser", "db-browser",
];

interface TabDef {
  id: Tab;
  label: string;
  icon: React.ReactNode;
  needsChart?: boolean;
}

interface TabGroup {
  label: string;
  tabs: TabDef[];
}

const TAB_GROUPS: TabGroup[] = [
  {
    label: "Today",
    tabs: [
      { id: "today-panchanga", label: "Panchanga (Today)", icon: <Sun size={16} /> },
      { id: "today-transits", label: "Transits (Today)", icon: <Orbit size={16} /> },
    ],
  },
  {
    label: "Learn",
    tabs: [
      { id: "learning", label: "Learning / Cheat-Sheet", icon: <BookOpen size={16} /> },
      { id: "cheatsheet", label: "Cheat-Sheet Console", icon: <CheckCircle2 size={16} /> },
      { id: "chart-lab", label: "Chart Lab", icon: <FlaskConical size={16} /> },
    ],
  },
  {
    label: "Chart workflow",
    tabs: [
      { id: "new-chart", label: "New Horoscope", icon: <PlusCircle size={16} /> },
      { id: "workbench", label: "Chart Workbench", icon: <LayoutDashboard size={16} />, needsChart: true },
      { id: "validation", label: "Validate", icon: <ShieldCheck size={16} />, needsChart: true },
      { id: "planet-lab", label: "Planet Lab", icon: <Sparkles size={16} />, needsChart: true },
      { id: "case-lookup", label: "Case Lookup (DB)", icon: <Database size={16} /> },
      { id: "marriage-compatibility", label: "Marriage Compatibility", icon: <Heart size={16} /> },
    ],
  },
  {
    label: "Dev tools",
    tabs: [
      { id: "api-console", label: "API Console", icon: <Terminal size={16} /> },
      { id: "rule-browser", label: "Rule Browser", icon: <FileCode2 size={16} /> },
      { id: "db-browser", label: "DB Browser", icon: <Database size={16} /> },
    ],
  },
];

function App() {
  const [selectedChart, setSelectedChart] = useState<string | null>(null);
  const [tab, setTab] = useState<Tab>("learning");

  const chartsQuery = useQuery({ queryKey: ["charts"], queryFn: api.listCharts });
  const validationQuery = useQuery({
    queryKey: ["validation", selectedChart],
    queryFn: () => api.getValidationScreen(selectedChart!),
    enabled: !!selectedChart && tab === "validation",
  });
  const coverageQuery = useQuery({
    queryKey: ["coverage", selectedChart],
    queryFn: () => api.getCoverage(selectedChart!),
    enabled: !!selectedChart && tab === "validation",
  });
  const doshasQuery = useQuery({
    queryKey: ["doshas", selectedChart],
    queryFn: () => api.getDoshas(selectedChart!),
    enabled: !!selectedChart && tab === "validation",
  });

  return (
    <div className="min-h-screen bg-bg text-ink">
      <header className="border-b border-ink/10 bg-surface px-4 py-5 sm:px-6">
        <div className="mx-auto flex max-w-7xl items-start justify-between gap-4">
          <div>
            <p className="mb-1 flex items-center gap-2 text-[11px] font-semibold uppercase tracking-[0.16em] text-gold">
              <Sparkles size={13} aria-hidden="true" /> Pramana workspace
            </p>
            <h1 className="text-2xl font-semibold font-scripture text-indigo sm:text-3xl">
              Jyotisha Workbench
            </h1>
            <p className="mt-1 text-sm text-ink-muted">
              Learn the doctrine, generate and test a chart, and keep every conclusion auditable.
            </p>
          </div>
          <div className="hidden items-center gap-2 rounded-full border border-sage/25 bg-sage/5 px-3 py-1.5 text-xs font-medium text-sage sm:flex">
            <CheckCircle2 size={14} aria-hidden="true" /> Evidence-first mode
          </div>
        </div>
      </header>

      <main className={`mx-auto px-4 py-5 sm:px-6 sm:py-7 ${tab === "chart-lab" || tab === "workbench" || tab === "api-console" || tab === "rule-browser" ? "max-w-7xl" : "max-w-6xl"}`}>
        <div className="mb-6 space-y-3 rounded-xl border border-ink/10 bg-surface p-3 shadow-sm">
          <div className="flex items-center justify-between px-1">
            <p className="text-xs font-semibold uppercase tracking-[0.12em] text-ink-muted">Workspace views</p>
            <p className="hidden text-xs text-ink-muted sm:block">
              {selectedChart ? `Chart loaded: ${selectedChart}` : "Chart-independent tools ready"}
            </p>
          </div>

          {TAB_GROUPS.map((group) => (
            <div key={group.label} className="flex flex-wrap items-center gap-1.5">
              <span className="mr-1 shrink-0 text-[10px] font-semibold uppercase tracking-wide text-ink-muted/70 w-24">
                {group.label}
              </span>
              {group.tabs.map((t) => (
                <button
                  key={t.id}
                  role="tab"
                  aria-selected={tab === t.id}
                  className={`flex shrink-0 items-center gap-1.5 rounded-lg px-3 py-2 text-xs font-semibold transition-colors ${
                    tab === t.id ? "bg-indigo text-white shadow-sm" : "text-ink-muted hover:bg-bg hover:text-ink"
                  } ${t.needsChart && !selectedChart ? "opacity-40" : ""}`}
                  onClick={() => setTab(t.id)}
                  disabled={t.needsChart && !selectedChart}
                >
                  {t.icon}
                  {t.label}
                </button>
              ))}
            </div>
          ))}

          {!CHART_AGNOSTIC_TABS.includes(tab) && (
            <select
              className="rounded-md border border-ink/20 bg-surface px-3 py-2 text-sm"
              value={selectedChart ?? ""}
              onChange={(e) => setSelectedChart(e.target.value || null)}
            >
              <option value="">Select a chart...</option>
              {chartsQuery.data?.charts.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name} ({c.id})
                </option>
              ))}
            </select>
          )}
        </div>

        {tab === "learning" && <LearningTab />}
        {tab === "cheatsheet" && <CheatsheetConsole />}
        {tab === "chart-lab" && <ChartLabTab />}
        {tab === "today-panchanga" && <TodayPanchanga />}
        {tab === "today-transits" && <TodayTransits />}
        {tab === "new-chart" && (
          <ChartCreate
            onCreated={(chartId) => {
              setSelectedChart(chartId);
              setTab("validation");
            }}
          />
        )}
        {tab === "api-console" && <ApiConsole />}
        {tab === "rule-browser" && <RuleBrowser />}
        {tab === "db-browser" && <DbBrowser />}
        {tab === "case-lookup" && (
          <CaseLookup
            onSelect={(chartId) => {
              setSelectedChart(chartId);
              setTab("workbench");
            }}
          />
        )}
        {tab === "marriage-compatibility" && <MarriageCompatibility />}

        {["workbench", "validation", "planet-lab"].includes(tab) && !selectedChart && (
          <p className="text-ink-muted">
            Pick a chart above (or create one under New Horoscope, or pick a case under Case Lookup) to
            see its Chart Integrity screen (spec 15) before any interpretation is shown -- this gate
            cannot be skipped.
          </p>
        )}

        {tab === "validation" && selectedChart && validationQuery.data && (
          <ValidationScreen data={validationQuery.data} coverage={coverageQuery.data} doshas={doshasQuery.data} />
        )}

        {tab === "workbench" && selectedChart && <ChartWorkbench chartId={selectedChart} />}

        {tab === "planet-lab" && selectedChart && <PlanetLab chartId={selectedChart} />}
      </main>
    </div>
  );
}

export default App;
