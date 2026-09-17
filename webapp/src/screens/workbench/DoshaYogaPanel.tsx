import { useState } from "react";
import { ChevronDown, ChevronRight } from "lucide-react";
import type { FullContext } from "../../lib/api";
import { JsonTree } from "../../components/JsonTree";

function isPresent(detail: unknown): boolean | null {
  if (typeof detail !== "object" || detail === null) return null;
  const d = detail as Record<string, unknown>;
  if ("present" in d) return Boolean(d.present);
  if ("any_present" in d) return Boolean(d.any_present);
  if ("type" in d) return d.type !== "none" && d.type !== null;
  return null;
}

function humanize(key: string): string {
  return key.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

function RegisterRow({ name, detail }: { name: string; detail: unknown }) {
  const [open, setOpen] = useState(false);
  const present = isPresent(detail);
  const badge =
    present === true ? "bg-red-muted/10 text-red-muted border-red-muted/30" :
    present === false ? "bg-sage/10 text-sage border-sage/30" :
    "bg-ink/5 text-ink-muted border-ink/15";
  const label = present === true ? "Present" : present === false ? "Absent" : "See detail";

  return (
    <div className="border-b border-ink/5 last:border-0 py-2">
      <button type="button" onClick={() => setOpen((o) => !o)} className="flex w-full items-center justify-between gap-2 text-left">
        <span className="flex items-center gap-2 text-sm font-medium">
          {open ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
          {humanize(name)}
        </span>
        <span className={`shrink-0 rounded-full border px-2 py-0.5 text-[11px] font-medium ${badge}`}>{label}</span>
      </button>
      {open && (
        <div className="mt-2 pl-5">
          <JsonTree data={detail} depth={1} />
        </div>
      )}
    </div>
  );
}

/**
 * Doshas & Yogas tab -- the full register (docs/dosha-registry.md's 8
 * mandatory checks + the compiled yoga set), each row expandable to its
 * full computed evidence.
 */
export function DoshaYogaPanel({ fullContext }: { fullContext: FullContext }) {
  const doshas = (fullContext.doshas as Record<string, unknown>) ?? {};
  const yogas = (fullContext.yogas as Record<string, unknown>) ?? {};

  return (
    <div className="grid gap-4 md:grid-cols-2">
      <div className="rounded-lg border border-ink/10 bg-surface p-5 shadow-sm">
        <h3 className="mb-2 text-base font-semibold font-scripture">Dosha Register</h3>
        <div>
          {Object.entries(doshas).map(([name, detail]) => (
            <RegisterRow key={name} name={name} detail={detail} />
          ))}
        </div>
      </div>
      <div className="rounded-lg border border-ink/10 bg-surface p-5 shadow-sm">
        <h3 className="mb-2 text-base font-semibold font-scripture">Compiled Yogas</h3>
        <div>
          {Object.entries(yogas).map(([name, detail]) => (
            <RegisterRow key={name} name={name} detail={detail} />
          ))}
        </div>
      </div>
    </div>
  );
}
