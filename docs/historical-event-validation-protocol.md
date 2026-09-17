# Historical-Event Validation Protocol (build_plan.md Phase 2 item 10)

> **Status: NOT YET EXECUTABLE.** This is an honest protocol definition,
> not a completed validation. It requires real, user-supplied biographical
> data that does not currently exist anywhere in this repo (confirmed:
> `data/charts/*.yaml` carries no `events` field as of this writing).
> Per AGENTS.md Cardinal Rule 2 ("never fabricate"), no plausible-sounding
> life events have been invented to make this look more complete than it
> is. This doc exists so that when real data becomes available, the
> protocol to run against it is already agreed, instead of being designed
> under time pressure later.

## 1. What "Lagna-balanced regression dataset" means operationally

`app.derived.lagna_coverage.lagna_coverage_report()` audits which of the 12
Lagna signs the current fixture set (`data/charts/*.yaml`) actually
exercises. As of this writing, the 7 fixtures cover only **5 of 12** Lagna
signs (Scorpio, Capricorn x3, Pisces, Gemini, Taurus) -- Aries, Cancer,
Leo, Virgo, Libra, Sagittarius, and Aquarius have **zero** fixture
coverage. `app.derived.lagna_coverage.functional_nature_classification_coverage()`
audits a second, complementary signal: which functional-nature
classifications (`functional_malefic`, `yoga_karaka`,
`kendradhipati_dosha`, `functional_benefic_with_dusthana_mitigation`, ...)
are exercised by at least one real fixture, since even a Lagna-complete
fixture set could still fail to exercise every classification.

**The only honest way to close this gap is adding real natives' charts**
to `data/charts/{id}.yaml`, ideally chosen to fill the missing Lagna signs
above. This is a data-acquisition task (get consent, get accurate
birth data), not an engineering one -- no code change closes it.

## 2. What "historical-event validation" would require, once data exists

For a given native's fixture, add an `events:` block (schema below) listing
real, dated life events the native has confirmed. The validation itself
would then check whether the computed daśā/transit/varga machinery was
*active* in the relevant domain at the time of each event -- using the
already-built engines, not new ones:

```yaml
events:
  - date: "2019-06-01"
    domain: marriage          # must be a key in app.derived.event_agreement.EVENT_DOMAINS
    description: "Native's own marriage date (user-confirmed)"
```

For each event, the protocol is:

1. Build the chart context anchored at `date` (`build_chart_context(fixture, today=event_date)`).
2. Run `app.derived.event_agreement.event_agreement(ctx, domain)` for that date.
3. Record whether `verdict` was `strong_agreement` or `moderate_agreement` (a
   "hit") vs. `weak_agreement` (a "miss").
4. Aggregate hit-rate across all recorded events, across all natives with
   event data -- this is the only trustworthy accuracy signal for the whole
   rule-engine pipeline, since it is the one place where the model's output
   is checked against ground truth the model cannot see in advance.

**This is deliberately not run today** because step 0 (real event data) does
not exist. Fabricating "the native got married around age 27" to have
*something* to validate against would produce a meaningless, self-flattering
number -- worse than no number at all, because it would look like evidence.

## 3. Next action (not automatic -- requires the user)

If/when real historical events are available for any of the 7 existing
natives (or a new native being onboarded), add the `events:` block above to
that fixture and run the 4-step protocol. Until then, this remains
`data_gap`, reported honestly rather than silently skipped.
