import { useQuery } from "@tanstack/react-query";
import { useMemo } from "react";
import ReactFlow, { Background, Controls, type Edge, type Node } from "reactflow";
import "reactflow/dist/style.css";
import { api } from "../../lib/api";

const RADIUS = 220;

function layoutNodes(planetIds: string[]): Node[] {
  const n = planetIds.length;
  return planetIds.map((id, i) => {
    const angle = (2 * Math.PI * i) / n - Math.PI / 2;
    return {
      id,
      data: { label: id },
      position: { x: RADIUS * Math.cos(angle) + RADIUS, y: RADIUS * Math.sin(angle) + RADIUS },
      style: {
        borderRadius: 9999,
        padding: 10,
        background: "#ede9fe",
        border: "2px solid #6366f1",
        fontWeight: 600,
        fontSize: 13,
      },
    };
  });
}

/**
 * Planet Relationship Graph -- Obsidian-style force/radial graph of the
 * classical natural friend/enemy table (BPHS Ch.3), replacing the flat
 * table with an interactive, draggable node graph. Green edges = friends,
 * red edges = enemies; unlabeled pairs are neutral.
 */
export function PlanetRelationshipGraphPanel() {
  const { data } = useQuery({
    queryKey: ["ref-planet-graph"],
    queryFn: api.getPlanetRelationshipGraph,
  });

  const nodes = useMemo(() => (data ? layoutNodes(data.nodes.map((n) => n.id)) : []), [data]);
  const edges = useMemo<Edge[]>(() => {
    if (!data) return [];
    return data.edges.map((e, i) => ({
      id: `${e.source}-${e.target}-${i}`,
      source: e.source,
      target: e.target,
      animated: e.kind === "friend",
      style: { stroke: e.kind === "friend" ? "#22c55e" : "#ef4444", strokeWidth: 2 },
      label: e.kind,
      labelStyle: { fontSize: 10, fill: e.kind === "friend" ? "#16a34a" : "#dc2626" },
    }));
  }, [data]);

  if (!data) return <p className="text-ink-muted">Loading...</p>;

  return (
    <div>
      <p className="text-sm text-ink-muted mb-3">
        Drag nodes to explore. Green = natural friend, red = natural enemy. Pairs with no edge are neutral.
        Source: BPHS Ch.3.
      </p>
      <div style={{ height: 480 }} className="rounded-lg border border-ink/10 bg-surface shadow-sm">
        <ReactFlow nodes={nodes} edges={edges} fitView>
          <Background />
          <Controls />
        </ReactFlow>
      </div>
    </div>
  );
}
