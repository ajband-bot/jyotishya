import { useMemo, useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { RotateCcw, Sun, Moon as MoonIcon } from "lucide-react";
import { api, type SandboxAnalysis, type SandboxPlanetPlacement } from "../../lib/api";
import {
  PLACEABLE_PLANETS,
  PLANET_COLOR,
  SIGN_GRID_POSITION,
  SIGN_LORDS,
  SIGN_NAMES,
  SPECIAL_ASPECT_OFFSETS,
  UNIVERSAL_ASPECT_OFFSET,
  cellCenter,
  houseForSign,
  ketuSignFor,
  signForHouseOffset,
  type AspectMode,
} from "./layout";
import { ObservationsPanel } from "./ObservationsPanel";
import { FocusPanel } from "./FocusPanel";
import { TimeController } from "./TimeController";
import { DashaModule, type ActiveDasha } from "./DashaModule";
import { ActivationPanel } from "./ActivationPanel";
import { TransitPanel } from "./TransitPanel";
import { TransitOverlay } from "./TransitOverlay";
import { FlaskConical } from "lucide-react";

type Placements = Record<string, SandboxPlanetPlacement>;

const DEFAULT_LAGNA = 1;
const DEFAULT_PLACEMENTS: Placements = {
  Sun: { sign: 1, degree: 15, retrograde: false },
  Moon: { sign: 4, degree: 15, retrograde: false },
  Mars: { sign: 1, degree: 15, retrograde: false },
  Mercury: { sign: 1, degree: 15, retrograde: false },
  Jupiter: { sign: 9, degree: 15, retrograde: false },
  Venus: { sign: 2, degree: 15, retrograde: false },
  Saturn: { sign: 10, degree: 15, retrograde: false },
  Rahu: { sign: 6, degree: 15, retrograde: false },
};

function GridCell({
  sign,
  house,
  isLagna,
  occupants,
  onDrop,
  onDragOver,
  onSelectPlanet,
  onSelectHouse,
  selectedPlanet,
  dashaRole,
  selectedHouse,
  contactedByTransit,
}: {
  sign: number;
  house: number;
  isLagna: boolean;
  occupants: string[];
  onDrop: (sign: number, item: string) => void;
  onDragOver: (e: React.DragEvent) => void;
  onSelectPlanet: (planet: string) => void;
  onSelectHouse: (house: number) => void;
  selectedPlanet: string | null;
  dashaRole: (planet: string) => "md" | "ad" | "pd" | null;
  selectedHouse: number | null;
  contactedByTransit: Set<string> | null;
}) {
  const dim = (planet: string) => {
    if (selectedPlanet) return selectedPlanet === planet ? 1 : 0.4;
    if (contactedByTransit && contactedByTransit.size > 0) return contactedByTransit.has(planet) ? 1 : 0.4;
    return 1;
  };
  const [row, col] = SIGN_GRID_POSITION[sign];
  return (
    <div
      style={{ gridRow: row + 1, gridColumn: col + 1 }}
      onDragOver={onDragOver}
      onDrop={(e) => {
        e.preventDefault();
        const item = e.dataTransfer.getData("text/plain");
        if (item) onDrop(sign, item);
      }}
      onClick={() => onSelectHouse(house)}
      role="button"
      tabIndex={0}
      aria-label={`Focus house ${house}, ${SIGN_NAMES[sign - 1]}`}
      onKeyDown={(e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          onSelectHouse(house);
        }
      }}
      className={`relative flex flex-col items-center justify-start border p-1 min-h-[92px] ${
        selectedHouse === house
          ? "bg-gold/10 border-gold ring-2 ring-inset ring-gold/60"
          : isLagna ? "bg-indigo/10 border-indigo/40" : "border-ink/15 bg-surface"
      }`}
    >
      <span className={`absolute top-1 left-1 h-5 min-w-5 rounded-full px-1 text-[10px] font-bold flex items-center justify-center ${selectedHouse === house ? "bg-gold text-white" : "bg-ink/10"}`}>
        {house}
      </span>
      <div className="text-[10px] text-ink-muted leading-none mt-0.5">
        {SIGN_NAMES[sign - 1]}
      </div>
      <div className="text-[9px] text-ink-muted/70 leading-none">{SIGN_LORDS[sign - 1]}</div>
      {isLagna && (
        <span className="absolute top-1 right-1 text-[9px] font-bold text-indigo">Lg</span>
      )}
      <div className="flex flex-wrap gap-1 mt-1 justify-center">
        {occupants.map((planet) => {
          const role = dashaRole(planet);
          return (
            <button
              key={planet}
              draggable={planet !== "Ketu"}
              onDragStart={(e) => e.dataTransfer.setData("text/plain", planet)}
              onClick={(e) => {
                e.stopPropagation();
                onSelectPlanet(planet);
              }}
              title={planet === "Ketu" ? "Ketu (always 180 deg from Rahu, not draggable)" : planet}
              className={`chartlab-planet-chip rounded-full h-6 w-6 text-[10px] font-bold text-white flex items-center justify-center ${
                planet !== "Ketu" ? "cursor-grab" : "cursor-default"
              } ${role === "md" ? "chartlab-dasha-md" : ""} ${role === "ad" ? "chartlab-dasha-ad" : ""} ${
                role === "pd" ? "chartlab-dasha-pd" : ""
              }`}
              style={{
                background: PLANET_COLOR[planet],
                outline: selectedPlanet === planet ? "2px solid #111827" : "none",
                opacity: dim(planet),
                ...(role ? ({ "--dasha-glow-color": PLANET_COLOR[planet] } as React.CSSProperties) : {}),
              }}
            >
              {planet.slice(0, 2)}
            </button>
          );
        })}
      </div>
    </div>
  );
}

interface AspectLine {
  planet: string;
  fromSign: number;
  toSign: number;
  special: boolean;
  offset: number;
  variant?: "natal" | "transit";
}

function AspectOverlay({ lines, animate }: { lines: AspectLine[]; animate: boolean }) {
  return (
    <svg
      className="absolute inset-0 pointer-events-none"
      viewBox="0 0 100 100"
      preserveAspectRatio="none"
    >
      <defs>
        <marker id="chartlab-arrow" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto">
          <path d="M0,0 L6,3 L0,6 Z" fill="currentColor" />
        </marker>
      </defs>
      {lines.map((line, i) => {
        const from = cellCenter(line.fromSign);
        const to = cellCenter(line.toSign);
        const midX = from.x + (to.x - from.x) * 0.6;
        const midY = from.y + (to.y - from.y) * 0.6;
        const isTransit = line.variant === "transit";
        return (
          <g key={i} style={{ color: PLANET_COLOR[line.planet] }}>
            <line
              x1={from.x}
              y1={from.y}
              x2={to.x}
              y2={to.y}
              stroke={PLANET_COLOR[line.planet]}
              strokeWidth={isTransit ? 0.45 : line.special ? 0.6 : 0.35}
              strokeDasharray={isTransit ? "0.6,1.2" : line.special ? "2,2" : "1.5,1.5"}
              opacity={line.special || isTransit ? 0.9 : 0.55}
              markerEnd="url(#chartlab-arrow)"
              className={animate ? "chartlab-aspect-animated" : undefined}
            >
              <title>
                {isTransit ? "Transit " : ""}
                {line.planet} {line.offset}
                {line.offset === 2 || line.offset === 3 ? "rd" : line.offset === 1 ? "st" : "th"} aspect
              </title>
            </line>
            {animate && (
              <text x={midX} y={midY} fontSize="3" fill={PLANET_COLOR[line.planet]} textAnchor="middle">
                {line.offset}
              </text>
            )}
          </g>
        );
      })}
    </svg>
  );
}

/**
 * Chart Lab -- drag-and-drop D1 sandbox. South Indian layout: signs are
 * FIXED to grid cells (their lordship never changes); the user drags the
 * Lagna marker onto a sign to set the reference point, then drags all 9
 * planets onto sign boxes. House numbers, functional nature, dignity,
 * doshas, yogas, and Shadbala all recompute live from the same engine
 * real charts use (app/derived/sandbox.py).
 */
export function ChartLabTab() {
  const [lagnaSign, setLagnaSign] = useState(DEFAULT_LAGNA);
  const [placements, setPlacements] = useState<Placements>(DEFAULT_PLACEMENTS);
  const [dayOrNight, setDayOrNight] = useState<"day" | "night">("day");
  const [selectedPlanet, setSelectedPlanet] = useState<string | null>(null);
  const [selectedHouse, setSelectedHouse] = useState<number | null>(null);
  const [result, setResult] = useState<SandboxAnalysis | null>(null);
  const [aspectMode, setAspectMode] = useState<AspectMode>("selected");
  const [selectedDate, setSelectedDate] = useState(() => new Date().toISOString().slice(0, 10));
  const [activeDasha, setActiveDasha] = useState<ActiveDasha>({ md: null, ad: null, pd: null });
  const [transitEnabled, setTransitEnabled] = useState(false);
  const [focusedTransit, setFocusedTransit] = useState<string | null>(null);

  const moonSign = placements.Moon?.sign ?? DEFAULT_PLACEMENTS.Moon.sign;
  const moonDegree = placements.Moon?.degree ?? DEFAULT_PLACEMENTS.Moon.degree;

  const natalPointers = useMemo(() => {
    const pointers: Record<string, { sign: number; degree: number }> = {};
    for (const planet of PLACEABLE_PLANETS) {
      if (placements[planet]) pointers[planet] = { sign: placements[planet].sign, degree: placements[planet].degree };
    }
    if (placements.Rahu) {
      pointers.Ketu = { sign: ketuSignFor(placements.Rahu.sign), degree: placements.Rahu.degree };
    }
    return pointers;
  }, [placements]);

  const transitsQuery = useQuery({
    queryKey: ["sandbox-transits", selectedDate, lagnaSign, moonSign, natalPointers],
    queryFn: () =>
      api.getSandboxTransits({
        on_date: selectedDate,
        lagna_sign: lagnaSign,
        moon_sign: moonSign,
        natal_planets: natalPointers,
      }),
    enabled: transitEnabled,
  });

  // Sprint 4: aspect lines cast BY the focused transit planet onto the
  // natal wheel -- drawn with a finer dotted stroke so they're never
  // confused with natal-to-natal aspects (spec section 7 & 12).
  const transitAspectLines = useMemo<AspectLine[]>(() => {
    if (!focusedTransit || !transitsQuery.data) return [];
    const pos = transitsQuery.data.planets[focusedTransit];
    if (!pos) return [];
    return pos.aspects_houses.map((house) => ({
      planet: focusedTransit,
      fromSign: pos.sign,
      toSign: signForHouseOffset(lagnaSign, house),
      special: true,
      offset: house,
      variant: "transit" as const,
    }));
  }, [focusedTransit, transitsQuery.data, lagnaSign]);

  const contactedByTransit = useMemo(() => {
    if (!focusedTransit || !transitsQuery.data) return null;
    const pos = transitsQuery.data.planets[focusedTransit];
    if (!pos) return null;
    return new Set(pos.natal_contacts.map((c) => c.natal_planet));
  }, [focusedTransit, transitsQuery.data]);

  function dashaRole(planet: string): "md" | "ad" | "pd" | null {
    if (activeDasha.pd === planet) return "pd";
    if (activeDasha.ad === planet) return "ad";
    if (activeDasha.md === planet) return "md";
    return null;
  }

  const mutation = useMutation({
    mutationFn: () =>
      api.analyzeSandbox({
        lagna_sign: lagnaSign,
        lagna_degree: 15,
        planets: placements,
        day_or_night: dayOrNight,
      }),
    onSuccess: (data) => setResult(data),
  });

  const occupantsBySign = useMemo(() => {
    const map: Record<number, string[]> = {};
    for (const planet of PLACEABLE_PLANETS) {
      const p = placements[planet];
      if (!p) continue;
      map[p.sign] = [...(map[p.sign] ?? []), planet];
    }
    if (placements.Rahu) {
      const ketuSign = ketuSignFor(placements.Rahu.sign);
      map[ketuSign] = [...(map[ketuSign] ?? []), "Ketu"];
    }
    return map;
  }, [placements]);

  const aspectLines = useMemo<AspectLine[]>(() => {
    const lines: AspectLine[] = [];
    const allPlanetSigns: Record<string, number> = {};
    for (const planet of PLACEABLE_PLANETS) {
      if (placements[planet]) allPlanetSigns[planet] = placements[planet].sign;
    }
    if (placements.Rahu) allPlanetSigns.Ketu = ketuSignFor(placements.Rahu.sign);

    for (const [planet, fromSign] of Object.entries(allPlanetSigns)) {
      const toUniversal = signForHouseOffset(fromSign, UNIVERSAL_ASPECT_OFFSET);
      lines.push({ planet, fromSign, toSign: toUniversal, special: false, offset: UNIVERSAL_ASPECT_OFFSET });
      for (const offset of SPECIAL_ASPECT_OFFSETS[planet] ?? []) {
        lines.push({ planet, fromSign, toSign: signForHouseOffset(fromSign, offset), special: true, offset });
      }
    }
    return lines;
  }, [placements]);

  const visibleAspectLines = useMemo(() => {
    if (aspectMode === "off") return [];
    if (aspectMode === "all") return aspectLines;
    // "selected" -- only the focused planet's own aspects, per spec section
    // 13, to avoid a spaghetti diagram of every planet's lines at once.
    if (!selectedPlanet) return [];
    return aspectLines.filter((l) => l.planet === selectedPlanet);
  }, [aspectLines, aspectMode, selectedPlanet]);

  function handleDrop(sign: number, item: string) {
    if (item === "Lagna") {
      setLagnaSign(sign);
      return;
    }
    setPlacements((prev) => ({
      ...prev,
      [item]: { sign, degree: prev[item]?.degree ?? 15, retrograde: prev[item]?.retrograde ?? false },
    }));
  }

  function updateSelected(patch: Partial<SandboxPlanetPlacement>) {
    if (!selectedPlanet) return;
    setPlacements((prev) => ({ ...prev, [selectedPlanet]: { ...prev[selectedPlanet], ...patch } }));
  }

  function reset() {
    setLagnaSign(DEFAULT_LAGNA);
    setPlacements(DEFAULT_PLACEMENTS);
    setResult(null);
    setSelectedPlanet(null);
    setSelectedHouse(null);
  }

  const allPlaced = PLACEABLE_PLANETS.every((p) => placements[p]);
  const selected = selectedPlanet ? placements[selectedPlanet] : null;
  const selectedHouseData = selectedHouse && result ? result.houses[String(selectedHouse)] : null;
  const selectedHouseConnection = selectedHouse && result ? result.house_connections[String(selectedHouse)] : null;
  const selectedHouseTransits = selectedHouse && transitsQuery.data
    ? Object.entries(transitsQuery.data.planets).filter(([, transit]) =>
        transit.house_from_lagna === selectedHouse || transit.aspects_houses.includes(selectedHouse),
      )
    : [];

  return (
    <div className="space-y-5">
      <div className="flex items-start gap-3 border-b border-ink/10 pb-4">
        <div className="mt-0.5 rounded-lg bg-indigo/10 p-2 text-indigo"><FlaskConical size={20} aria-hidden="true" /></div>
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.14em] text-indigo">Interactive sandbox</p>
          <h2 className="mt-1 font-scripture text-2xl font-semibold text-indigo">Chart Lab</h2>
          <p className="mt-1 max-w-2xl text-sm text-ink-muted">Build a D1 chart, focus a planet, and inspect how house lordship and timing signals respond. Your placements stay local until you run analysis.</p>
        </div>
      </div>
      <TimeController selectedDate={selectedDate} onChange={setSelectedDate} />
      <div className="grid gap-4 lg:grid-cols-[420px_1fr]">
      <div className="space-y-4">
        <section className="rounded-xl border border-ink/10 bg-surface p-3 shadow-sm" aria-labelledby="chart-builder-heading">
          <div className="mb-3 flex items-start justify-between gap-3">
            <div>
              <p className="text-[11px] font-semibold uppercase tracking-[0.12em] text-indigo">Step 1</p>
              <h3 id="chart-builder-heading" className="font-scripture text-lg font-semibold text-indigo">Place planets</h3>
              <p className="text-[11px] text-ink-muted">Drag a marker onto a sign. Click a marker on the wheel to inspect it.</p>
            </div>
            <button onClick={reset} className="flex shrink-0 items-center gap-1 rounded-md px-2 py-1 text-xs text-ink-muted hover:bg-bg hover:text-ink">
              <RotateCcw size={12} aria-hidden="true" /> Reset
            </button>
          </div>
          <div className="flex flex-wrap gap-2">
            <button
              draggable
              onDragStart={(e) => e.dataTransfer.setData("text/plain", "Lagna")}
              className="cursor-grab rounded-md bg-indigo px-3 py-1.5 text-xs font-semibold text-white"
            >
              Lagna marker
            </button>
            {PLACEABLE_PLANETS.map((planet) => (
              <button
                key={planet}
                draggable
                onDragStart={(e) => e.dataTransfer.setData("text/plain", planet)}
                className="cursor-grab rounded-md px-3 py-1.5 text-xs font-semibold text-white"
                style={{ background: PLANET_COLOR[planet] }}
              >
                {planet}
              </button>
            ))}
          </div>
        </section>

        <section aria-labelledby="chart-display-heading">
          <div className="mb-2 flex items-center justify-between gap-3">
            <div>
              <p className="text-[11px] font-semibold uppercase tracking-[0.12em] text-ink-muted">Step 2</p>
              <h3 id="chart-display-heading" className="font-scripture text-lg font-semibold text-indigo">Chart display</h3>
            </div>
            <div className="flex items-center gap-2 text-[10px] text-ink-muted" aria-label="Chart marker legend">
              <span className="inline-block h-3 w-3 rounded-full bg-indigo" aria-hidden="true" /> Natal
              <span className="inline-block h-3 w-3 rounded-full border-2 border-indigo bg-surface" aria-hidden="true" /> Transit
            </div>
          </div>
          <div className="mb-2 flex items-center gap-2 rounded-lg border border-ink/10 bg-surface p-2">
          <span className="shrink-0 text-xs font-medium text-ink-muted">Aspects</span>
          {(["off", "selected", "all"] as AspectMode[]).map((m) => (
            <button
              key={m}
              onClick={() => setAspectMode(m)}
              aria-pressed={aspectMode === m}
              className={`rounded-md px-2 py-1 text-[11px] capitalize ${
                aspectMode === m ? "bg-indigo text-white" : "bg-ink/5 text-ink-muted"
              }`}
            >
              {m === "off" ? "Off" : m === "selected" ? "Selected Planet" : "All Natal"}
            </button>
          ))}
          </div>
          <div className="flex flex-wrap gap-x-3 gap-y-1">
            {aspectMode === "selected" && !selectedPlanet && (
              <span className="text-[10px] text-amber">Click a planet to see its aspects</span>
            )}
            {aspectMode !== "off" && (
              <span className="text-[10px] text-ink-muted">
                solid + thick = special aspect, dashed = universal 7th-house aspect
              </span>
            )}
          </div>
        </section>

        <div
          className="relative grid gap-0.5 bg-ink/10 p-0.5 rounded-lg border border-ink/20"
          style={{ gridTemplateColumns: "repeat(4, 1fr)", gridTemplateRows: "repeat(4, 1fr)" }}
        >
          {Array.from({ length: 12 }, (_, i) => i + 1).map((sign) => (
            <GridCell
              key={sign}
              sign={sign}
              house={houseForSign(lagnaSign, sign)}
              isLagna={sign === lagnaSign}
              occupants={occupantsBySign[sign] ?? []}
              onDragOver={(e) => e.preventDefault()}
              onDrop={handleDrop}
              onSelectPlanet={setSelectedPlanet}
              onSelectHouse={setSelectedHouse}
              selectedPlanet={selectedPlanet}
              dashaRole={dashaRole}
              selectedHouse={selectedHouse}
              contactedByTransit={contactedByTransit}
            />
          ))}
          <div
            style={{ gridRow: "2 / span 2", gridColumn: "2 / span 2" }}
            className="flex items-center justify-center text-xs text-ink-muted bg-bg"
          >
            D1 -- Chart Lab
          </div>
          {(aspectMode !== "off" || transitAspectLines.length > 0) && (
            <AspectOverlay
              lines={[...visibleAspectLines, ...transitAspectLines]}
              animate={(aspectMode === "selected" && !!selectedPlanet) || transitAspectLines.length > 0}
            />
          )}
          {transitEnabled && transitsQuery.data && (
            <TransitOverlay transits={transitsQuery.data.planets} focusedPlanet={focusedTransit} onSelect={setFocusedTransit} />
          )}
        </div>

        {selectedPlanet && selected && (
          <FocusPanel planet={selectedPlanet} placement={selected} result={result} onUpdate={updateSelected} />
        )}

        <div className="mt-4 flex items-center gap-3 rounded-lg border border-ink/10 bg-surface p-2">
          <span className="text-xs font-medium text-ink-muted">Day / night proxy</span>
          <button
            onClick={() => setDayOrNight("day")}
            aria-pressed={dayOrNight === "day"}
            className={`flex items-center gap-1 text-xs px-2 py-1 rounded-md ${dayOrNight === "day" ? "bg-amber text-white" : "bg-ink/5"}`}
          >
            <Sun size={12} /> Day
          </button>
          <button
            onClick={() => setDayOrNight("night")}
            aria-pressed={dayOrNight === "night"}
            className={`flex items-center gap-1 text-xs px-2 py-1 rounded-md ${dayOrNight === "night" ? "bg-indigo text-white" : "bg-ink/5"}`}
          >
            <MoonIcon size={12} /> Night
          </button>
        </div>

        {mutation.isError && (
          <div className="mt-3 rounded-md border border-red-muted/40 bg-red-muted/10 p-2 text-xs text-red-muted flex items-start justify-between gap-2">
            <span>
              Analysis failed: {mutation.error instanceof Error ? mutation.error.message : "unknown error"}.
              Is the backend running?
            </span>
            <button onClick={() => mutation.mutate()} className="underline shrink-0">
              Retry
            </button>
          </div>
        )}

        <button
          onClick={() => mutation.mutate()}
          disabled={!allPlaced || mutation.isPending}
          className="mt-4 w-full rounded-lg bg-indigo py-2.5 font-semibold text-white shadow-sm transition-colors hover:bg-indigo/90 disabled:cursor-not-allowed disabled:opacity-40"
        >
          {mutation.isPending ? "Analyzing..." : "Analyze Chart"}
        </button>
        {!allPlaced && (
          <p className="text-[11px] text-amber mt-2">
            Place all 8 planets on the wheel to run the analysis (Ketu is auto-derived, always opposite Rahu).
          </p>
        )}
      </div>

      <div className="space-y-4">
        <section aria-labelledby="timing-heading" className="space-y-3">
          <div>
            <p className="text-[11px] font-semibold uppercase tracking-[0.12em] text-indigo">Step 3</p>
            <h3 id="timing-heading" className="font-scripture text-lg font-semibold text-indigo">Timing signals</h3>
          </div>
          <DashaModule moonSign={moonSign} moonDegree={moonDegree} selectedDate={selectedDate} onActiveChange={setActiveDasha} />
          <TransitPanel
            enabled={transitEnabled}
            onToggle={setTransitEnabled}
            isFetching={transitsQuery.isFetching}
            transits={transitsQuery.data?.planets ?? null}
            focusedPlanet={focusedTransit}
            onFocusChange={setFocusedTransit}
            active={activeDasha}
          />
        </section>
        {result && (
          <section aria-labelledby="evidence-heading" className="space-y-3">
            <div>
              <p className="text-[11px] font-semibold uppercase tracking-[0.12em] text-gold">Step 4</p>
              <h3 id="evidence-heading" className="font-scripture text-lg font-semibold text-indigo">Computed evidence</h3>
            </div>
            <ActivationPanel active={activeDasha} result={result} transits={transitEnabled ? transitsQuery.data?.planets ?? null : null} />
            {selectedHouse && selectedHouseData && (
              <div className="rounded-xl border border-gold/30 bg-gold/5 p-3 text-xs shadow-sm">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <p className="text-[10px] font-semibold uppercase tracking-[0.12em] text-gold">Selected house</p>
                    <h4 className="font-scripture text-lg font-semibold text-indigo">H{selectedHouse} · {selectedHouseData.theme.core}</h4>
                  </div>
                  <span className="rounded-full bg-gold px-2 py-1 text-[10px] font-bold text-white">Wheel focus</span>
                </div>
                <div className="mt-2 grid gap-2 sm:grid-cols-2">
                  <p><span className="text-ink-muted">Lord:</span> <b>{selectedHouseData.lord}</b></p>
                  <p><span className="text-ink-muted">Occupants:</span> <b>{selectedHouseData.occupants.join(", ") || "None"}</b></p>
                  <p><span className="text-ink-muted">Aspected by:</span> <b>{selectedHouseData.aspected_by.join(", ") || "None"}</b></p>
                  {selectedHouseConnection && <p><span className="text-ink-muted">Connection:</span> <b>H{selectedHouseConnection.lord_house}</b> · {selectedHouseConnection.connection}</p>}
                </div>
                {selectedHouseTransits.length > 0 && (
                  <div className="mt-2 border-t border-gold/20 pt-2">
                    <p className="font-semibold text-gold">Transit signals touching H{selectedHouse}</p>
                    <p className="mt-1 text-ink-muted">{selectedHouseTransits.map(([planet, transit]) => `${planet} ${transit.house_from_lagna === selectedHouse ? "occupies" : "aspects"} H${selectedHouse}`).join(" · ")}</p>
                  </div>
                )}
              </div>
            )}
          </section>
        )}
        {result ? (
          <section aria-labelledby="interpretation-heading" className="space-y-3">
            <div>
              <p className="text-[11px] font-semibold uppercase tracking-[0.12em] text-ink-muted">Step 5</p>
              <h3 id="interpretation-heading" className="font-scripture text-lg font-semibold text-indigo">Interpretation map</h3>
              <p className="text-xs text-ink-muted">Switch between planets, houses, yogas, and doshas to inspect the computed result.</p>
            </div>
            <ObservationsPanel
              result={result}
              onSelectPlanet={setSelectedPlanet}
              onSelectHouse={setSelectedHouse}
              selectedHouse={selectedHouse}
            />
          </section>
        ) : (
          <p className="text-ink-muted text-sm">
            Build a chart on the left, then click "Analyze Chart" to see house lordships, functional
            nature, dignity, doshas, yogas, aspects, and simplified Shadbala -- computed live by the
            same engine real charts use.
          </p>
        )}
      </div>
      </div>
    </div>
  );
}
