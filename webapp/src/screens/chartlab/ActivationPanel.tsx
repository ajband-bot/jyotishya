import type { SandboxAnalysis, TransitPlanet } from "../../lib/api";
import { SIGN_LORDS, PLANET_COLOR } from "./layout";
import type { ActiveDasha } from "./DashaModule";

interface LordCard {
  role: "MD" | "AD" | "PD";
  planet: string;
  owns: number[];
  occupies: number;
  aspects: number[];
  conjunct: string[];
  dispositor: string;
  transit?: TransitPlanet;
}

function buildCard(
  role: "MD" | "AD" | "PD",
  planet: string,
  result: SandboxAnalysis,
  transits: Record<string, TransitPlanet> | null,
): LordCard | null {
  const p = result.planets[planet];
  if (!p) return null;
  const conjunct = Object.entries(result.planets)
    .filter(([name, other]) => name !== planet && other.house === p.house)
    .map(([name]) => name);
  return {
    role,
    planet,
    owns: p.functional?.houses_owned ?? [],
    occupies: p.house,
    aspects: p.aspects_houses,
    conjunct,
    dispositor: SIGN_LORDS[p.sign - 1],
    transit: transits?.[planet],
  };
}

/** Every distinct piece of computed evidence touching a house, tagged by
 * source so the ranking (and the user) can tell WHY a house is "hot"
 * instead of just seeing a number (spec sections 19-20). */
function collectEvidence(cards: LordCard[]): Record<number, string[]> {
  const evidence: Record<number, string[]> = {};
  const push = (house: number, note: string) => {
    evidence[house] = [...(evidence[house] ?? []), note];
  };
  for (const c of cards) {
    for (const h of c.owns) push(h, `${c.planet} (${c.role}) owns`);
    push(c.occupies, `${c.planet} (${c.role}) occupies`);
    for (const h of c.aspects) push(h, `${c.planet} (${c.role}) aspects`);
    if (c.transit) {
      push(c.transit.house_from_lagna, `Transit ${c.planet} (${c.role}) occupies`);
      for (const h of c.transit.aspects_houses) push(h, `Transit ${c.planet} (${c.role}) aspects`);
    }
  }
  return evidence;
}

function CardView({ card }: { card: LordCard }) {
  return (
    <div className="rounded-lg border border-ink/10 bg-surface p-3 text-xs">
      <p className="font-semibold flex items-center gap-2 mb-1">
        <span className="inline-block h-2.5 w-2.5 rounded-full" style={{ background: PLANET_COLOR[card.planet] }} />
        {card.planet} {card.role}
      </p>
      <p>Owns: <b>{card.owns.length ? card.owns.map((h) => `H${h}`).join(" · ") : "none"}</b></p>
      <p>Occupies: <b>H{card.occupies}</b></p>
      <p>Aspects: <b>{card.aspects.map((h) => `H${h}`).join(" · ")}</b></p>
      {card.conjunct.length > 0 && <p>Conjunct: <b>{card.conjunct.join(" · ")}</b></p>}
      <p>Dispositor: <b>{card.dispositor}</b></p>
      {card.transit && (
        <p className="mt-1 pt-1 border-t border-indigo/10 text-indigo">
          Current trigger: Transit {card.planet} is in H{card.transit.house_from_lagna}, aspecting{" "}
          {card.transit.aspects_houses.map((h) => `H${h}`).join(" · ") || "nothing new"}
        </p>
      )}
    </div>
  );
}

/**
 * Current Activation panel (Chart Lab v2 spec sections 6, 19-20). Given
 * the active MD/AD/PD lords, shows what each one owns/occupies/aspects,
 * and -- Sprint 5 -- folds in each lord's REAL transit position (when
 * Transits are enabled) as additional evidence, so a house that is owned
 * natally AND currently being transited by the same lord shows up as a
 * stronger "Double Activation" signal, not just a bigger number.
 */
export function ActivationPanel({
  active,
  result,
  transits,
}: {
  active: ActiveDasha;
  result: SandboxAnalysis | null;
  transits: Record<string, TransitPlanet> | null;
}) {
  if (!result) {
    return (
      <div className="rounded-lg border border-ink/10 bg-surface p-3 text-xs text-ink-muted">
        Click "Analyze Chart" to see MD/AD/PD house activation evidence.
      </div>
    );
  }

  const cards = ([
    ["MD", active.md],
    ["AD", active.ad],
    ["PD", active.pd],
  ] as const)
    .map(([role, planet]) => (planet ? buildCard(role, planet, result, transits) : null))
    .filter((c): c is LordCard => c !== null);

  const evidence = collectEvidence(cards);
  const rankedHouses = Object.entries(evidence)
    .map(([house, notes]) => ({ house: Number(house), notes, hits: notes.length }))
    .sort((a, b) => b.hits - a.hits)
    .filter((h) => h.hits > 0);

  return (
    <div className="space-y-3">
      <div className="grid gap-2 md:grid-cols-3">
        {cards.map((c) => (
          <CardView key={c.role} card={c} />
        ))}
      </div>
      {rankedHouses.length > 0 && (
        <div className="rounded-lg border border-indigo/20 bg-indigo/5 p-3 text-xs">
          <p className="font-semibold mb-1">Most activated houses</p>
          <div className="space-y-1.5">
            {rankedHouses.map((h) => (
              <details key={h.house}>
                <summary
                  className={`cursor-pointer inline-block ${h.hits >= 3 ? "font-bold text-gold" : h.hits >= 2 ? "font-bold text-indigo" : "text-ink-muted"}`}
                >
                  H{h.house} ({h.hits} confirmation{h.hits > 1 ? "s" : ""})
                  {h.notes.some((n) => n.startsWith("Transit")) && h.notes.some((n) => !n.startsWith("Transit")) && (
                    <span className="ml-2 text-[9px] font-bold px-1.5 py-0.5 rounded bg-gold text-white">
                      Double Activation
                    </span>
                  )}
                </summary>
                <ul className="list-disc list-inside ml-3 text-ink-muted">
                  {h.notes.map((note, i) => (
                    <li key={i}>{note}</li>
                  ))}
                </ul>
              </details>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
