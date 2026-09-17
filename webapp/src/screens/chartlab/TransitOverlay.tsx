import type { TransitPlanet } from "../../lib/api";
import { PLANET_COLOR, cellCenter } from "./layout";

/**
 * Transit badges overlaid on the South Indian grid (Chart Lab v2 Sprint 3,
 * spec section 7). Deliberately styled differently from natal planet
 * chips (outline ring instead of solid fill, offset toward the bottom of
 * the cell) so natal vs transiting is instantly distinguishable, never
 * relying on color alone (WCAG 2.2 AA -- also just good chart hygiene).
 */
export function TransitOverlay({
  transits,
  focusedPlanet,
  onSelect,
}: {
  transits: Record<string, TransitPlanet>;
  focusedPlanet: string | null;
  onSelect: (planet: string) => void;
}) {
  return (
    <div className="absolute inset-0 pointer-events-none">
      {Object.entries(transits).map(([planet, pos], index, entries) => {
        const { x, y } = cellCenter(pos.sign);
        const sameSignIndex = entries
          .slice(0, index)
          .filter(([, previous]) => previous.sign === pos.sign).length;
        const dim = focusedPlanet && focusedPlanet !== planet ? 0.35 : 1;
        return (
          <button
            key={planet}
            onClick={() => onSelect(planet)}
            aria-label={`Focus transit ${planet}, ${pos.sign_en}, ${pos.deg_in_sign.toFixed(1)} degrees`}
            title={`Transit ${planet} -- ${pos.sign_en} ${pos.deg_in_sign.toFixed(1)} deg${pos.retrograde ? " (R)" : ""}`}
            className="pointer-events-auto absolute z-10 flex min-h-6 min-w-[3.25rem] -translate-x-1/2 items-center justify-center gap-0.5 rounded-md border-2 bg-surface px-1 text-[10px] font-bold shadow-sm transition-opacity"
            style={{
              left: `${x}%`,
              top: `${y + 12 + sameSignIndex * 9}%`,
              borderColor: PLANET_COLOR[planet],
              color: PLANET_COLOR[planet],
              opacity: dim,
              outline: focusedPlanet === planet ? "2px solid #111827" : "none",
            }}
          >
            {planet}
          </button>
        );
      })}
    </div>
  );
}
