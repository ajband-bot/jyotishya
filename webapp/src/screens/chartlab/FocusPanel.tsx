import type { SandboxAnalysis, SandboxPlanetPlacement } from "../../lib/api";
import { PLANET_COLOR, SIGN_LORDS, SIGN_NAMES } from "./layout";

/**
 * Planet Focus Mode side panel (Chart Lab v2, Sprint 1 -- spec section 14).
 * Shown whenever a planet is selected on the canvas. Before "Analyze" has
 * run it's just the raw degree/retrograde editor (unchanged behaviour);
 * once a SandboxAnalysis exists it upgrades into the full focus summary --
 * functional nature, placement, dignity, combustion, retrograde,
 * dispositor, D9 condition. D10/Dasha/Transit are honestly labeled as
 * data gaps rather than fabricated (Chart Lab has no birth data -- see
 * app/derived/sandbox.py data_gaps).
 */
export function FocusPanel({
  planet,
  placement,
  result,
  onUpdate,
}: {
  planet: string;
  placement: SandboxPlanetPlacement;
  result: SandboxAnalysis | null;
  onUpdate: (patch: Partial<SandboxPlanetPlacement>) => void;
}) {
  const obs = result?.planets[planet];
  const dispositor = obs ? SIGN_LORDS[obs.sign - 1] : SIGN_NAMES[placement.sign - 1] && SIGN_LORDS[placement.sign - 1];

  return (
    <div className="mt-4 rounded-lg border border-ink/10 bg-surface p-3">
      <p className="text-sm font-semibold mb-2 flex items-center gap-2">
        <span className="inline-block h-2.5 w-2.5 rounded-full" style={{ background: PLANET_COLOR[planet] }} />
        {planet} focus
      </p>

      {planet !== "Ketu" && (
        <>
          <label className="text-xs text-ink-muted">Degree in sign: {placement.degree.toFixed(1)}°</label>
          <input
            type="range"
            min={0}
            max={29.9}
            step={0.1}
            value={placement.degree}
            onChange={(e) => onUpdate({ degree: Number(e.target.value) })}
            className="w-full"
          />
          <label className="flex items-center gap-2 text-xs mt-2">
            <input
              type="checkbox"
              checked={placement.retrograde}
              onChange={(e) => onUpdate({ retrograde: e.target.checked })}
            />
            Retrograde
          </label>
        </>
      )}

      {!obs ? (
        <p className="text-[11px] text-ink-muted mt-3 border-t border-ink/10 pt-2">
          Click "Analyze Chart" to see functional nature, dignity, combustion, dispositor and D9
          condition here.
        </p>
      ) : (
        <div className="mt-3 border-t border-ink/10 pt-2 space-y-1 text-xs">
          <p>
            Placement: <b>{obs.sign_en}</b> H{obs.house}
          </p>
          {obs.functional && (
            <p>
              Functional nature: <b>{obs.functional.classification}</b> ({obs.functional.tag})
            </p>
          )}
          <p>
            Dignity: <b>{obs.dignity !== "n/a" ? obs.dignity : "-- (node)"}</b>
          </p>
          <p>Combustion: <b>{obs.combust ? "Combust" : "Not combust"}</b></p>
          <p>Retrograde: <b>{obs.retrograde ? "Yes" : "No"}</b></p>
          <p>
            Dispositor: <b>{dispositor}</b> {dispositor && `(lord of ${obs.sign_en})`}
          </p>
          <p>
            D9 condition: <b>{obs.d9_sign_en}</b> ({obs.d9_state}
            {obs.vargottama ? " -- Vargottama" : ""})
          </p>
          <p className="text-ink-muted mt-2 italic">
            data_gap: D10 condition, Daśā status, and Transit status need real birth data --
            not available in Chart Lab's sandbox mode.
          </p>
        </div>
      )}
    </div>
  );
}
