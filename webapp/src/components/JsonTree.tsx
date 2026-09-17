import { useState } from "react";
import { ChevronRight, ChevronDown } from "lucide-react";

/**
 * Generic collapsible viewer for any JSON-shaped API response.
 *
 * Design trade-off, disclosed rather than hidden (this app's own "never
 * sugarcoat" habit, applied to UI decisions): several derived-layer
 * sections (Panchanga, Graha Maitri, Vimsopaka, Gochara, Bhava Bala,
 * Marriage/Career/Remedy synthesis) have rich, evolving nested shapes.
 * Hand-building a bespoke table for every one of them would either lag
 * behind the engine (a stale UI silently hiding a new field) or cost far
 * more than this phase's scope justifies. This tree renders whatever the
 * API actually returns, always in sync by construction, while the small
 * number of highest-traffic sections (Vimsottari, Doshas/Yogas,
 * Ashtakavarga, Aspects) get dedicated, friendlier panels elsewhere.
 */
function isPlainObject(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function ScalarValue({ value }: { value: unknown }) {
  if (typeof value === "boolean") {
    return <span className={value ? "text-sage" : "text-red-muted"}>{String(value)}</span>;
  }
  if (value === null || value === undefined) {
    return <span className="text-ink-muted italic">null</span>;
  }
  return <span className="text-ink">{String(value)}</span>;
}

export function JsonTree({ data, depth = 0 }: { data: unknown; depth?: number }) {
  const [collapsed, setCollapsed] = useState(depth > 1);

  if (Array.isArray(data)) {
    if (data.length === 0) return <span className="text-ink-muted italic">[]</span>;
    if (data.every((item) => !isPlainObject(item) && !Array.isArray(item))) {
      return <span className="text-ink">{data.map(String).join(", ")}</span>;
    }
    return (
      <div className="border-l border-ink/10 pl-3">
        {data.map((item, i) => (
          <div key={i} className="py-0.5">
            <span className="text-ink-muted text-xs mr-2">[{i}]</span>
            <JsonTree data={item} depth={depth + 1} />
          </div>
        ))}
      </div>
    );
  }

  if (isPlainObject(data)) {
    const entries = Object.entries(data).filter(([k]) => k !== "model");
    if (entries.length === 0) return <span className="text-ink-muted italic">{"{}"}</span>;
    return (
      <div>
        {depth > 0 && (
          <button
            type="button"
            onClick={() => setCollapsed((c) => !c)}
            className="mb-0.5 flex items-center gap-1 text-xs text-ink-muted hover:text-indigo"
          >
            {collapsed ? <ChevronRight size={12} /> : <ChevronDown size={12} />}
            {collapsed ? `${entries.length} field(s)` : "collapse"}
          </button>
        )}
        {!collapsed && (
          <div className={depth > 0 ? "border-l border-ink/10 pl-3" : ""}>
            {entries.map(([key, value]) => (
              <div key={key} className="py-0.5 text-sm">
                <span className="font-medium text-indigo mr-2">{key}:</span>
                {isPlainObject(value) || Array.isArray(value) ? (
                  <JsonTree data={value} depth={depth + 1} />
                ) : (
                  <ScalarValue value={value} />
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    );
  }

  return <ScalarValue value={data} />;
}

/** A titled card wrapping JsonTree -- the standard shell for "evidence"
 * sections that don't yet have a bespoke renderer. */
export function EvidenceCard({ title, subtitle, data }: { title: string; subtitle?: string; data: unknown }) {
  return (
    <div className="rounded-lg border border-ink/10 bg-surface p-5 shadow-sm">
      <h3 className="mb-1 text-base font-semibold font-scripture">{title}</h3>
      {subtitle && <p className="mb-3 text-xs text-ink-muted">{subtitle}</p>}
      <JsonTree data={data} />
    </div>
  );
}
