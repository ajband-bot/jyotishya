import { useEffect, useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { api, type DashaPeriod } from "../../lib/api";
import { DASHA_ORDER, PLANET_COLOR } from "./layout";

export interface ActiveDasha {
  md: string | null;
  ad: string | null;
  pd: string | null;
}

function PeriodStrip({
  periods,
  activePlanet,
  cycleYears,
}: {
  periods: DashaPeriod[];
  activePlanet: string | null;
  cycleYears: number;
}) {
  return (
    <div className="flex h-6 w-full overflow-hidden rounded-md border border-ink/10">
      {periods.map((p) => (
        <div
          key={p.planet + p.start}
          title={`${p.planet}: ${p.start} to ${p.end} (${p.years}y)`}
          className={`flex items-center justify-center text-[9px] font-semibold text-white ${
            p.planet === activePlanet ? "ring-2 ring-inset ring-white" : "opacity-70"
          }`}
          style={{ background: PLANET_COLOR[p.planet], width: `${(p.years / cycleYears) * 100}%` }}
        >
          {p.planet === activePlanet ? p.planet.slice(0, 2) : ""}
        </div>
      ))}
    </div>
  );
}

/**
 * Vimsottari Dasha module (Chart Lab v2 Sprint 2, spec sections 4-6).
 * "Computed" mode needs a birth date to anchor a real BPHS Ch.46 calendar
 * for the hypothetical Moon position; "Manual" mode lets the user pick
 * MD/AD/PD directly without pretending to know any dates (spec section 18).
 */
export function DashaModule({
  moonSign,
  moonDegree,
  selectedDate,
  onActiveChange,
}: {
  moonSign: number;
  moonDegree: number;
  selectedDate: string;
  onActiveChange: (active: ActiveDasha) => void;
}) {
  const [mode, setMode] = useState<"computed" | "manual">("manual");
  const [birthDate, setBirthDate] = useState("");
  const [manualMd, setManualMd] = useState("Rahu");
  const [manualAd, setManualAd] = useState("Moon");
  const [manualPd, setManualPd] = useState("Saturn");

  const { data, isFetching } = useQuery({
    queryKey: ["sandbox-dasha", moonSign, moonDegree, birthDate, selectedDate],
    queryFn: () =>
      api.getSandboxDasha({
        moon_sign: moonSign,
        moon_degree: moonDegree,
        birth_date: birthDate,
        as_of_date: selectedDate,
      }),
    enabled: mode === "computed" && !!birthDate,
  });

  const active: ActiveDasha = useMemo(() => {
    if (mode === "manual") return { md: manualMd, ad: manualAd, pd: manualPd };
    if (data && data.mode === "computed") {
      return {
        md: data.current.mahadasha?.planet ?? null,
        ad: data.current.antardasha?.planet ?? null,
        pd: data.current.pratyantardasha?.planet ?? null,
      };
    }
    return { md: null, ad: null, pd: null };
  }, [mode, manualMd, manualAd, manualPd, data]);

  useEffect(() => onActiveChange(active), [active, onActiveChange]);

  return (
    <div className="rounded-lg border border-ink/10 bg-surface p-3">
      <div className="flex items-center justify-between mb-2">
        <p className="text-sm font-semibold">Vimśottarī Daśā</p>
        <div className="flex gap-1">
          {(["manual", "computed"] as const).map((m) => (
            <button
              key={m}
              onClick={() => setMode(m)}
              className={`text-[10px] px-2 py-1 rounded-md capitalize ${
                mode === m ? "bg-indigo text-white" : "bg-ink/5 text-ink-muted"
              }`}
            >
              {m === "manual" ? "Manual MD/AD/PD" : "Calculate from birth date"}
            </button>
          ))}
        </div>
      </div>

      {mode === "manual" ? (
        <div className="grid grid-cols-3 gap-2 text-xs">
          {[
            { label: "MD", value: manualMd, set: setManualMd },
            { label: "AD", value: manualAd, set: setManualAd },
            { label: "PD", value: manualPd, set: setManualPd },
          ].map(({ label, value, set }) => (
            <label key={label} className="flex flex-col gap-1">
              <span className="text-ink-muted">{label}</span>
              <select
                value={value}
                onChange={(e) => set(e.target.value)}
                className="rounded-md border border-ink/20 px-1.5 py-1"
              >
                {DASHA_ORDER.map((p) => (
                  <option key={p} value={p}>
                    {p}
                  </option>
                ))}
              </select>
            </label>
          ))}
        </div>
      ) : (
        <div>
          <label className="text-xs text-ink-muted">
            Birth date (anchors a real calendar for this hypothetical Moon position):
          </label>
          <input
            type="date"
            value={birthDate}
            onChange={(e) => setBirthDate(e.target.value)}
            className="ml-2 rounded-md border border-ink/20 px-2 py-1 text-xs"
          />
          {!birthDate && (
            <p className="text-[11px] text-amber mt-2">Pick a birth date to compute a real MD/AD/PD chain.</p>
          )}
          {isFetching && <p className="text-[11px] text-ink-muted mt-2">Computing...</p>}
          {data && data.mode === "computed" && (
            <div className="mt-2 space-y-2">
              <p className="text-[10px] text-ink-muted italic">{data.data_gap}</p>
              <p className="text-xs">
                MD: <b>{data.current.mahadasha?.planet ?? "?"}</b> · AD:{" "}
                <b>{data.current.antardasha?.planet ?? "?"}</b> · PD:{" "}
                <b>{data.current.pratyantardasha?.planet ?? "?"}</b>
              </p>
              <PeriodStrip periods={data.mahadashas} activePlanet={data.current.mahadasha?.planet ?? null} cycleYears={120} />
              {data.current.all_antars && (
                <PeriodStrip
                  periods={data.current.all_antars}
                  activePlanet={data.current.antardasha?.planet ?? null}
                  cycleYears={data.current.mahadasha?.years ?? 1}
                />
              )}
              {data.current.all_pratyantaras && data.current.all_pratyantaras.length > 0 && (
                <PeriodStrip
                  periods={data.current.all_pratyantaras}
                  activePlanet={data.current.pratyantardasha?.planet ?? null}
                  cycleYears={data.current.antardasha?.years ?? 1}
                />
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
