import { useEffect, useId, useRef } from "react";
import mermaid from "mermaid";

let initialized = false;

function ensureInit() {
  if (initialized) return;
  mermaid.initialize({ startOnLoad: false, theme: "neutral", securityLevel: "loose" });
  initialized = true;
}

/**
 * Thin Mermaid.js wrapper -- renders a diagram definition string into an
 * SVG. Used across the Learning tab for Obsidian-style visual references
 * (dasha cycle, rule mindmap) instead of flat tables, per Ajay's ask.
 */
export function MermaidDiagram({ definition }: { definition: string }) {
  const containerRef = useRef<HTMLDivElement>(null);
  const idBase = useId().replace(/[:]/g, "");

  useEffect(() => {
    ensureInit();
    let cancelled = false;
    const renderId = `mermaid-${idBase}`;
    mermaid.render(renderId, definition).then(({ svg }) => {
      if (!cancelled && containerRef.current) {
        containerRef.current.innerHTML = svg;
      }
    }).catch((err) => {
      if (!cancelled && containerRef.current) {
        containerRef.current.innerHTML = `<p class="text-red-muted text-xs">Diagram render failed: ${String(err)}</p>`;
      }
    });
    return () => {
      cancelled = true;
    };
  }, [definition, idBase]);

  return <div ref={containerRef} className="overflow-x-auto" />;
}
