# 2. Feature & Architecture Comparison

## Scale

| Codebase | Language | Files | Lines (approx) | Test evidence |
|---|---|---|---|---|
| **Our `app/`** | Python | 40 | ~4,600 | `tests/run_suite.py` snapshot regression + 10 `tests/unit/*.py` modules |
| OpenJyotish `src/jhora/` | Python | ~180 | ~26,400 | claims "1153 tests" in README |
| PyJHora `src/jhora/` | Python | ~150 | ~119,300 | claims "~6800 tests" (`pvr_tests.py`), verified against PVR Narasimha Rao's book examples |
| VedAstro `Library/` | C# | ~120 | ~60,400 | separate `LibraryTests/` project (not exercised in this review — different runtime) |

Context: our codebase is deliberately narrow and self-labeling
(`computed`, `computed_simplified`, `data_gap` — see `AGENTS.md` §9). These
three projects are 5x-25x larger because they implement broad *desktop
software* surface (GUIs, muhurta electional timing, mundane astrology,
matchmaking pipelines, AI chat) that is out of scope for what we're
building. Line-count is not itself a quality signal here — it mostly
reflects "how much of Jyotiṣa's total surface area is covered."

## Direct mapping to our documented `data_gap` list

`AGENTS.md` §6 lists these as explicitly missing from our engine today:

> full classical Vimśopaka, full Śaḍbala in ṣaṣṭyāṁśa terms, full Iṣṭa/Kaṣṭa
> Phala, classical Argala with strength comparison, full Aṣṭakavarga,
> Bhāvapada family beyond A1/UL, D10/D7 derived interpretation layers,
> Pañcāṅga computation.

| Gap | Have it? | Where (reference only, not to be imported) |
|---|---|---|
| Full classical Vimśopaka Bala | OpenJyotish: yes | `calc/vimsopaka.py` (OpenJyotish). PyJHora does **not** have a dedicated Vimśopaka module — grep for `vimsopaka` across `PyJHora-main/src` returned zero hits despite the CLI-adjacent README claims for OpenJyotish's fork of the concept. |
| Full Śaḍbala | Both (simplified vs. full split unclear) | `calc/shadbala.py` (OpenJyotish, 19.1 KB), `horoscope/chart/strength.py` (PyJHora, has `Shadbala`-named functions). Neither was verified line-by-line for "true ṣaṣṭyāṁśa precision" in this review — treat as "worth reading," not "confirmed superior." |
| Full Iṣṭa/Kaṣṭa Phala | Partial | Not found as a dedicated module in either Python repo under an obvious name; likely folded into `strength.py`/`shadbala.py`. Needs a deeper read before relying on it even as reference. |
| Classical Argala (with strength comparison) | Not found | Grep for `argala` (case-insensitive) across all of PyJHora's `src/jhora` returned **zero matches**. Not confirmed in OpenJyotish's `calc/` file list either. This may be a genuine gap in all three, not just us. |
| Full Aṣṭakavarga (Bhinna + Sarva) | Yes, both | `horoscope/chart/ashtakavarga.py` (PyJHora), `calc/ashtakavarga.py` (OpenJyotish, 14.7 KB) |
| Bhāvapada family beyond A1/UL | Yes | `horoscope/chart/arudhas.py` (PyJHora) has `bhava_arudhas_from_planet_positions`, `bhava_arudha_longitudes`, `graha_arudhas` — i.e. the full Arūḍha Pada family (A1-A12) plus graha ārūḍhas, not just Upapada (A7/UL). `calc/arudha.py` in OpenJyotish is the refactored equivalent. |
| D10/D7 derived interpretation layers | Yes (generic) | Both support arbitrary varga generation (`divisional_chart(..., divisional_chart_factor=N)` in PyJHora; `varga` CLI command in OpenJyotish covers D-1 to D-150) — this is a computation layer, not an "interpretation" layer; interpretive text is still ours to write per `docs/interpretive-frameworks.md`. |
| Pañcāṅga computation | Yes, both | `panchanga/drik.py` (PyJHora — actually forked from the older standalone `drik-panchanga` project by Satish BD, itself AGPL) has `tithi`, `nakshatra`, `yogam`, `karana`, `vaara` — literally the exact gap flagged in `AGENTS.md`. OpenJyotish CLI: `jhora panchanga`. |
| Sahamas (36 classical) | Yes, both | `horoscope/chart/sphuta.py` (PyJHora) computes Tri/Chatur/Pancha/Prāṇa/Deha/Mṛtyu/Bīja/Kṣetra/Tithi/Yoga/Yogi/Avayogi Sphuṭas. OpenJyotish: `calc/sahama.py` (8.7 KB) + a dedicated `calc/sphuta.py` (2.6 KB). |
| Doṣa registry (Mangal/Kāla Sarpa/Pitṛ/Guru Chāṇḍāla/etc.) | Yes, both | `horoscope/chart/dosha.py` (PyJHora) matches our `docs/dosha-registry.md` doṣa list almost 1:1 — this is the module cross-checked in `03-validation-cross-checks.md`. |

**Reading:** every calculator on our documented gap list except Argala
exists in at least one of these two Python repos. That is useful
*confirmation the formulas are well-trodden ground* (good — it means our
eventual implementations have something to validate against), but it does
not change the license verdict in `01-license-and-legal.md`. Argala
appearing to be missing everywhere is itself a useful data point — it may
be a genuinely under-served classical technique worth extra care when we
build it, since less prior art exists to cross-check against.

## Architectural approach comparison

| Aspect | Ours (`app/`) | PyJHora | OpenJyotish | VedAstro |
|---|---|---|---|---|
| Ephemeris | pyswisseph (Python binding) | pyswisseph | pyswisseph | SwissEphNet (C# port) |
| Ayanamsha | Lahiri hardcoded at import (flagged as a gap to fix in `technical-architecture.md` §4.1) | Configurable, 20+ modes, defaults per `const._DEFAULT_AYANAMSA_MODE` | Configurable, "20 ayanamsa modes" per README | Configurable |
| Rule/interpretation layer | YAML rule packs + evaluator (currently hardcoded `if rid ==` chain — flagged for rewrite) | Prose/dict-based interpreter (`interpreter/` in OpenJyotish; `horoscope/prediction/` in PyJHora) | Same lineage as PyJHora, plus a full local-LLM RAG layer (`ai/`) | Same category, `Library/Logic/` |
| Persistence | None yet (planned SQLite, per `technical-architecture.md` §4.7) | SQLite (atlas + charts + knowledge, unified DB) | SQLite (same unified DB pattern) | Azure Table Storage |
| Test discipline | Snapshot regression (2 golden fixtures) + growing unit suite | ~6800 tests against book examples (strong, but book-example fixtures aren't visible/portable to us) | Claims 1153 tests | Separate `LibraryTests/` project |
| Interface | FastAPI + Jinja2 (+ new React/TS workbench planned) | PyQt6 desktop GUI, CLI via package import | CLI (Typer) + PyQt6 GUI + TUI + JSON API for AI agents | ASP.NET REST API + Blazor website + mobile |
| Deployment shape | Single Python service, our infra | Desktop app / library | Desktop app / library / self-hosted CLI | Full SaaS stack (their hosted website + self-host Docker option) |

**Takeaway:** none of the three are "an app we could stand up instead of
ours." OpenJyotish and VedAstro are full products (GUI/website + hosting
concerns we don't want to inherit); PyJHora is a library, but an AGPL one,
and its API shape (positional planet-index lists, global mutable
`const`/`drik` module state set via side-effecting functions like
`drik.set_ayanamsa_mode(...)`) does not match the explicit, parameter-
threaded, no-global-side-effects design direction already decided in
`technical-architecture.md` §4.1 ("Refactor to accept `ayanamsha`,
`node_type`... as explicit parameters... Never silently default"). Even
without the license problem, adopting PyJHora's API shape wholesale would
be a step backward from our own architecture decisions.
