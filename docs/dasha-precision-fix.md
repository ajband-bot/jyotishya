# Dasha Engine Precision Fix — 2026-09-16

> Written in response to a user report: "my current pratyantardasha is
> Mercury, not Rahu as flagged in earlier messages." Investigated
> rigorously rather than assumed correct or incorrect on either side.
> Two separate things were tangled together here — a real bug, and a
> miscommunication. Both are recorded below.

## Finding 1 (miscommunication, not a bug): "Rahu" was a frozen test anchor, not "today"

The earlier session cited `tests/run_suite.py`'s regression baseline,
which computes the dasha chain as of a **hardcoded historical anchor
date, `CRITICAL_DATE = date(2026, 4, 11)`** — not the live calendar date.
As of that specific frozen date, Ajay Kumar's chain genuinely is
Rahu/Moon/**Rahu**. Presenting that as "your current dasha" without
noting it was anchored to April 11 was a mistake in that response, not a
computation error. This file's own regression test
(`test_critical_date_baseline_unaffected_by_precision_fix`) locks in that
CRITICAL_DATE answer permanently so it can be cited correctly going
forward.

## Finding 2 (real bug, fixed): compounding day-truncation in `app/astro/dashas.py`

`compute_antardashas()` and `compute_pratyantaradashas()` used to compute
each sub-period's day-count via `int(years * 365.25)` (hard truncation,
always rounding DOWN) and then stack that truncated day-count onto the
running current date:

```python
sub_days = int(sub_yrs * 365.25)   # always loses a fraction of a day
end_d = cur + timedelta(days=sub_days)
cur = end_d                         # loss carries forward to the next period
```

Doing this **9 times** within a Mahadasha (for 9 Antardashas), and then
**9 more times** within the active Antardasha (for 9 Pratyantardashas),
compounds the loss. For Ajay Kumar's Rahu Mahadasha → Moon Antardasha,
this produced a **cumulative drift of 4-5 days** by the time the
timeline reached "today" — enough, in principle, to make the wrong
Pratyantardasha appear "current" right at a boundary.

**Fix**: track a single cumulative elapsed-days float per parent period,
and round to a whole day exactly ONCE per boundary (both the start and
end of each sub-period are derived from the same running float, not from
re-adding an already-rounded previous sub-period's truncated span):

```python
elapsed_days = 0.0
for i in range(9):
    sub_yrs = ...
    start_d_i = start_d + timedelta(days=round(elapsed_days))
    elapsed_days += sub_yrs * DAYS_PER_YEAR
    end_d = start_d + timedelta(days=round(elapsed_days))
```

This guarantees the 9th (last) sub-period's end lands within 1 day of
its parent's own end boundary (an unavoidable residual from each level
independently rounding its own start against its own already-rounded
parent start — not a further compounding bug), instead of several days
short. Applied identically to `compute_dashas()` at the Mahadasha level
too, for consistency (its own drift is much smaller since Mahadashas
span 6-19 years, but the same class of bug existed there).

**Verified harmless to the existing regression baseline**: re-running
`tests/run_suite.py --mode verify` at the frozen `CRITICAL_DATE`
(2026-04-11) after the fix reproduces the exact same
Rahu/Moon/Rahu and Mercury/Jupiter/Venus chains as before — the fix only
changes answers for dates far enough from a period's own start that the
old compounding truncation had accumulated multiple days of drift.

## Finding 3: does the fix make today's (2026-09-16) Pratyantardasha "Mercury"?

**No** — after the fix, Ajay Kumar's Pratyantardasha as of 2026-09-16 is
still **Saturn**, running 2026-06-30 → 2026-09-25. Mercury begins
2026-09-26, only ~10 days after the date this session's environment
reported as "today." The fix closed a multi-day compounding gap, but it
was not large enough (nor should it have been — the bug was real but
modest) to flip the Sept-16 answer all the way to Mercury.

**Most likely explanation for the remaining gap**: the coding
environment's system clock and the user's real, live wall-clock date are
not the same moment — Mercury genuinely does become current within about
a week and a half of the environment's stated "today." If the user's own
real calendar date is on or after **2026-09-26**, Mercury is the
textually-correct current Pratyantardasha and there is no remaining
discrepancy. This is a mundane environment/session-clock skew, not
something to "fix" in the engine. Flagged rather than silently assumed —
see the conversation for the explicit ask back to the user to confirm
their real current date so this can be closed out definitively.

## Finding 4: D9 (Navamsha) Lagna for Ajay Kumar — re-verified, still Virgo

The user separately flagged that D9 Lagna should be Capricorn, not Virgo
(the value this session's engine output, and which
`docs/marriage-compatibility-notes.md` already flagged as contradicting
3 existing corpus documents that claim Pisces). Re-verified independently
a FIFTH way this session (on top of the 4 already logged in
`docs/marriage-compatibility-notes.md`): PyJHora's own
`dasavarga_from_long()` formula (`public-git-repos/PyJHora-main/src/jhora/panchanga/drik.py`),
applied by hand to Ajay's exact Lagna longitude (219.8485°), independently
gives **Virgo**:

```
one_sign = 40.0  (= 12 * 360/(12*9), PyJHora's own elegant constant)
signs_elapsed = 219.8485 / 40.0 = 5.496212
fraction_left = 0.496212
constellation = int(0.496212 * 12) = 5   # 0-indexed -> Virgo (6th sign)
```

This is now confirmed FIVE independent ways (hand-applied classical
movable/fixed/dual navamsha rule; the "108-part universal index" formula;
this codebase's own `app.astro.engine.navamsha_d9()`; this codebase's own
separately-implemented `app.astro.vargas.compute_varga(chart, 9)`, which
carries `citation_status: verified_by_engine`; and now PyJHora's
independent open-source formula). All five agree: Virgo. **This engine
continues to trust Virgo as the correct D9 Lagna for Ajay Kumar.** If
there is a specific external source or a different birth-time/ayanamsha
assumption behind the "Capricorn" expectation, please share it — that is
the one piece of information that would let this be investigated further
rather than re-asserted.
