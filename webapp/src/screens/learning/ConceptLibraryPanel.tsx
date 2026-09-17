import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { api, type ConceptEntry } from "../../lib/api";

const QUALITY_COLOR: Record<string, string> = {
  computed: "text-sage border-sage/30 bg-sage/5",
  computed_simplified: "text-gold border-gold/30 bg-gold/5",
  computed_with_conflict: "text-amber border-amber/30 bg-amber/5",
  data_gap: "text-red-muted border-red-muted/30 bg-red-muted/5",
};

function ConceptCard({ entry }: { entry: ConceptEntry }) {
  return (
    <div className="rounded-lg border border-ink/10 bg-surface p-4 shadow-sm">
      <div className="mb-1 flex items-start justify-between gap-2">
        <h4 className="font-semibold font-scripture">
          {entry.english_gloss}
          {entry.sanskrit_term && <span className="ml-1 text-xs text-ink-muted">({entry.sanskrit_term})</span>}
        </h4>
        <span className={`shrink-0 rounded-full border px-2 py-0.5 text-[10px] font-semibold ${QUALITY_COLOR[entry.quality_label]}`}>
          {entry.quality_label}
        </span>
      </div>
      <p className="mb-2 text-sm text-ink">{entry.classical_definition}</p>
      <p className="mb-1 text-xs text-ink-muted">
        <span className="font-medium">Citation:</span> {entry.primary_citation}
      </p>
      {entry.code_ref && (
        <p className="mb-1 text-xs text-ink-muted">
          <span className="font-medium">Implemented at:</span> <code>{entry.code_ref}</code>
        </p>
      )}
      {entry.caveats.length > 0 && (
        <ul className="mt-2 list-disc space-y-1 pl-4 text-xs text-amber">
          {entry.caveats.map((c, i) => (
            <li key={i}>{c}</li>
          ))}
        </ul>
      )}
      {entry.cross_check_note && (
        <p className="mt-2 text-xs italic text-ink-muted">{entry.cross_check_note}</p>
      )}
    </div>
  );
}

/**
 * Concept Library (build_plan.md Phase 7 "learning platform" cheat sheet) --
 * renders app.engine.cheatsheet.concepts's registry: every classical
 * Jyotisha concept this project implements, with citation, code_ref,
 * honesty label, and caveats. Read top to bottom to learn both the
 * doctrine and this project's own thought process at once.
 */
export function ConceptLibraryPanel() {
  const [category, setCategory] = useState<string | undefined>(undefined);
  const { data, isLoading } = useQuery({
    queryKey: ["cheatsheet-concepts", category],
    queryFn: () => api.getCheatsheetConcepts(category),
  });

  if (isLoading) return <p className="text-ink-muted">Loading concept registry...</p>;
  if (!data) return null;

  return (
    <div>
      <p className="mb-4 text-sm text-ink-muted">
        {data.total_concepts} concepts spanning every layer of the Process (Truth {"->"} Derived {"->"}
        {" "}Rules {"->"} Engine). See <code>docs/JYOTISHA_CHEATSHEET.md</code> for the same content as a
        single generated document.
      </p>
      <div className="mb-4 flex flex-wrap gap-2">
        <button
          onClick={() => setCategory(undefined)}
          className={`rounded-md px-3 py-1.5 text-sm font-medium ${!category ? "bg-indigo text-white" : "bg-surface border border-ink/20"}`}
        >
          All
        </button>
        {data.categories.map((cat) => (
          <button
            key={cat}
            onClick={() => setCategory(cat)}
            className={`rounded-md border px-3 py-1.5 text-sm font-medium ${category === cat ? "bg-indigo text-white border-indigo" : "border-ink/20"}`}
          >
            {cat}
          </button>
        ))}
      </div>
      <div className="grid gap-3 md:grid-cols-2">
        {data.concepts.map((entry) => (
          <ConceptCard key={entry.concept_id} entry={entry} />
        ))}
      </div>
    </div>
  );
}
