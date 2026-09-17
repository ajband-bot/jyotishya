import type { TransitPlanet } from "../../lib/api";
import { PLANET_COLOR } from "./layout";
import type { ActiveDasha } from "./DashaModule";

function TransitRow({
  planet,
  pos,
  focused,
  isDoubleActivation,
  onClick,
}: {
  planet: string;
  pos: TransitPlanet;
  focused: boolean;
  isDoubleActivation: boolean;
  onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      className={`w-full text-left rounded-lg border p-2 text-xs ${
        focused ? "border-indigo/50 bg-indigo/5" : "border-ink/10 bg-surface hover:border-indigo/30"
      }`}
    >
      <div className="flex items-center justify-between">
        <span className="font-semibold flex items-center gap-1.5">
          <span className="inline-block h-2.5 w-2.5 rounded-full border-2" style={{ borderColor: PLANET_COLOR[planet] }} />
          {planet}
        </span>
        {isDoubleActivation && (
          <span className="text-[9px] font-bold px-1.5 py-0.5 rounded bg-gold text-white">Double Activation</span>
        )}
      </div>
      <p className="text-ink-muted mt-0.5">
        {pos.sign_en} {pos.deg_in_sign.toFixed(1)}deg {pos.retrograde ? "(R)" : ""}
        {pos.dignity && ` -- ${pos.dignity}`}
      </p>
      <p className="text-ink-muted">
        From Lagna: H{pos.house_from_lagna} · From Moon: H{pos.house_from_moon}
      </p>
      {focused && (
        <div className="mt-1 space-y-0.5">
          <p className="text-ink-muted">
            Aspects: {pos.aspects_houses.map((h) => `H${h}`).join(" · ")}
          </p>
          {pos.natal_contacts.length > 0 ? (
            <p className="text-indigo">
              Natal contacts:{" "}
              {pos.natal_contacts
                .map((c) =>
                  c.kind === "conjunction"
                    ? `${c.natal_planet} (conjunction, orb ${c.orb_deg}deg)`
                    : `${c.natal_planet} (aspect -> H${c.house})`,
                )
                .join(" · ")}
            </p>
          ) : (
            <p className="text-ink-muted italic">No exact natal contacts right now.</p>
          )}
        </div>
      )}
    </button>
  );
}

/**
 * Transit info list + focus detail (Chart Lab v2 Sprint 3, spec sections
 * 7-9). "Double Activation" badge fires when a transiting planet is ALSO
 * the current MD/AD/PD lord -- exactly the compounding-evidence pattern
 * the spec calls out.
 */
export function TransitPanel({
  enabled,
  onToggle,
  isFetching,
  transits,
  focusedPlanet,
  onFocusChange,
  active,
}: {
  enabled: boolean;
  onToggle: (v: boolean) => void;
  isFetching: boolean;
  transits: Record<string, TransitPlanet> | null;
  focusedPlanet: string | null;
  onFocusChange: (planet: string | null) => void;
  active: ActiveDasha;
}) {
  const dashaLords = new Set([active.md, active.ad, active.pd].filter(Boolean));

  return (
    <div className="rounded-lg border border-ink/10 bg-surface p-3">
      <div className="flex items-center justify-between mb-2">
        <p className="text-sm font-semibold">Transits</p>
        <label className="flex items-center gap-1.5 text-xs">
          <input type="checkbox" checked={enabled} onChange={(e) => onToggle(e.target.checked)} />
          Show on chart
        </label>
      </div>
      {!enabled && <p className="text-[11px] text-ink-muted">Enable to overlay real Swiss Ephemeris positions.</p>}
      {enabled && isFetching && <p className="text-[11px] text-ink-muted">Computing transits...</p>}
      {enabled && transits && (
        <div className="space-y-1.5 max-h-72 overflow-y-auto">
          {Object.entries(transits).map(([planet, pos]) => (
            <TransitRow
              key={planet}
              planet={planet}
              pos={pos}
              focused={focusedPlanet === planet}
              isDoubleActivation={dashaLords.has(planet)}
              onClick={() => onFocusChange(focusedPlanet === planet ? null : planet)}
            />
          ))}
        </div>
      )}
    </div>
  );
}
