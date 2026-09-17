/**
 * Thin fetch wrapper against the Workbench API v2 (FastAPI).
 * Per architecture.md: the frontend NEVER computes Jyotisha logic itself --
 * every value shown in the UI must come from this layer, untouched.
 */
const BASE = "/api/v2";

async function getJSON<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`);
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`API ${path} failed: ${res.status} ${text}`);
  }
  return res.json() as Promise<T>;
}

async function postJSON<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`API ${path} failed: ${res.status} ${text}`);
  }
  return res.json() as Promise<T>;
}

export interface ChartSummary {
  id: string;
  name: string;
  dob: string;
  tob: string;
  ayanamsha: string;
  node_type: string;
  house_system: string;
}

export interface PlanetPosition {
  longitude: number;
  sign: number;
  deg_in_sign: number;
  house: number;
  retrograde: boolean;
  speed: number;
}

export interface VargaPlanet {
  sign: number;
  deg_in_sign: number;
  house: number;
  state: string;
  sign_en: string;
  sign_tel: string;
  sign_lord: string;
  retrograde: boolean;
}

export interface VargaChart {
  varga: number;
  name: string;
  significance: string;
  citation_status: string;
  lagna_sign: number;
  lagna_sign_en: string;
  lagna_sign_tel: string;
  planets: Record<string, VargaPlanet>;
  vargottama: string[];
  birth_time_sensitivity_warning?: boolean;
  warning_note?: string;
}

export interface ChartDetail {
  chart_id: string;
  settings: { ayanamsha: string; node_type: string; house_system: string };
  d1: Record<string, PlanetPosition>;
  vargas: Record<string, VargaChart>;
  dashas: Array<{ planet: string; years: number; start: string; end: string }>;
  current_dasha: {
    mahadasha?: { planet: string; start: string; end: string };
    antardasha?: { planet: string; start: string; end: string };
    pratyantardasha?: { planet: string; start: string; end: string };
    all_antars?: Array<{ planet: string; start: string; end: string }>;
    all_pratyantaras?: Array<{ planet: string; start: string; end: string }>;
  };
  transits: Record<string, unknown>;
  house_lords: Record<string, string>;
  yoga_karakas: string[];
}

export interface RuleEvaluation {
  rule_id: string;
  title: string;
  matched: boolean;
  chart_evidence: Record<string, unknown>;
  outputs: Array<{ kind: string; payload: Record<string, unknown> }>;
  confidence: "high" | "medium" | "low";
  source_tier: number;
  status: string;
  quality: "computed" | "computed_simplified" | "computed_with_conflict" | "data_gap";
}

export interface ValidationScreenData {
  chart_id: string;
  checks: Record<string, unknown>;
  warnings: string[];
}

export interface HouseTheme {
  house: number;
  name_en: string;
  name_tel: string;
  karakas: string[];
  nature: "trikona" | "kendra" | "dusthana" | "upachaya" | "neutral";
  is_maraka_house: boolean;
  core: string;
  material: string;
  higher: string;
}

export interface NaturalRelationships {
  table: Record<string, { friends: string[]; neutral: string[]; enemies: string[] }>;
  source: string;
  citation_status: string;
}

export interface DignityEntry {
  exalted_sign: string;
  exalted_degree: number;
  debilitated_sign: string;
  own_signs: string[];
  moolatrikona_sign: string;
  moolatrikona_range_deg: [number, number];
  moolatrikona_citation_status: string;
}

export interface FunctionalNatureCell {
  houses_owned: number[];
  tag: string;
  classification: string;
  is_lagna_lord: boolean;
  is_yoga_karaka: boolean;
  natural_nature: "benefic" | "malefic";
}

export interface FunctionalNatureGrid {
  grid: Record<string, { lagna_sign_en: string; planets: Record<string, FunctionalNatureCell> }>;
  legend: Record<string, string>;
  disclaimer: string;
}

export interface LordPlacementConnections {
  lagna_sign: number;
  lagna_sign_en: string;
  matrix: Record<string, { lord: string; destinations: Record<string, { connection: string; dest_nature: string }> }>;
  note: string;
}

export interface PlanetLabProfile {
  sign_en: string;
  deg_in_sign: number;
  house: number;
  retrograde: boolean;
  functional: FunctionalNatureCell;
  combust: boolean;
  combustion_orb_deg: number | null;
  d9_sign_en: string;
  d9_state: string;
  vargottama: boolean;
  shadbala: {
    components: Record<string, number>;
    total_score: number;
    verdict: string;
  };
  ishta_kashta: { ishta: number; kashta: number; verdict: string };
  aspected_by: string[];
}

export interface PlanetLabData {
  chart_id: string;
  lagna_sign: number;
  planets: Record<string, PlanetLabProfile>;
}

export interface DoshaResult {
  present: boolean;
  citation: string;
  [key: string]: unknown;
}

export interface DoshasData {
  chart_id: string;
  doshas: Record<string, DoshaResult>;
  sade_sati: unknown;
}

export interface CheatsheetClaim {
  claim_id: string;
  source_file: string;
  section: string;
  claim_text: string;
  formula_ref: string | null;
  applies_to_chart: string | null;
  claim_type: string;
}

export interface CheatsheetResult {
  claim: CheatsheetClaim;
  computed_value: unknown;
  verdict: "match" | "mismatch" | "unverifiable" | "data_gap";
  diff_detail: string;
}

export interface CheatsheetClaimsResponse {
  total_claims: number;
  verdict_counts: Record<string, number>;
  results: CheatsheetResult[];
}

export interface ConceptEntry {
  concept_id: string;
  category: string;
  sanskrit_term: string | null;
  english_gloss: string;
  classical_definition: string;
  primary_citation: string;
  code_ref: string | null;
  quality_label: "computed" | "computed_simplified" | "computed_with_conflict" | "data_gap";
  caveats: string[];
  cross_check_note: string;
}

export interface ConceptsResponse {
  categories: string[];
  total_concepts: number;
  concepts: ConceptEntry[];
}

export interface CaseQAEntry {
  id: number;
  chart_id: string;
  question: string;
  answer: string;
  source_refs: string;
  asked_at: string;
}

export interface CaseSummary {
  chart: Record<string, unknown> | null;
  planets: Array<Record<string, unknown>>;
  dashas: Array<Record<string, unknown>>;
  doshas: Array<Record<string, unknown>>;
  yogas: Array<Record<string, unknown>>;
  remedies: Array<Record<string, unknown>>;
}

export interface DashaAntardashaRow {
  planet: string;
  years: number;
  months: number;
}

export interface DashaPratyantardashaRow {
  planet: string;
  years: number;
  days: number;
}

export interface DashaReference {
  sequence: Array<{ planet: string; years: number }>;
  total_years: number;
  antardasha_tables: Record<string, DashaAntardashaRow[]>;
  pratyantardasha_tables: Record<string, Record<string, DashaPratyantardashaRow[]>>;
  pratyantardasha_formula: string;
  citation: string;
  note: string;
}

export interface TransitHouseEffect {
  quality: string;
  effect: string;
}

export interface TransitReference {
  jupiter_from_moon: Record<string, TransitHouseEffect>;
  saturn_from_moon: Record<string, TransitHouseEffect>;
  sade_sati_phases: Array<{ phase: number; label: string; house_from_moon: number; duration_years: number }>;
  citation: string;
}

export interface RuleCitation {
  text: string;
  chapter?: number;
  sloka_range?: string;
  translation_snippet?: string;
}

export interface TopRule {
  rule_id: string;
  priority: number | null;
  name: string;
  authority_tier: string;
  chapter_signal: string;
  domain_tags: string[];
  why_it_matters: string;
  canonical_statement: string;
  activation_conditions: string[];
  exclusions: string[];
  examples: string[];
  citations: RuleCitation[];
  citation_status: string;
}

export interface TopRulesResponse {
  total_rules: number;
  target_total: number;
  coverage_note: string;
  rules: TopRule[];
  by_domain: Record<string, string[]>;
}

export interface PlanetGraphNode {
  id: string;
  label: string;
}

export interface PlanetGraphEdge {
  source: string;
  target: string;
  kind: "friend" | "enemy";
}

export interface PlanetRelationshipGraph {
  nodes: PlanetGraphNode[];
  edges: PlanetGraphEdge[];
}

export interface SandboxPlanetPlacement {
  sign: number;
  degree: number;
  retrograde: boolean;
}

export interface SandboxRequestBody {
  lagna_sign: number;
  lagna_degree: number;
  planets: Record<string, SandboxPlanetPlacement>;
  day_or_night: "day" | "night";
}

export interface SandboxHouseObservation {
  lord: string;
  theme: { core: string; material: string; higher: string };
  occupants: string[];
  aspected_by: string[];
}

export interface SandboxPlanetObservation {
  sign: number;
  sign_en: string;
  degree: number;
  house: number;
  retrograde: boolean;
  dignity: string;
  territory: string;
  d9_sign_en: string;
  d9_state: string;
  vargottama: boolean;
  aspects_houses: number[];
  functional?: FunctionalNatureCell;
  combust?: boolean;
  shadbala?: { components: Record<string, number>; total_score: number; verdict: string };
  varga_quality?: { vargottama: boolean; d9_state: string; score: number };
  ishta_kashta?: { ishta: number; kashta: number; verdict: string };
}

export interface SandboxHouseConnection {
  lord: string;
  lord_house: number;
  connection: string;
  dest_nature: string;
  is_self_placed: boolean;
}

export interface SandboxAnalysis {
  lagna_sign: number;
  lagna_sign_en: string;
  houses: Record<string, SandboxHouseObservation>;
  house_connections: Record<string, SandboxHouseConnection>;
  planets: Record<string, SandboxPlanetObservation>;
  maraka_lords: Record<string, string>;
  yoga_karakas: string[];
  doshas: Record<string, DoshaResult>;
  yogas: Array<{ name: string; effect: string; tel: string; strength: string }>;
  data_gaps: string[];
}

export interface DashaPeriod {
  planet: string;
  years: number;
  start: string;
  end: string;
}

export interface DashaCurrent {
  mahadasha?: DashaPeriod;
  antardasha?: DashaPeriod;
  pratyantardasha?: DashaPeriod;
  all_antars?: DashaPeriod[];
  all_pratyantaras?: DashaPeriod[];
}

export type SandboxDashaResponse =
  | { mode: "manual_required"; reason: string }
  | {
      mode: "computed";
      birth_date: string;
      as_of_date: string;
      mahadashas: DashaPeriod[];
      current: DashaCurrent;
      data_gap: string;
    };

export interface SandboxDashaRequestBody {
  moon_sign: number;
  moon_degree: number;
  birth_date?: string | null;
  as_of_date?: string | null;
}

export interface TransitNatalContact {
  natal_planet: string;
  kind: "conjunction" | "aspect";
  house: number;
  orb_deg: number | null;
}

export interface TransitPlanet {
  longitude: number;
  sign: number;
  sign_en: string;
  deg_in_sign: number;
  retrograde: boolean;
  speed: number;
  house_from_lagna: number;
  house_from_moon: number;
  aspects_houses: number[];
  natal_contacts: TransitNatalContact[];
  dignity?: string;
}

export interface SandboxTransitResponse {
  date: string;
  planets: Record<string, TransitPlanet>;
}

export interface NatalPointerBody {
  sign: number;
  degree: number;
}

export interface SandboxTransitRequestBody {
  on_date: string;
  lagna_sign: number;
  moon_sign: number;
  natal_planets?: Record<string, NatalPointerBody>;
}

// ---------------------------------------------------------------------
// Phase 8 workbench-catchup additions: chart creation, rule-pack browser,
// DB browser, coverage/full-context, and a generic OpenAPI-driven API
// console invoker.
// ---------------------------------------------------------------------

export interface NewChartRequest {
  name: string;
  dob: string;
  tob: string;
  utc_offset: number;
  latitude: number;
  longitude: number;
  place?: string;
  ayanamsha?: string;
  node_type?: string;
  house_system?: string;
  notes?: string[];
}

export interface NewChartResult {
  chart_id: string;
  fixture_path: string;
  lagna_sign: number;
  current_dasha: ChartDetail["current_dasha"];
  ingested: Record<string, number>;
}

export interface CoverageData {
  chart_id: string;
  rule_coverage_pct: number;
  evidence_traceability_pct: number;
  unsupported_claim_count: number;
  contradictions: string[];
  total_rules_evaluated: number;
  total_matched: number;
}

// FullContext is deliberately loose (Record<string, unknown> per section) --
// it mirrors build_chart_context()'s full output, which is large and
// evolves as new derived layers are added. Sections consumed with a fixed
// shape (doshas, yogas) reuse their existing typed interfaces where
// convenient at the call site.
export type FullContext = Record<string, unknown> & { chart_id: string };

export interface RulePackSummary {
  pack_id: string;
  kind: "v2_generic" | "v1_legacy";
  file: string;
  rule_count: number;
  categories: string[];
  status_counts: Record<string, number>;
  size_bytes: number;
  note?: string;
  error?: string;
}

export interface RulePackListResponse {
  packs: RulePackSummary[];
  count: number;
}

export interface RulePackRule {
  id: string;
  title: string;
  category: string;
  source_tier: number;
  source_ref: string;
  tradition: string;
  conditions: Array<{ path: string; op: string; value: unknown; description?: string }>;
  outputs: Array<{ kind: string; payload: Record<string, unknown> }>;
  confidence: string;
  status: string;
  contradictions: string[];
  notes: string[];
  computation_model: string;
}

export interface RulePackDetail {
  pack_id: string;
  rule_count: number;
  rules: RulePackRule[];
}

export interface DbTableInfo {
  name: string;
  columns: string[];
  row_count: number;
}

export interface DbTablesResponse {
  tables: DbTableInfo[];
  count: number;
  database_url: string;
}

export interface DbTableRowsResponse {
  table: string;
  columns: string[];
  total_rows: number;
  limit: number;
  offset: number;
  rows: Array<Record<string, unknown>>;
}

export interface OpenApiOperation {
  path: string;
  method: string;
  summary: string;
  parameters: Array<{ name: string; in: string; required: boolean; schema?: { type?: string } }>;
  requestBodyExample: string | null;
  tags: string[];
}

/** Fetch the raw OpenAPI schema FastAPI already generates for free, and
 * flatten it into a simple operation list scoped to /api/v2/* -- this is
 * what powers the API Console tab ("trigger every V2 API") without
 * hand-maintaining a parallel endpoint registry (DRY: the schema IS the
 * registry). */
export async function getApiV2Operations(): Promise<OpenApiOperation[]> {
  const res = await fetch("/openapi.json");
  if (!res.ok) throw new Error(`openapi.json failed: ${res.status}`);
  const spec = await res.json();
  const ops: OpenApiOperation[] = [];
  for (const [path, methods] of Object.entries<Record<string, unknown>>(spec.paths ?? {})) {
    if (!path.startsWith("/api/v2")) continue;
    for (const [method, opRaw] of Object.entries(methods)) {
      if (!["get", "post", "put", "delete", "patch"].includes(method)) continue;
      const op = opRaw as Record<string, unknown>;
      let requestBodyExample: string | null = null;
      const requestBody = op.requestBody as Record<string, unknown> | undefined;
      if (requestBody) {
        const content = requestBody.content as Record<string, unknown> | undefined;
        const schemaRef = (content?.["application/json"] as Record<string, unknown> | undefined)?.schema as
          | Record<string, unknown>
          | undefined;
        requestBodyExample = schemaRef ? JSON.stringify(schemaRef, null, 2) : "{}";
      }
      ops.push({
        path,
        method: method.toUpperCase(),
        summary: (op.summary as string) || (op.operationId as string) || path,
        parameters: (op.parameters as OpenApiOperation["parameters"]) ?? [],
        requestBodyExample,
        tags: (op.tags as string[]) ?? [],
      });
    }
  }
  return ops.sort((a, b) => a.path.localeCompare(b.path) || a.method.localeCompare(b.method));
}

/** Execute an arbitrary API v2 call built by the API Console -- `path`
 * already has placeholders substituted by the caller. Returns the raw
 * response body (parsed JSON) plus status, so the console can show
 * failures honestly instead of swallowing them. */
export async function invokeApiConsole(
  method: string,
  path: string,
  body?: string,
): Promise<{ status: number; ok: boolean; data: unknown }> {
  const res = await fetch(path, {
    method,
    headers: body ? { "Content-Type": "application/json" } : undefined,
    body: body || undefined,
  });
  const text = await res.text();
  let data: unknown = text;
  try {
    data = text ? JSON.parse(text) : null;
  } catch {
    // leave as raw text
  }
  return { status: res.status, ok: res.ok, data };
}

export interface CaseListItem {
  id: string;
  name: string;
  dob: string;
  tob: string;
  utc_offset: number;
  latitude: number;
  longitude: number;
  ayanamsha: string;
  node_type: string;
  house_system: string;
  created_at: string;
  notes: string;
}

export interface TodayTransitPlanet {
  longitude: number;
  sign: number;
  sign_en: string;
  deg_in_sign: number;
  retrograde: boolean;
  speed: number;
  nakshatra: string;
  pada: number;
}

export interface TodayTransitsResponse {
  date: string;
  utc_offset: number;
  node_type: string;
  planets: Record<string, TodayTransitPlanet>;
}

export interface TodayPanchangaResponse {
  date: string;
  utc_offset: number;
  model: string;
  vara: { number: number; name: string; lord: string; day_boundary: string };
  tithi: { number: number; paksha: string; name: string; percentage_complete: number };
  nakshatra: { number: number; name: string; lord: string; pada: number; percentage_complete: number };
  yoga: { number: number; name: string; percentage_complete: number };
  karana: { number: number; name: string; percentage_complete: number };
}

// ---------------------------------------------------------------------
// Marriage Compatibility screen (build_plan.md Phase 8 follow-up -- the
// one item Phase 8's own note left explicitly undone). Kept loosely typed
// (Record<string, unknown>) for the deeper/faster-evolving sub-sections,
// same disclosed trade-off convention as FullContext above -- concrete
// fields are typed only where the screen actually renders them.
// ---------------------------------------------------------------------
export interface KutaResult {
  raw_score: number;
  effective_score: number;
  max_score: number;
  citation: string;
  [key: string]: unknown;
}

export interface MangalDoshaMatch {
  groom: Record<string, unknown>;
  bride: Record<string, unknown>;
  both_manglik: boolean;
  verdict: string;
  citation: string;
}

export interface AshtakutaReport {
  kutas: Record<string, KutaResult>;
  raw_total: number;
  effective_total: number;
  max_total: number;
  interpretation: string;
  mangal_dosha: MangalDoshaMatch;
  citation: string;
}

export interface MarriageTimingWindow {
  mahadasha: string;
  antardasha: string;
  start: string;
  end: string;
  agreements: string[];
  agreement_count: number;
  verdict: "possible" | "confirmed" | "certain";
  probability_percent: number;
  reason: string;
  best_rank_label: string;
}

export interface MarriageTimingReport {
  significators: Record<string, unknown>;
  upcoming_windows: MarriageTimingWindow[];
  combined_windows: MarriageTimingWindow[];
  probability_model: string;
  probability_caveat: string;
  citation: string;
}

export interface MarriedLifeStatusItem {
  area: string;
  note: string;
  citation: string;
}

export interface MarriedLifeStatus {
  strengths: MarriedLifeStatusItem[];
  cautions: MarriedLifeStatusItem[];
  five_pillar_summary: Record<string, unknown>;
  active_doshas: Record<string, unknown>;
  current_dasha: { mahadasha: string | null; antardasha: string | null };
  sade_sati: Record<string, unknown> | null;
  citation: string;
}

export interface MarriageCompatibilityPerson {
  chart_id: string;
  name: string;
  marriage_timing?: MarriageTimingReport;
  married_life_status?: MarriedLifeStatus;
}

export interface MarriageCompatibilityResponse {
  groom_chart_id: string;
  bride_chart_id: string;
  already_married: boolean;
  ashtakuta: AshtakutaReport;
  synastry: Record<string, unknown>;
  d9_cross_compatibility: Record<string, unknown>;
  groom: MarriageCompatibilityPerson;
  bride: MarriageCompatibilityPerson;
}

export const api = {
  listCharts: () => getJSON<{ charts: ChartSummary[]; count: number }>("/charts"),
  listCases: () => getJSON<{ cases: CaseListItem[]; count: number }>("/cases"),
  getTodayTransits: (onDate?: string) =>
    getJSON<TodayTransitsResponse>(`/today/transits${onDate ? `?on_date=${onDate}` : ""}`),
  getTodayPanchanga: (onDate?: string) =>
    getJSON<TodayPanchangaResponse>(`/today/panchanga${onDate ? `?on_date=${onDate}` : ""}`),
  getChart: (chartId: string) => getJSON<ChartDetail>(`/charts/${chartId}`),
  getVarga: (chartId: string, n: number) => getJSON<VargaChart>(`/charts/${chartId}/vargas/${n}`),
  getRules: (chartId: string) =>
    getJSON<{ chart_id: string; engine: string; evaluations: RuleEvaluation[] }>(
      `/charts/${chartId}/rules`,
    ),
  getValidationScreen: (chartId: string) =>
    getJSON<ValidationScreenData>(`/charts/${chartId}/validation-screen`),
  getHouseThemes: () => getJSON<{ houses: Record<string, HouseTheme> }>("/reference/house-themes"),
  getNaturalRelationships: () => getJSON<NaturalRelationships>("/reference/natural-relationships"),
  getDignityTable: () => getJSON<{ dignity: Record<string, DignityEntry> }>("/reference/dignity-table"),
  getFunctionalNatureGrid: () => getJSON<FunctionalNatureGrid>("/reference/functional-nature-grid"),
  getLordPlacementConnections: (lagnaSign: number) =>
    getJSON<LordPlacementConnections>(`/reference/lord-placement-connections/${lagnaSign}`),
  getPlanetLab: (chartId: string) => getJSON<PlanetLabData>(`/charts/${chartId}/planet-lab`),
  getDoshas: (chartId: string) => getJSON<DoshasData>(`/charts/${chartId}/doshas`),
  getCheatsheetClaims: (verdict?: string) =>
    getJSON<CheatsheetClaimsResponse>(`/cheatsheet/claims${verdict ? `?verdict=${verdict}` : ""}`),
  getDashaReference: () => getJSON<DashaReference>("/reference/dasha-system"),
  getTransitReference: () => getJSON<TransitReference>("/reference/transit-impacts"),
  getTopRules: () => getJSON<TopRulesResponse>("/reference/top-rules"),
  getPlanetRelationshipGraph: () => getJSON<PlanetRelationshipGraph>("/reference/planet-relationship-graph"),
  analyzeSandbox: (body: SandboxRequestBody) => postJSON<SandboxAnalysis>("/sandbox/analyze", body),
  getSandboxDasha: (body: SandboxDashaRequestBody) => postJSON<SandboxDashaResponse>("/sandbox/dasha", body),
  getSandboxTransits: (body: SandboxTransitRequestBody) =>
    postJSON<SandboxTransitResponse>("/sandbox/transits", body),
  getCheatsheetConcepts: (category?: string) =>
    getJSON<ConceptsResponse>(`/cheatsheet/concepts${category ? `?category=${category}` : ""}`),
  getCaseSummary: (chartId: string) => getJSON<CaseSummary>(`/cases/${chartId}`),
  getCaseQA: (chartId: string, search?: string) =>
    getJSON<{ chart_id: string; qa: CaseQAEntry[]; count: number }>(
      `/cases/${chartId}/qa${search ? `?search=${encodeURIComponent(search)}` : ""}`,
    ),
  postCaseQA: (chartId: string, body: { question: string; answer: string; source_refs?: string }) =>
    postJSON<{ chart_id: string; qa_id: number; logged: boolean }>(`/cases/${chartId}/qa`, body),
  createChart: (body: NewChartRequest) => postJSON<NewChartResult>("/charts", body),
  getCoverage: (chartId: string) => getJSON<CoverageData>(`/charts/${chartId}/coverage`),
  getFullContext: (chartId: string) => getJSON<FullContext>(`/charts/${chartId}/full-context`),
  listRulePacks: () => getJSON<RulePackListResponse>("/rules/packs"),
  getRulePack: (packId: string, filters?: { category?: string; status?: string; search?: string }) => {
    const params = new URLSearchParams();
    if (filters?.category) params.set("category", filters.category);
    if (filters?.status) params.set("status", filters.status);
    if (filters?.search) params.set("search", filters.search);
    const qs = params.toString();
    return getJSON<RulePackDetail>(`/rules/packs/${packId}${qs ? `?${qs}` : ""}`);
  },
  listDbTables: () => getJSON<DbTablesResponse>("/db/tables"),
  getDbTableRows: (table: string, limit = 50, offset = 0) =>
    getJSON<DbTableRowsResponse>(`/db/tables/${table}/rows?limit=${limit}&offset=${offset}`),
  getMarriageCompatibility: (groomChartId: string, brideChartId: string, alreadyMarried: boolean) =>
    getJSON<MarriageCompatibilityResponse>(
      `/marriage-compatibility/${groomChartId}/${brideChartId}?already_married=${alreadyMarried}`,
    ),
};
