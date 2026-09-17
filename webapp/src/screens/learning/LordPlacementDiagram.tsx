import { useMemo, useState } from "react";
import type { LordPlacementConnections } from "../../lib/api";

const KEY_HOUSES = new Set([1, 4, 7, 9]);

const NATURE_STROKE: Record<string, string> = {
  trikona: "#16a34a",
  kendra: "#4f46e5",
  dusthana: "#dc2626",
  upachaya: "#ca8a04",
  neutral: "#9ca3af",
};

function housePosition(house: number, radius: number, center: number) {
  // House 1 at top, going clockwise -- matches how astrologers read a chart wheel.
  const angle = ((house - 1) / 12) * 2 * Math.PI - Math.PI / 2;
  return { x: center + radius * Math.cos(angle), y: center + radius * Math.sin(angle) };
}

/**
 * Full 12-house interactive Lord Placement Diagram -- click any house to
 * see where its lord could land and what thematic connection that
 * creates, across ALL 12 destinations (not just kendras). H1/H4/H7/H9 are
 * highlighted as the houses most decisive for Raja/Dhana Yoga formation.
 */
export function LordPlacementDiagram({ data }: { data: LordPlacementConnections }) {
  const [sourceHouse, setSourceHouse] = useState(1);
  const [hoverHouse, setHoverHouse] = useState<number | null>(null);

  const size = 460;
  const center = size / 2;
  const radius = 170;

  const positions = useMemo(() => {
    const out: Record<number, { x: number; y: number }> = {};
    for (let h = 1; h <= 12; h++) out[h] = housePosition(h, radius, center);
    return out;
  }, []);

  const row = data.matrix[String(sourceHouse)];
  const hoverConnection = hoverHouse ? row?.destinations[String(hoverHouse)] : null;

  return (
    <div className="grid gap-4 md:grid-cols-[460px_1fr]">
      <div className="rounded-lg border border-ink/10 bg-surface p-2 shadow-sm">
        <svg width={size} height={size}>
          {sourceHouse &&
            row &&
            Object.entries(row.destinations).map(([destStr, dest]) => {
              const destHouse = Number(destStr);
              if (destHouse === sourceHouse) return null;
              const from = positions[sourceHouse];
              const to = positions[destHouse];
              return (
                <line
                  key={destHouse}
                  x1={from.x}
                  y1={from.y}
                  x2={to.x}
                  y2={to.y}
                  stroke={NATURE_STROKE[dest.dest_nature] ?? "#9ca3af"}
                  strokeWidth={hoverHouse === destHouse ? 3 : 1}
                  strokeOpacity={hoverHouse === null || hoverHouse === destHouse ? 0.7 : 0.15}
                  onMouseEnter={() => setHoverHouse(destHouse)}
                  onMouseLeave={() => setHoverHouse(null)}
                  style={{ cursor: "pointer" }}
                />
              );
            })}
          {Array.from({ length: 12 }, (_, i) => i + 1).map((house) => {
            const pos = positions[house];
            const lord = data.matrix[String(house)]?.lord;
            const isKey = KEY_HOUSES.has(house);
            const isSource = house === sourceHouse;
            return (
              <g
                key={house}
                transform={`translate(${pos.x}, ${pos.y})`}
                onClick={() => setSourceHouse(house)}
                style={{ cursor: "pointer" }}
              >
                <circle
                  r={isKey ? 26 : 22}
                  fill={isSource ? "#4f46e5" : isKey ? "#fef3c7" : "#f3f4f6"}
                  stroke={isKey ? "#ca8a04" : "#d1d5db"}
                  strokeWidth={isSource ? 3 : isKey ? 2 : 1}
                />
                <text
                  textAnchor="middle"
                  dy="-2"
                  fontSize="12"
                  fontWeight={700}
                  fill={isSource ? "#fff" : "#111827"}
                >
                  H{house}
                </text>
                <text
                  textAnchor="middle"
                  dy="11"
                  fontSize="9"
                  fill={isSource ? "#e0e7ff" : "#4b5563"}
                >
                  {lord}
                </text>
              </g>
            );
          })}
        </svg>
      </div>
      <div>
        <p className="text-sm font-semibold mb-1">
          H{sourceHouse} lord ({row?.lord}) -- possible placements
        </p>
        <p className="text-xs text-ink-muted mb-3">
          Click any house on the wheel to trace its lord. Gold-ringed houses (H1, H4, H7, H9) are the
          Kendra + Trikona houses most decisive for Raja/Dhana Yoga formation.
        </p>
        {hoverConnection ? (
          <div className="rounded-lg border border-indigo/30 bg-indigo/5 p-3 text-sm mb-3">
            <p className="font-medium">H{sourceHouse} lord in H{hoverHouse}</p>
            <p className="text-ink-muted">{hoverConnection.connection}</p>
            <p className="text-xs mt-1" style={{ color: NATURE_STROKE[hoverConnection.dest_nature] }}>
              destination nature: {hoverConnection.dest_nature}
            </p>
          </div>
        ) : (
          <p className="text-xs text-ink-muted mb-3">Hover a line for the exact connection theme.</p>
        )}
        <div className="flex flex-wrap gap-2 text-[11px]">
          {Object.entries(NATURE_STROKE).map(([nature, color]) => (
            <span key={nature} className="flex items-center gap-1">
              <span className="inline-block h-2 w-2 rounded-full" style={{ background: color }} />
              {nature}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}
