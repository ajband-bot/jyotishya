import { useQuery } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import { ChevronDown, ChevronRight } from "lucide-react";
import { api, type TopRule } from "../../lib/api";
import { MermaidDiagram } from "../../components/MermaidDiagram";

function buildMindmap(byDomain: Record<string, string[]>): string {
  const lines = ["mindmap", "  root((Top Rules))"];
  for (const [domain, ruleIds] of Object.entries(byDomain)) {
    lines.push(`    ${domain}`);
    for (const ruleId of ruleIds) {
      lines.push(`      ${ruleId}`);
    }
  }
  return lines.join("\n");
}

function RuleCard({ rule }: { rule: TopRule }) {
  const [open, setOpen] = useState(false);
  return (
    <div className="rounded-lg border border-ink/10 bg-surface shadow-sm">
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center justify-between p-3 text-left"
      >
        <div className="flex items-center gap-2">
          {open ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
          <span className="font-semibold text-sm">{rule.rule_id}</span>
          <span className="text-sm text-ink-muted">{rule.name}</span>
        </div>
        <span className="text-[10px] px-2 py-0.5 rounded-full border border-indigo/30 text-indigo">
          {rule.authority_tier}
        </span>
      </button>
      {open && (
        <div className="px-4 pb-4 text-sm space-y-2">
          <p className="text-ink-muted italic">{rule.chapter_signal}</p>
          <p><span className="font-medium">Canonical statement: </span>{rule.canonical_statement}</p>
          <p className="text-xs text-ink-muted"><span className="font-medium text-ink">Why it matters: </span>{rule.why_it_matters}</p>
          {rule.activation_conditions.length > 0 && (
            <div>
              <p className="text-xs font-medium">Activation conditions:</p>
              <ul className="list-disc list-inside text-xs text-ink-muted">
                {rule.activation_conditions.map((c, i) => <li key={i}>{c}</li>)}
              </ul>
            </div>
          )}
          {rule.examples.length > 0 && (
            <div>
              <p className="text-xs font-medium">Worked examples:</p>
              <ul className="list-disc list-inside text-xs text-ink-muted space-y-1">
                {rule.examples.map((ex, i) => <li key={i}>{ex}</li>)}
              </ul>
            </div>
          )}
          <div className="flex flex-wrap gap-1 pt-1">
            {rule.domain_tags.map((d) => (
              <span key={d} className="text-[10px] px-2 py-0.5 rounded-full bg-ink/5 text-ink-muted">{d}</span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

/**
 * Top Rules Reference -- the 20-of-30 BPHS rule-card corpus that governs
 * how every chart is actually interpreted. Mindmap overview (Obsidian-
 * style graph-of-concepts) + expandable per-rule detail cards.
 */
export function TopRulesPanel() {
  const { data } = useQuery({ queryKey: ["ref-top-rules"], queryFn: api.getTopRules });
  const mindmap = useMemo(() => (data ? buildMindmap(data.by_domain) : ""), [data]);

  if (!data) return <p className="text-ink-muted">Loading...</p>;

  return (
    <div>
      <p className="text-sm text-amber mb-4 rounded-md border border-amber/30 bg-amber/5 p-2">
        {data.coverage_note}
      </p>
      <div className="mb-6 rounded-lg border border-ink/10 bg-surface p-4 shadow-sm">
        <MermaidDiagram definition={mindmap} />
      </div>
      <div className="grid gap-3">
        {data.rules.map((rule) => (
          <RuleCard key={rule.rule_id} rule={rule} />
        ))}
      </div>
    </div>
  );
}
