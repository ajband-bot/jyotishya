/**
 * Chart Lab v2 -- shared "Selected Analysis Date" (spec section 3). Drives
 * both the Dasha module (which MD/AD/PD is active) and the Transit module
 * (real Swiss Ephemeris positions for that date) from one control.
 */
export function TimeController({
  selectedDate,
  onChange,
}: {
  selectedDate: string;
  onChange: (iso: string) => void;
}) {
  const today = new Date().toISOString().slice(0, 10);
  return (
    <div className="flex items-center gap-2 rounded-lg border border-ink/10 bg-surface px-3 py-2">
      <span className="text-xs font-semibold text-ink-muted">Analysis date:</span>
      <input
        type="date"
        value={selectedDate}
        onChange={(e) => onChange(e.target.value)}
        className="rounded-md border border-ink/20 px-2 py-1 text-xs"
      />
      <button
        onClick={() => onChange(today)}
        disabled={selectedDate === today}
        className="text-[11px] rounded-md bg-indigo/10 text-indigo px-2 py-1 font-medium disabled:opacity-40"
      >
        Today
      </button>
    </div>
  );
}
