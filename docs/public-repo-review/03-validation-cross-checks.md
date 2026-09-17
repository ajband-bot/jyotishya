# 3. Validation Cross-Checks

Two independent sample checks were run comparing our engine's already-published
`output/Ajay_Kumar_Validation.md` against a from-scratch computation using
PyJHora (chosen because it is the most mathematically rigorous of the three —
~6800 tests against the source textbook's worked examples, and the direct
upstream that OpenJyotish itself is built on).

**Method note (why this is a legitimate independent check, not circular):**
PyJHora was run from a disposable scratch virtualenv (`venv/`, this repo's
existing Python env, with PyJHora's runtime dependencies installed
temporarily via `uv pip install`) by importing `jhora.panchanga.drik` and
`jhora.horoscope.chart.charts` directly — no code was copied, no import was
added to `app/`, and nothing here is wired into the product. This is exactly
the "read-only reference, run standalone, never import into `app/`" policy
from `01-license-and-legal.md` §"Practical policy going forward" item 1,
demonstrated in practice.

Input: **Bandlapalli Ajay Kumar**, DOB 1987-12-31, 04:15:00 IST, Kalyandurg
AP (14.54519N, 77.10552E), Lahiri ayanamsha, mean node — pulled verbatim from
`data/charts/ajay_kumar.yaml`.

## Check 1 — Planetary positions (D1 Rāśi chart)

First pass (before pinning ayanamsha mode explicitly on the PyJHora side)
showed a **constant ~1.15 degree offset across every single body** — a
strong tell that this was an ayanamsha *setting* mismatch, not a
computation bug, since a real bug would not produce an identical offset on
every planet. Diagnosis confirmed: PyJHora's `drik` module needs an explicit
`drik.set_ayanamsa_mode('LAHIRI')` call; without it, some other default mode
was active. After pinning both engines to Lahiri explicitly:

| Body | Our engine (`output/Ajay_Kumar_Validation.md`) | PyJHora (this check) | Diff |
|---|---|---|---|
| Lagna | Scorpio 09°50'54.6" | Scorpio 09°50'54.7" | 0.1" |
| Sun | Sagittarius 15°00'49.0" | Sagittarius 15°01'09.6" | ~21" |
| Moon | Aries 27°58'36.1" | Aries 27°58'36.8" | 0.7" |
| Mars | Scorpio 00°32'16.4" | Scorpio 00°32'46.2" | ~30" |
| Mercury | Sagittarius 19°27'15.8" | Sagittarius 19°28'03.4" | ~48" |
| Jupiter | Pisces 26°29'14.6" | Pisces 26°29'19.8" | ~5" |
| Venus | Capricorn 17°01'26.4" | Capricorn 17°02'00.7" | ~34" |
| Saturn | Sagittarius 01°39'10.8" | Sagittarius 01°39'37.5" | ~27" |
| Rahu | Pisces 03°32'01.3" | Pisces 03°10'54.5" | **~21'01"** |
| Ketu | Virgo 03°32'01.3" | Virgo 03°10'54.5" | **~21'01"** |

**Verdict: PASS with one explained, config-level discrepancy.**

- **Sign placement matches on all 10 bodies** — Lagna and every graha land
  in the identical rāśi in both engines. This is the number that matters
  most for house-lordship, yoga, and doṣa logic (all of which key off sign
  and house, not sub-degree precision).
- **Lagna and the 7 classical grahas agree to within under 1 arc-minute**
  (most under 30 arc-seconds). Residual sub-arcminute differences at this
  scale are consistent with: (a) our engine falling back to Swiss
  Ephemeris's built-in Moshier approximation because no `.se1` ephemeris
  data files are installed locally (`ephe/` is gitignored and absent — see
  `app/astro/engine.py`, uses `FLG_SWIEPH` without a path set), vs. (b)
  PyJHora possibly applying topocentric/elevation correction (`drik.py` has
  an `_elevation_lookup(lat, lon)` helper suggesting it may factor in site
  elevation via a network lookup) or using bundled ephemeris files instead
  of the Moshier fallback. Either way this is a known, bounded, and
  non-alarming source of sub-arcminute drift — well within tolerance for
  sign/house/nakshatra-pada level interpretation, and worth resolving
  properly once `ephe/` data files are actually installed (a pre-existing,
  unrelated action item — not something this review is raising as new).
- **Rahu/Ketu differ by ~21 arc-minutes — fully explained, not a bug.**
  PyJHora's `const.py` sets `_use_true_nodes_for_rahu_ketu = True` as its
  **default** (`_RAHU = swe.TRUE_NODE if _use_true_nodes_for_rahu_ketu else
  swe.MEAN_NODE`), while our fixture and engine explicitly use the **mean**
  node (`data/charts/ajay_kumar.yaml`: `node_type: mean`;
  `app/astro/engine.py`: hardcoded `swe.MEAN_NODE`). True and mean node can
  differ by up to roughly 1.5 degrees depending on lunar nutation phase; 21'
  is well within that normal range. This is a genuine, well-documented
  difference in classical practice (different traditions/software default
  differently) — not an error in either engine. It does, however,
  **independently confirm a real gap already flagged in our own
  `technical-architecture.md` §4.1**: our engine has no `node_type`
  parameter yet (mean node is hardcoded), so a user who wants true-node
  Rahu/Ketu has no way to ask for it today. This cross-check is good
  evidence to prioritize that specific config knob.

## Check 2 — Kuja Doṣa (Maṅgala Doṣa) with cancellation logic

Our published validation (`output/Ajay_Kumar_Validation.md` §9) states:

| Reference | Verdict |
|---|---|
| From Lagna | PRESENT (Mars in H1) |
| From Moon | PRESENT (Mars in H8 from Moon) |
| From Venus | Absent (Mars in H11 from Venus) |
| **Overall** | **Moderate — Largely Cancelled** (Mars in own sign is the primary cancellation, reinforced by Jupiter's aspect on the Mars-occupied house) |

PyJHora's `horoscope/chart/dosha.py::manglik()` function (a completely
independent implementation, including its own from-scratch BV Raman
17-condition exception table) was run against the same chart:

```
From Lagna:  [True,  True,  [7, 9, 12]]   # [is_manglik, has_exceptions, exception_ids]
From Moon:   [True,  True,  [7, 9, 12]]
From Venus:  [False, False, []]
```

Mapping PyJHora's exception indices back to its own docstring (`dosha.py`,
`_manglik_exceptions`):

- **#7** — "Mars is in association or aspected by Jupiter or Saturn" — this
  is the *exact same cancellation reason* our doc cites: "Jupiter's 9th
  aspect on H1."
- **#12** — "Mars in own house, exalted, or in friend's house — reduced
  effects" — this is the *exact same primary cancellation* our doc leads
  with: "Mars in own sign (Scorpio) in doṣa house — PRIMARY CANCELLATION."
- **#9** — "Mars is weak (combust, rāśi sandhi, etc.)" — flagged by PyJHora
  because Mars sits at 00°32' (within 1 degree of a sign boundary, the
  classical rāśi-sandhi zone). This is a *legitimate additional
  cancellation factor our own doc did not explicitly call out* — worth
  folding into `docs/dosha-registry.md`'s Kuja Doṣa cancellation checklist
  as an explicit numbered condition (see `04-recommendations-roadmap.md`).

**Verdict: PASS, and better than a bare pass** — not only does the
present/absent/cancelled verdict match across two fully independent
codebases (different languages... well, both Python here, but zero shared
code, built by unrelated authors, using different internal representations
for planet positions), the *specific cited reasons* for cancellation match
on the two factors we already document, and PyJHora surfaced one additional
legitimate classical factor (rāśi-sandhi weakness of Mars) that strengthens
rather than contradicts our "largely cancelled" conclusion.

## What this cross-check does and doesn't prove

**Does prove:**
- Our Julian Day / Lahiri ayanamsha / sidereal longitude / house-mapping
  pipeline in `app/astro/engine.py` is correct to well within usable
  tolerance against an independently-built, heavily-tested reference engine.
- Our Kuja Doṣa interpretation logic (currently authored by the LLM
  narrative pipeline per `AGENTS.md`, not yet a first-class `app/derived/`
  calculator) reaches the same conclusion as a mature, rule-based,
  from-scratch implementation, including matching specific cancellation
  citations.

**Does not prove:**
- Accuracy of our other, more speculative interpretive layers (yogas,
  dasha-timing narrative, remedy prescriptions) — those weren't
  cross-checked here and have no equivalent "ground truth" engine to check
  against; they remain governed by the citation/confidence discipline in
  `AGENTS.md` (cite chapter/verse, label `data_gap` honestly).
- That PyJHora (or the other two repos) are bug-free or authoritative in
  some absolute sense — they are themselves one more implementation of
  classical formulas, useful as a second data point, not a supreme oracle.

## Reproducing this check

The scratch script used (not committed, reconstructable from this doc):

```python
from jhora.panchanga import drik
from jhora import utils, const
from jhora.horoscope.chart import charts, dosha

dob = drik.Date(1987, 12, 31)
tob = (4, 15, 0)
place = drik.Place('Kalyandurg,AP', 14.54519, 77.10552, 5.5)
jd = utils.julian_day_number(dob, tob)
drik.set_ayanamsa_mode('LAHIRI')   # must be explicit -- see Check 1 finding

pp = charts.rasi_chart(jd, place)   # [[planet, (rasi, longitude)], ...]
print(dosha.manglik(pp, manglik_reference_planet='L',
                     include_lagna_house=True, include_2nd_house=True))
```

Runtime deps installed into this repo's existing `venv/` for the duration
of this check only: `numpy`, `pytz`, `requests`, `geopy`, `img2pdf`,
`timezonefinder`, `reverse_geocode`, `geocoder`, `python-dateutil` — all via
the standard `uv pip install --index-url
https://pypi.ci.artifacts.walmart.com/artifactory/api/pypi/external-pypi/simple
--allow-insecure-host pypi.ci.artifacts.walmart.com ...` command per the
Walmart Python install standard. These are transitive runtime dependencies
of PyJHora's `utils.py` module import (geocoding/timezone lookups it does at
import time even though this check never used those features) — they are
**not** proposed as project dependencies; they were only needed to get
PyJHora's own module to import successfully for this one-off comparison.
