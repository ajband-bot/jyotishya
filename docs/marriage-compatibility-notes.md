# Marriage Compatibility Engine — Cross-Check & Discrepancy Log

> Written during build_plan.md Phase 4a (Marriage Compatibility engine:
> `app/derived/compatibility.py`, `synastry.py`, `marriage_timing.py`).
> Records every source disagreement found and how it was resolved, per
> Cardinal Rule 3 (never silently resolve conflicts) and Cardinal Rule 5
> (cite sources honestly). Nothing below blocks the engine being used —
> it is the receipts trail for *why* certain numbers differ from the
> existing prose corpus.

## 1. New fixture: `data/charts/sravani.yaml`

Transcribed from `Ajay_Sravani_Compatibility.md`'s own Couple Summary
table (19 Jul 1997, 22:16 IST, Anantapur AP). Verified against the
engine's own Swiss-Ephemeris computation: Sun longitude (93.22°), Moon
longitude (267.17°), and Jupiter's debilitated-retrograde-in-Capricorn-H11
placement all match that document's stated values to the same precision
it reports them at. High confidence in the fixture's birth data.

## 2. A real, repeated bug found in the existing prose corpus: Ajay Kumar's D9

`Marriage_Guide_Part1.md`, `Marriage_Guide_Part4.md`, and
`Ajay_Sravani_Compatibility.md` all independently state:

- Ajay's D9 Lagna = **Pisces**
- Ajay's D9 Venus = **Virgo (debilitated)**

The engine (`app.astro.engine.navamsha_d9`) computes, and this was
independently re-derived by hand twice (once via the classical
movable/fixed/dual starting-sign navamsha rule, once via the universal
"108-part index" formula — both agree with the engine and with each
other):

- Ajay's D1 Lagna = Scorpio at 219.8485° (9.8485° into the sign) → **D9
  Lagna = Virgo**
- Ajay's Venus = Capricorn at 287.024° (17.024° into the sign, matching
  the guide's OWN stated D1 value exactly) → **D9 Venus = Gemini**

The corpus's D9 Lagna/Venus values are wrong, most likely a copy-forward
error from a single earlier mis-computation that then propagated across
three documents (the "Ajay must consciously cultivate romantic
expression because his D9 Venus is debilitated" narrative thread appears
in all three). **This engine trusts its own computed D9, not the
corpus.** `app/derived/synastry.py::d9_cross_compatibility()` therefore
disagrees with the guide's own worked Rule 1/Rule 3 findings for this
couple — see the regression test
`test_d9_rule3_requires_exalted_not_merely_own_sign` in
`tests/unit/test_synastry.py` for the specific, disclosed divergence.

## 3. Nadi table: `Marriage_Guide_Part2.md` disagrees with itself

The document's quick "Nakshatra Reference Table" (top of file) and its
own detailed "NADI SYSTEM" section (used correctly in that same
document's worked example) disagree on roughly a third of the 27
nakshatras' Nadi group. The detailed section was kept — it is internally
consistent and matches PyJHora's independently-implemented
`naadi_porutham()` grouping array (`bvk`/`gvk`) **exactly on all 27
nakshatras** (cross-checked by hand, AD-4 data-only comparison). See
`app/knowledge/nakshatras.py`'s `nadi` field and its module docstring.

## 4. Varna: resolved via Moon RASHI ELEMENT, not a nakshatra table

`Marriage_Guide_Part2.md`'s per-nakshatra Varna column is ambiguous for
any nakshatra straddling two rashis with different elements (e.g.
Krittika spans Aries/Taurus). PyJHora's independent implementation
derives Varna purely from the Moon's rashi element (Water=Brahmin,
Fire=Kshatriya, Air=Vaishya, Earth=Shudra) — unambiguous, and the guide's
own two worked Varna examples (Ajay=Kshatriya via Aries/Fire,
Sravani=Kshatriya via Sagittarius/Fire) are consistent with this rule.
Adopted as the primary method; see `compatibility.py::varna_of_sign()`.

## 5. Vasya: resolved two self-contradictions in the guide's own bullet list

`Marriage_Guide_Part2.md` (a) lists Leo under "Chatushpada" in one bullet
but separately flags "Vanachara (Forest): Leo (some schools)" in the same
list; (b) lists all of Capricorn under "Chatushpada" AND "1st half of
Capricorn" under "Jalachara" in the same list. PyJHora's independent
`VasiyaArray` (sourced, per its own comment, from Saravali.de) resolves
both: Leo gets its own Vanachara group, and Capricorn splits at 15° (not
by nakshatra pada — PyJHora's own docstring admits the pada-based version
is an approximation of the degree-based one). Both resolutions adopted;
see `compatibility.py::vasya_group()`.

## 6. Yoni: `Marriage_Guide_Part2.md`'s own yoni table drifts from Mrigashira onward

`app.knowledge.nakshatras.NAKSHATRA_PROFILES` (already tested, cited to
BPHS Ch.86) and PyJHora's `yoni_mappings` agree exactly on all 27
nakshatra→animal assignments. `Marriage_Guide_Part2.md`'s own yoni table
disagrees starting around Mrigashira (it says "Female Deer"; both other
sources say "Serpent"). The already-tested, doubly-cross-checked
NAKSHATRA_PROFILES data was reused (DRY) rather than importing a third,
disagreeing table. This is why `yoni_kuta(Krittika, Uttara_Ashadha)`
returns 3 (Goat↔Mongoose per the 14×14 cross-checked matrix) rather than
the guide's informally-labeled "2 (neutral)" — the guide's own 5-tier
verbal label doesn't map to a rigorously derived matrix, unlike the value
used here.

## 7. Gana: adopted the richer, asymmetric Saravali-sourced matrix

`Marriage_Guide_Part2.md`'s own summary table treats
Deva+Manushya/Manushya+Deva as symmetric (both scored 5), and
Deva+Rakshasa/Rakshasa+Deva as symmetric (both scored 0).
PyJHora's `gana_array` (its own comment: "Based on saravali.de (Maitri)")
is asymmetric: Deva(bride)+Manushya(groom)=6 vs Manushya(bride)+Deva(groom)=5;
Deva(bride)+Rakshasa(groom)=0 vs Rakshasa(bride)+Deva(groom)=1. The richer,
independently-sourced table was adopted (`compatibility.py::GANA_MATRIX`)
since it is a strictly more granular version of the same classical
doctrine, not a contradiction of it.

## 8. Net effect: raw Ashtakuta total still matches exactly

Despite the Yoni (+1) and Gana (−1) individual differences from
`Ajay_Sravani_Compatibility.md`'s stated per-kuta scores, this engine's
computed **raw total (14/36) and dosha-cancelled effective total (25/36)
match that document exactly** — the two individual differences happen to
offset. This is disclosed as a coincidence of this specific chart pair,
not evidence the two approaches are numerically equivalent in general.

## 9. Bhakut: kept the guide's finer 7/5/0 scale, cross-checked the dosha-axis SET only

PyJHora's `raasi_array` for the "north Indian" Bhakut check is a simple
pass/fail (0 or 7) — it does not distinguish 3/11 and 4/10 (guide: 5
points) from 1/1 and 1/7 (guide: 7 points). What WAS cross-checked and
confirmed exact: the *set* of axes PyJHora treats as zero/dosha ({2/12,
5/9, 6/8}) matches the guide's own dosha-axis list exactly. The guide's
richer point scale was kept since PyJHora simply doesn't offer that level
of detail (not a disagreement, an absence).

## 10. Nadi Dosha mitigation scoring: a disclosed heuristic, not a universal formula

`Marriage_Guide_Part3.md`'s own worked example ("4 of 5 conditions met →
effective score 4/8") treats "conditions met" as a direct point count,
not a fraction of the max (4/5×8 would be 6.4, not 4). This is kept
exactly as the source demonstrates it (`nadi_kuta()`), disclosed in that
function's docstring as the source's own heuristic rather than a fixed
classical formula — other texts treat 2 met conditions as sufficient for
full cancellation.
