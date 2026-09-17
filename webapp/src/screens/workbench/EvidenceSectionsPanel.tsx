import type { FullContext } from "../../lib/api";
import { EvidenceCard } from "../../components/JsonTree";

/**
 * Generic grid of EvidenceCard sections -- reused for both the "Strength &
 * Timing" tab (Vimsopaka/Gochara/Bhava Bala/Panchanga/Graha Maitri/Argala)
 * and the "Domains" tab (Marriage/Career/Remedies). See JsonTree.tsx's
 * module docstring for why these stay evidence-tree views rather than
 * bespoke tables.
 */
export function EvidenceSectionsPanel({
  fullContext,
  sections,
}: {
  fullContext: FullContext;
  sections: Array<{ key: string; title: string; subtitle?: string }>;
}) {
  return (
    <div className="grid gap-4 md:grid-cols-2">
      {sections
        .filter((s) => fullContext[s.key] !== undefined)
        .map((s) => (
          <EvidenceCard key={s.key} title={s.title} subtitle={s.subtitle} data={fullContext[s.key]} />
        ))}
    </div>
  );
}
