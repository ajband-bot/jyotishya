import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Terminal, Send } from "lucide-react";
import { getApiV2Operations, invokeApiConsole, type OpenApiOperation } from "../lib/api";

const METHOD_COLOR: Record<string, string> = {
  GET: "text-sage border-sage/30 bg-sage/5",
  POST: "text-indigo border-indigo/30 bg-indigo/5",
  PUT: "text-amber border-amber/30 bg-amber/5",
  DELETE: "text-red-muted border-red-muted/30 bg-red-muted/5",
};

function groupByTag(ops: OpenApiOperation[]): Record<string, OpenApiOperation[]> {
  const groups: Record<string, OpenApiOperation[]> = {};
  for (const op of ops) {
    const tag = op.tags[0] ?? "other";
    (groups[tag] ??= []).push(op);
  }
  return groups;
}

/**
 * API Console -- Phase 8 "independently trigger all the V2 APIs" ask.
 * Reads FastAPI's own auto-generated /openapi.json (never a hand-maintained
 * duplicate list -- new endpoints show up here automatically) and builds a
 * minimal Postman-style form: fill in path/query params, optionally a JSON
 * body, hit Send, see the raw response.
 */
export function ApiConsole() {
  const opsQuery = useQuery({ queryKey: ["openapi-v2-ops"], queryFn: getApiV2Operations });
  const [selected, setSelected] = useState<OpenApiOperation | null>(null);
  const [pathParams, setPathParams] = useState<Record<string, string>>({});
  const [queryParams, setQueryParams] = useState<Record<string, string>>({});
  const [body, setBody] = useState("");
  const [result, setResult] = useState<{ status: number; ok: boolean; data: unknown } | null>(null);
  const [sending, setSending] = useState(false);

  const selectOp = (op: OpenApiOperation) => {
    setSelected(op);
    setPathParams({});
    setQueryParams({});
    setBody(op.requestBodyExample ? "{}" : "");
    setResult(null);
  };

  const runRequest = async () => {
    if (!selected) return;
    setSending(true);
    let path = selected.path;
    for (const [key, value] of Object.entries(pathParams)) {
      path = path.replace(`{${key}}`, encodeURIComponent(value));
    }
    const qs = Object.entries(queryParams)
      .filter(([, v]) => v !== "")
      .map(([k, v]) => `${encodeURIComponent(k)}=${encodeURIComponent(v)}`)
      .join("&");
    if (qs) path += `?${qs}`;
    try {
      const res = await invokeApiConsole(selected.method, path, selected.requestBodyExample ? body : undefined);
      setResult(res);
    } finally {
      setSending(false);
    }
  };

  const groups = opsQuery.data ? groupByTag(opsQuery.data) : {};
  const pathParamDefs = selected?.parameters.filter((p) => p.in === "path") ?? [];
  const queryParamDefs = selected?.parameters.filter((p) => p.in === "query") ?? [];

  return (
    <div className="grid gap-4 md:grid-cols-[300px_1fr]">
      <div className="max-h-[70vh] space-y-4 overflow-y-auto pr-1">
        <div className="mb-1 flex items-center gap-2 text-sm font-semibold text-ink-muted">
          <Terminal size={16} /> Every /api/v2 endpoint
        </div>
        {Object.entries(groups).map(([tag, ops]) => (
          <div key={tag}>
            <p className="mb-1 text-xs font-semibold uppercase tracking-wide text-gold">{tag}</p>
            <div className="space-y-1">
              {ops.map((op) => (
                <button
                  key={`${op.method}-${op.path}`}
                  onClick={() => selectOp(op)}
                  className={`w-full rounded-md border px-2 py-1.5 text-left text-xs transition-colors ${
                    selected?.path === op.path && selected.method === op.method
                      ? "border-indigo bg-indigo/5"
                      : "border-ink/10 bg-surface hover:bg-bg"
                  }`}
                >
                  <span className={`mr-1.5 rounded border px-1.5 py-0.5 font-mono font-semibold ${METHOD_COLOR[op.method] ?? ""}`}>
                    {op.method}
                  </span>
                  <span className="font-mono">{op.path}</span>
                </button>
              ))}
            </div>
          </div>
        ))}
      </div>

      <div>
        {!selected && <p className="text-ink-muted">Pick any endpoint on the left to build and send a request.</p>}
        {selected && (
          <div className="space-y-4 rounded-lg border border-ink/10 bg-surface p-5 shadow-sm">
            <div>
              <span className={`mr-2 rounded border px-2 py-0.5 font-mono text-xs font-semibold ${METHOD_COLOR[selected.method] ?? ""}`}>
                {selected.method}
              </span>
              <span className="font-mono text-sm">{selected.path}</span>
              <p className="mt-1 text-xs text-ink-muted">{selected.summary}</p>
            </div>

            {pathParamDefs.map((p) => (
              <label key={p.name} className="block">
                <span className="mb-1 block text-xs font-semibold uppercase tracking-wide text-ink-muted">
                  {p.name} (path)
                </span>
                <input
                  className="w-full rounded-md border border-ink/20 bg-surface px-3 py-1.5 text-sm"
                  value={pathParams[p.name] ?? ""}
                  onChange={(e) => setPathParams((prev) => ({ ...prev, [p.name]: e.target.value }))}
                />
              </label>
            ))}

            {queryParamDefs.map((p) => (
              <label key={p.name} className="block">
                <span className="mb-1 block text-xs font-semibold uppercase tracking-wide text-ink-muted">
                  {p.name} (query{p.required ? ", required" : ""})
                </span>
                <input
                  className="w-full rounded-md border border-ink/20 bg-surface px-3 py-1.5 text-sm"
                  value={queryParams[p.name] ?? ""}
                  onChange={(e) => setQueryParams((prev) => ({ ...prev, [p.name]: e.target.value }))}
                />
              </label>
            ))}

            {selected.requestBodyExample !== null && (
              <label className="block">
                <span className="mb-1 block text-xs font-semibold uppercase tracking-wide text-ink-muted">JSON body</span>
                <textarea
                  className="h-32 w-full rounded-md border border-ink/20 bg-surface p-2 font-mono text-xs"
                  value={body}
                  onChange={(e) => setBody(e.target.value)}
                />
              </label>
            )}

            <button
              onClick={runRequest}
              disabled={sending}
              className="flex items-center gap-2 rounded-md bg-indigo px-4 py-2 text-sm font-semibold text-white disabled:opacity-50"
            >
              <Send size={14} /> {sending ? "Sending..." : "Send"}
            </button>

            {result && (
              <div>
                <p className={`mb-1 text-xs font-semibold ${result.ok ? "text-sage" : "text-red-muted"}`}>
                  Status: {result.status}
                </p>
                <pre className="max-h-96 overflow-auto rounded-md bg-ink/5 p-3 text-xs">
                  {JSON.stringify(result.data, null, 2)}
                </pre>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
