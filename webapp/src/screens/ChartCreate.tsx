import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Sparkles, MapPin, Clock, AlertCircle, CheckCircle2 } from "lucide-react";
import { api, type NewChartRequest, type NewChartResult } from "../lib/api";

const AYANAMSHAS = ["lahiri"];
const NODE_TYPES = ["mean", "true"];
const HOUSE_SYSTEMS = ["whole_sign"];

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <label className="block">
      <span className="mb-1 block text-xs font-semibold uppercase tracking-wide text-ink-muted">{label}</span>
      {children}
    </label>
  );
}

const inputClass =
  "w-full rounded-md border border-ink/20 bg-surface px-3 py-2 text-sm focus:border-indigo focus:outline-none focus:ring-1 focus:ring-indigo";

/**
 * New Horoscope -- Phase 8 workbench ask: generate a chart directly from
 * DOB/TOB/lat/lon, matching AGENTS.md Step 0's Input Lock exactly (name,
 * dob, tob, utc_offset, lat, lon are the only mandatory fields; everything
 * else has a sane classical default the user can override).
 */
export function ChartCreate({ onCreated }: { onCreated: (chartId: string) => void }) {
  const queryClient = useQueryClient();
  const [form, setForm] = useState<NewChartRequest>({
    name: "",
    dob: "",
    tob: "",
    utc_offset: 5.5,
    latitude: 0,
    longitude: 0,
    place: "",
    ayanamsha: "lahiri",
    node_type: "mean",
    house_system: "whole_sign",
  });

  const mutation = useMutation<NewChartResult, Error, NewChartRequest>({
    mutationFn: (body) => api.createChart(body),
    onSuccess: (result) => {
      queryClient.invalidateQueries({ queryKey: ["charts"] });
      onCreated(result.chart_id);
    },
  });

  const set = <K extends keyof NewChartRequest>(key: K, value: NewChartRequest[K]) =>
    setForm((f) => ({ ...f, [key]: value }));

  const canSubmit = form.name.trim() && form.dob && form.tob;

  return (
    <div className="mx-auto max-w-2xl">
      <div className="mb-5 flex items-center gap-2">
        <Sparkles size={18} className="text-gold" aria-hidden="true" />
        <h2 className="text-xl font-semibold font-scripture text-indigo">Generate a New Horoscope</h2>
      </div>
      <p className="mb-6 text-sm text-ink-muted">
        Input Lock (AGENTS.md Step 0): name, birth date, birth time, UTC offset, latitude, and
        longitude are required before any computation happens. Nothing here is guessed.
      </p>

      <form
        className="space-y-4 rounded-xl border border-ink/10 bg-surface p-6 shadow-sm"
        onSubmit={(e) => {
          e.preventDefault();
          mutation.mutate(form);
        }}
      >
        <Field label="Full name *">
          <input
            className={inputClass}
            value={form.name}
            onChange={(e) => set("name", e.target.value)}
            placeholder="e.g. Bandlapalli Ajay Kumar"
            required
          />
        </Field>

        <div className="grid grid-cols-2 gap-4">
          <Field label="Date of birth *">
            <input
              type="date"
              className={inputClass}
              value={form.dob}
              onChange={(e) => set("dob", e.target.value)}
              required
            />
          </Field>
          <Field label="Time of birth (local) *">
            <div className="relative">
              <Clock size={14} className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-ink-muted" />
              <input
                type="time"
                step={1}
                className={`${inputClass} pl-8`}
                value={form.tob}
                onChange={(e) => set("tob", e.target.value)}
                required
              />
            </div>
          </Field>
        </div>

        <div className="grid grid-cols-3 gap-4">
          <Field label="UTC offset (hrs) *">
            <input
              type="number"
              step={0.25}
              className={inputClass}
              value={form.utc_offset}
              onChange={(e) => set("utc_offset", Number(e.target.value))}
              required
            />
          </Field>
          <Field label="Latitude *">
            <input
              type="number"
              step={0.0001}
              className={inputClass}
              value={form.latitude}
              onChange={(e) => set("latitude", Number(e.target.value))}
              required
            />
          </Field>
          <Field label="Longitude *">
            <input
              type="number"
              step={0.0001}
              className={inputClass}
              value={form.longitude}
              onChange={(e) => set("longitude", Number(e.target.value))}
              required
            />
          </Field>
        </div>

        <Field label="Birthplace (optional, label only)">
          <div className="relative">
            <MapPin size={14} className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-ink-muted" />
            <input
              className={`${inputClass} pl-8`}
              value={form.place}
              onChange={(e) => set("place", e.target.value)}
              placeholder="e.g. Hyderabad, Telangana"
            />
          </div>
        </Field>

        <div className="grid grid-cols-3 gap-4 border-t border-ink/10 pt-4">
          <Field label="Ayanamsha">
            <select className={inputClass} value={form.ayanamsha} onChange={(e) => set("ayanamsha", e.target.value)}>
              {AYANAMSHAS.map((a) => (
                <option key={a} value={a}>{a}</option>
              ))}
            </select>
          </Field>
          <Field label="Node type">
            <select className={inputClass} value={form.node_type} onChange={(e) => set("node_type", e.target.value)}>
              {NODE_TYPES.map((n) => (
                <option key={n} value={n}>{n}</option>
              ))}
            </select>
          </Field>
          <Field label="House system">
            <select
              className={inputClass}
              value={form.house_system}
              onChange={(e) => set("house_system", e.target.value)}
            >
              {HOUSE_SYSTEMS.map((h) => (
                <option key={h} value={h}>{h.replace("_", " ")}</option>
              ))}
            </select>
          </Field>
        </div>

        {mutation.isError && (
          <div className="flex items-start gap-2 rounded-md border border-red-muted/30 bg-red-muted/5 p-3 text-sm text-red-muted">
            <AlertCircle size={16} className="mt-0.5 shrink-0" />
            <span>{mutation.error.message}</span>
          </div>
        )}

        {mutation.isSuccess && (
          <div className="flex items-start gap-2 rounded-md border border-sage/30 bg-sage/5 p-3 text-sm text-sage">
            <CheckCircle2 size={16} className="mt-0.5 shrink-0" />
            <span>
              Chart <b>{mutation.data.chart_id}</b> created and ingested into the DB. Lagna sign:{" "}
              {mutation.data.lagna_sign}. Switch to Chart Workbench or Validate to explore it.
            </span>
          </div>
        )}

        <button
          type="submit"
          disabled={!canSubmit || mutation.isPending}
          className="w-full rounded-md bg-indigo px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition-colors hover:bg-indigo/90 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {mutation.isPending ? "Computing chart..." : "Generate horoscope"}
        </button>
      </form>
    </div>
  );
}
