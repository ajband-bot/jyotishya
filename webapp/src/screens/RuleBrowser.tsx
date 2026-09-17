import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { FileCode2, Search } from "lucide-react";
import { api, type RulePackRule, type RulePackSummary } from "../lib/api";

const STATUS_COLOR: Record<string, string> = {
  ACTIVE: "text-sage border-sage/30 bg-sage/5",
  DRAFT: "text-ink-muted border-ink/20 bg-ink/5",
  CONTESTED: "text-amber border-amber/30 bg-amber/5",
  DEPRECATED: "text-red-muted border-red-muted/30 bg-red-muted/5",
  SOURCE_FOUND: "text-indigo border-indigo/30 bg-indigo/5",
  VERIFIED: "text-sage border-sage/30 bg-sage/5",
};

function PackCard({ pack, selected, onClick }: { pack: RulePackSummary; selected: boolean; onClick: () => void }) {
  return (
    <button
      onClick={onClick}
      disabled={pack.kind === "v1_legacy"}
      className={`w-full rounded-lg border p-3 text-left text-sm transition-colors ${
        selected ? "border-indigo bg-indigo/5" : "border-ink/10 bg-surface hover:bg-bg"
      } ${pack.kind === "v1_legacy" ? "opacity-60" : ""}`}
    >
      <div className="flex items-center justify-between">
        <span className="font-medium">{pack.pack_id}</span>
        <span className="text-xs text-ink-muted">{pack.rule_count} rules</span>
      </div>
      <p className="mt-0.5 text-xs text-ink-muted">{pack.file}</p>
      {pack.note && <p className="mt-1 text-xs italic text-ink-muted">{pack.note}</p>}
      {pack.categories.length > 0 && (
        <p className="mt-1 text-xs text-indigo">{pack.categories.join(", ")}</p>
      )}
    </button>
  );
}

function RuleDetail({ rule }: { rule: RulePackRule }) {
  return (
    <div className="rounded-lg border border-ink/10 bg-surface p-4 shadow-sm">
      <div className="mb-1 flex flex-wrap items-center gap-2">
        <span className="font-mono text-xs text-ink-muted">{rule.id}</span>
        <span className={`rounded-full border px-2 py-0.5 text-[11px] font-medium ${STATUS_COLOR[rule.status] ?? ""}`}>
          {rule.status}
        </span>
        <span className="rounded-full border border-ink/15 px-2 py-0.5 text-[11px] text-ink-muted">
          {rule.category}
        </span>
        <span className="rounded-full border border-ink/15 px-2 py-0.5 text-[11px] text-ink-muted">
          confidence: {rule.confidence}
        </span>
        <span className="rounded-full border border-ink/15 px-2 py-0.5 text-[11px] text-ink-muted">
          tier {rule.source_tier}
        </span>
      </div>
      <h4 className="mb-1 font-semibold">{rule.title}</h4>
      <p className="mb-2 text-xs text-ink-muted">{rule.source_ref}</p>

      <div className="mb-2 space-y-1">
        {rule.conditions.map((c, i) => (
          <div key={i} className="rounded bg-bg px-2 py-1 font-mono text-xs">
            {c.path} {c.op} {JSON.stringify(c.value)}
          </div>
        ))}
      </div>

      {rule.outputs.map((o, i) => (
        <div key={i} className="rounded border border-gold/20 bg-gold/5 px-2 py-1 text-xs">
          <span className="font-medium text-gold">{o.kind}: </span>
          {JSON.stringify(o.payload)}
        </div>
      ))}

      {rule.notes.length > 0 && (
        <p className="mt-2 text-xs text-ink-muted italic">{rule.notes.join(" ")}</p>
      )}
    </div>
  );
}

/**
 * Rule Browser -- Phase 8 "check any rule.yaml" ask. Every v2 rule pack is
 * loaded through the same validated schema the evaluator itself uses, so
 * this view can never drift from what the engine actually executes.
 */
export function RuleBrowser() {
  const [selectedPack, setSelectedPack] = useState<string | null>(null);
  const [search, setSearch] = useState("");

  const packsQuery = useQuery({ queryKey: ["rule-packs"], queryFn: api.listRulePacks });
  const packQuery = useQuery({
    queryKey: ["rule-pack", selectedPack, search],
    queryFn: () => api.getRulePack(selectedPack!, { search: search || undefined }),
    enabled: !!selectedPack,
  });

  return (
    <div className="grid gap-4 md:grid-cols-[280px_1fr]">
      <div className="space-y-2">
        <div className="mb-2 flex items-center gap-2 text-sm font-semibold text-ink-muted">
          <FileCode2 size={16} /> Rule packs
        </div>
        {packsQuery.data?.packs.map((pack) => (
          <PackCard
            key={pack.pack_id}
            pack={pack}
            selected={selectedPack === pack.pack_id}
            onClick={() => setSelectedPack(pack.pack_id)}
          />
        ))}
      </div>

      <div>
        {!selectedPack && (
          <p className="text-ink-muted">
            Pick a rule pack on the left. The legacy v1 pack (rich prose/citation format) is browsable
            in full via the Learning tab's "Top Rules" panel instead of here.
          </p>
        )}
        {selectedPack && (
          <>
            <div className="relative mb-3">
              <Search size={14} className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-ink-muted" />
              <input
                className="w-full rounded-md border border-ink/20 bg-surface py-2 pl-8 pr-3 text-sm focus:border-indigo focus:outline-none"
                placeholder="Search by rule id or title..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
            </div>
            <p className="mb-2 text-xs text-ink-muted">
              {packQuery.data ? `${packQuery.data.rule_count} rule(s)` : "Loading..."}
            </p>
            <div className="space-y-2">
              {packQuery.data?.rules.map((rule) => (
                <RuleDetail key={rule.id} rule={rule} />
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  );
}
