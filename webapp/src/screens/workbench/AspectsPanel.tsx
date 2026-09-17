import type { FullContext } from "../../lib/api";

const PLANET_ORDER = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"];
const HOUSES = Array.from({ length: 12 }, (_, i) => i + 1);

/**
 * Aspects (Drishti) tab -- both directions of the same computed map:
 * "which houses does each planet aspect" and "which planets aspect each
 * house" -- straight from app.derived.aspects.full_aspect_report.
 */
export function AspectsPanel({ fullContext }: { fullContext: FullContext }) {
  const aspects = fullContext.aspects as
    | { graha_drishti: Record<string, number[]>; aspected_by: Record<string, string[]> }
    | undefined;

  if (!aspects) return <p className="text-ink-muted">Aspect data unavailable.</p>;

  return (
    <div className="grid gap-4 md:grid-cols-2">
      <div className="rounded-lg border border-ink/10 bg-surface p-5 shadow-sm">
        <h3 className="mb-3 text-base font-semibold font-scripture">Planet -&gt; Houses Aspected</h3>
        <table className="w-full text-sm">
          <tbody>
            {PLANET_ORDER.filter((p) => aspects.graha_drishti[p]).map((planet) => (
              <tr key={planet} className="border-b border-ink/5 last:border-0">
                <td className="py-1.5 pr-3 font-medium w-24">{planet}</td>
                <td className="py-1.5 text-ink-muted">
                  {aspects.graha_drishti[planet].length > 0
                    ? aspects.graha_drishti[planet].map((h) => `H${h}`).join(", ")
                    : "--"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="rounded-lg border border-ink/10 bg-surface p-5 shadow-sm">
        <h3 className="mb-3 text-base font-semibold font-scripture">House -&gt; Aspected By</h3>
        <table className="w-full text-sm">
          <tbody>
            {HOUSES.map((h) => (
              <tr key={h} className="border-b border-ink/5 last:border-0">
                <td className="py-1.5 pr-3 font-medium w-16">H{h}</td>
                <td className="py-1.5 text-ink-muted">
                  {(aspects.aspected_by[String(h)] ?? []).length > 0
                    ? aspects.aspected_by[String(h)].join(", ")
                    : "--"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
