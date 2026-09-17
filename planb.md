---
status: analysis
updated: 2026-09-16
purpose: Direct answer to "if I use the public repos (OpenJyotish, PyJHora, VedAstro) directly, with only light LLM help, will predictions be more accurate, faster, and more controllable than our current app?" — and what that alternative would actually look like if chosen.
companion_to: build_plan.md (the recommended path — this file is the alternative it was weighed against)
---

# Plan B — Using the public repos directly instead of building our own

## The short answer

**Split by layer, because the honest answer isn't the same for both halves
of "predictions":**

| Layer | Would Plan B beat our current app? | Why |
|---|---|---|
| **Chart accounting** (planet positions, D1-D60 vargas, panchanga, dashas, doshas, yogas-as-detected-flags, Ashtakavarga, transits) | **Yes, immediately, on both accuracy and speed.** | These repos are 5-25x larger, tested against a published book's worked examples (PyJHora: ~6800 tests against P.V.R. Narasimha Rao's book; OpenJyotish: 1153+ tests, plus its own third-party cross-check against an independent library). Our app covers a narrower slice today (D1+D9 only, ~5 compiled v2 rules, no marriage compatibility, thin aspect logic). For pure computation, adopting one of these directly would out-perform our current app on day one. |
| **Narrative synthesis / "predictions" in the sense your readings deliver** (10-layer synthesis, dasha-by-dasha story, remedies, tone, Telugu voice, the specific format `AGENTS.md` defines) | **No — neither repo has this, and "a little LLM help" doesn't close that gap for free.** | Read `planb.md` §3 — even OpenJyotish's own `ai/` module (the most advanced of the three on this front) still hands narrative synthesis to a local LLM chat layer over its computed chart. It proves the same point `build_plan.md` is built around: **no one has solved deterministic narrative synthesis, including the most mature project reviewed.** "A little LLM help" over someone else's engine reproduces the exact black-box/non-reproducible problem you're trying to escape — just on top of a better substrate. |

So: **Plan B would make the *computation* faster and more accurate to reach.
It would not make the *predictions* (interpretive narrative) more
controllable — that problem is orthogonal to which chart-math engine you
use, and remains unsolved by every project reviewed, including the most
mature one.**

---

## 1. What "directly using" the repos would actually mean, concretely

Three real options, in increasing order of entanglement:

### Option B1 — Run one repo standalone, unmodified, as a local tool
Install OpenJyotish (has a CLI + PyQt6 GUI) or run PyJHora's PyQt6 desktop
app locally, generate charts/dashas/panchanga/compatibility reports through
their own UI, and manually copy numbers into your own readings. No code
integration at all.

- **License risk: near-zero.** Both are copyleft (GPL-3.0 for OpenJyotish
  per its actual `LICENSE` file — its `pyproject.toml` inconsistently
  still declares AGPL — and AGPL-3.0 for PyJHora, confirmed unambiguous).
  Running unmodified, un-networked, locally installed software you never
  redistribute triggers no copyleft obligation under either license — you
  are simply "a user," not "a distributor" or "a network-service operator."
- **Speed: fast to start, slow to scale.** Great for one-off cross-checks
  (this is exactly the workflow `docs/public-repo-review/` already uses).
  Bad as a production pipeline — manual copy-paste doesn't scale to
  "generate 5 people's readings a week," and it reintroduces human
  transcription error into what should be a deterministic chain.
- **Verdict: already what you're doing informally; keep doing it as a
  reference oracle, not a production path.**

### Option B2 — Run one repo as a separate local service, call it over a process/API boundary
Wrap OpenJyotish's `jhora` package in a tiny local FastAPI/CLI shim of your
own (a few dozen lines, your own code, calling their public functions),
run it as a second local process, and have `app/` call it over HTTP/subprocess
for raw chart-math JSON — never `import jhora` inside `app/` itself.

- **License risk: low but not zero — the honest nuance.** GPL/AGPL's
  copyleft attaches to *derivative works*, not to *separate programs that
  merely communicate over a process boundary* (this is the FSF's own
  long-standing "mere aggregation" / IPC distinction, and is why e.g. many
  companies run GPL'd databases as a separate service without their own
  app becoming GPL). This is meaningfully safer than embedding, but:
  - It is **not** a bulletproof legal wall — how "separate" the programs
    really are (shared memory vs. socket, how tightly your product depends
    on it, whether you'd ever ship/distribute the two together as one
    installable unit) affects the analysis, and neither of us is a lawyer.
  - It still doesn't change anything if you ever want to **distribute,
    sell, or host this for others** — at that point get real legal review
    before shipping, not before.
  - PyJHora specifically is AGPL, whose network clause is the strictest
    reading of "does running it count as distribution" — if you ever
    exposed *their* process as a network-reachable endpoint to anyone but
    yourself, the calculus changes. Keep it strictly loopback/local for
    this option to hold.
- **Speed: fast** — you'd have full-featured panchanga/dasha/varga/dosha/
  compatibility computation working in days, not the months `build_plan.md`
  budgets for the equivalent clean-room build.
- **Accuracy: very likely higher, sooner** — you inherit their book-example
  test coverage instantly instead of re-earning it rule-by-rule.
- **Controllability: this is where it gets worse, not better** — you now
  have a second runtime (different Python env, different ayanamsha
  defaults, different global-state conventions — PyJHora's own `const`/
  `drik` modules use side-effecting global mode-setting, which
  `technical-architecture.md` already flagged as a design smell we
  explicitly rejected) that you don't own and can't safely patch without
  re-entering the license risk. Bugs in their code become "wait for
  upstream" instead of "fix it now." Every future feature request has to
  ask "does their API even expose this" before you can build it.
- **Verdict: legitimate accelerant for the computation layer specifically**,
  if you're comfortable owning the licensing nuance above. Does **not**
  replace `build_plan.md`'s rule-engine/narrative-composer work — it just
  gives that work a faster, better-tested foundation to sit on, and you'd
  still need to build your own rule/composer layer over it for
  interpretation.

### Option B3 — Fork/vendor one repo's code into `app/`
Copy `jhora`'s modules directly into the codebase, modify them, ship them
as part of `app/`.

- **License risk: real and immediate**, exactly as `docs/public-repo-review/01-license-and-legal.md`
  already concluded. This is the one option that's a clear no given the
  project's own stated posture (proprietary rule engine IP, Walmart-adjacent
  infra guidance to not paper over compliance risk).
- **Not recommended, not re-litigated here** — the original review's
  verdict stands for this option specifically.

---

## 2. Would Option B2 actually be "faster and more accurate" than `build_plan.md`'s Phase 1-2?

**For the chart-math substrate specifically: yes, materially.** Compare:

| | `build_plan.md`'s clean-room path | Plan B2 (local service wrapper) |
|---|---|---|
| Time to full D1-D60 vargas | Phase 1, several build-agent sessions, algorithm read from BPHS + cross-checked against `charts.py` | Hours — call their existing, tested function |
| Time to full Panchanga | Phase 1 | Hours |
| Time to marriage compatibility (Ashtakuta) | Phase 4a, gated on aspects + dignities engines existing first | Hours — call `compatibility.py`/`kuta.py` directly |
| Time to 50+ dasha systems | Not attempted (scoped down to Vimshottari + 1-2 secondary per `build_plan.md` §5a) | Already there if you want them |
| Test coverage inherited | Whatever you write yourself, fixture by fixture | ~6800 book-example tests (PyJHora) or 1153+ (OpenJyotish), inherited immediately |
| Long-term ownership/control | Full — every line is yours, no upstream dependency, license-clean regardless of future distribution plans | Partial — a second runtime you don't own, license-constrained if you ever want to distribute/host, harder to patch |
| Interpretation/narrative layer | Still has to be built either way (§3) | Still has to be built either way (§3) |

**The honest recommendation, given both files now exist:** treat Option B2
as a legitimate *time-boxed acceleration tactic* for exactly the items in
`build_plan.md` §5 that are pure mechanical computation (vargas, panchanga,
Ashtakavarga, basic dasha timelines) — stand up a local OpenJyotish shim,
validate your own clean-room implementations against it continuously (this
is just a faster, live version of the scratch-venv cross-check `build_plan.md`
already mandates), and let it set your accuracy bar. But **don't let it
replace the clean-room build for anything you might ever distribute,
commercialize, or host for others** — that's the one scenario where the
license question stops being "probably fine for personal use" and starts
being a real liability, and it's cheap to keep that door open by staying
clean-room now rather than expensive to re-do later.

---

## 3. Why "a little LLM help" doesn't close the real gap

Your original ask was to *reduce* LLM dependency because the current
pipeline is "a black box, very slow, output might differ every time with no
control on narrative." Using these repos directly and adding "a little LLM
help" on top reproduces that exact failure mode, just with better inputs:

- OpenJyotish's own `ai/` module (`src/jhora/ai/{engine,prompts,teacher}.py`)
  is proof of this in the wild: it's the most feature-complete of the three
  repos on the interpretation front, and its answer to "how do we generate
  readings" is *still* "call a local LLM (Ollama/LM Studio/Unsloth) with a
  system prompt" — not a deterministic rule/template layer. If the largest,
  most mature, most-tested open-source Jyotisha codebase reviewed here
  didn't solve deterministic narrative generation, "a little LLM help" over
  a similar engine won't either — the problem isn't the chart math, it's
  the interpretation layer, and that's `build_plan.md` §3-§4's job
  (rule-content buildout + Narrative Composer), independent of which engine
  supplies the numbers underneath.
- What *would* be faster and more controllable, if you want the LLM-out-of-
  the-loop benefit sooner: use Option B2 to get accurate chart math fast,
  then invest the time you'd have spent re-deriving vargas/panchanga/dasha
  math into `build_plan.md`'s rule-content buildout and Narrative Composer
  instead — that's the piece no one else has built, and it's the piece that
  actually determines whether your output is reproducible.

---

## 4. Recommendation

1. **Do not adopt Option B3** (vendoring/forking) — license risk is real, already settled by the original review.
2. **Consider Option B2** (local service wrapper) as a `build_plan.md` accelerant specifically for Phase 1 items (vargas, panchanga, Ashtakavarga) and Phase 4a (marriage compatibility) — it can compress those phases from weeks to days, provided you keep it strictly local/loopback and never redistribute it bundled with your own product.
3. **Do not treat B2 as a substitute for `build_plan.md` §3-§4** (rule-engine content + Narrative Composer) — that work is unavoidable regardless of which engine supplies the chart math, because no reviewed project (including the best one) has solved it.
4. **Keep Option B1** (manual reference-oracle use) exactly as `docs/public-repo-review/` already does — it's low-effort, zero-risk, and already working.
5. If your priority is genuinely "get accurate charts + panchanga + dashas + compatibility numbers this week," start with B2 on those specific calculators; if your priority is "get controllable, reproducible, scripture-cited *predictions*," that's `build_plan.md` §3-§4 regardless of which path you take on §1.
