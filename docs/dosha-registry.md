# Doṣa Registry & Sade Sati Protocol

> **Status: MANDATORY.** Referenced by AGENTS.md §3 (The Process). Every Validation Document
> must check this full registry. Split out of AGENTS.md purely for context-budget reasons —
> carries the same authority as AGENTS.md itself.

---

## Doṣa Analysis Protocols

The following doṣas MUST be checked for every chart. Results go in the Validation Document.

### Maṅgala Doṣa (Kuja Doṣa)
**Definition**: Mars in houses 1, 2, 4, 7, 8, or 12 from Lagna, Moon, or Venus (BPHS Ch.77).
Check from all three references (Lagna, Moon, Venus). If present from any, flag it.

**11 Cancellation Conditions** (all must be checked):
1. Mars in own sign (Aries, Scorpio) or exalted (Capricorn) in the doṣa house
2. Mars in the same doṣa house in partner's chart (doṣa-samatva — mutual cancellation)
3. Jupiter or Venus aspects the Mars-occupied house
4. Mars conjunct or aspected by Jupiter
5. Mars in H1 in Aries/Leo/Aquarius Lagna
6. Mars in H2 in Gemini/Virgo
7. Mars in H4 in Aries/Scorpio
8. Mars in H7 in Cancer/Capricorn
9. Mars in H8 in Sagittarius/Pisces
10. Mars in H12 in Taurus/Libra
11. Moon conjunct Mars (Chandra-Maṅgala Yoga overrides partial doṣa)

**Severity rating**: Severe (from all 3 references, no cancellation) / Moderate (from 1-2 references, partial cancellation) / Cancelled (cancellation conditions apply)

### Kāla Sarpa Doṣa
**Definition**: All 7 planets (Sun through Saturn) hemmed between Rahu-Ketu axis on one side.
- **Full Kāla Sarpa**: all 7 on one side, none conjunct Rahu or Ketu
- **Partial Kāla Sarpa**: all 7 on one side, but one or more conjunct Rahu/Ketu (breaks the doṣa partially)
- **Not present**: even one planet on the other side

### Pitṛ Doṣa
**Definition**: Sun afflicted by Rahu or Saturn in the 9th house, OR 9th lord afflicted (BPHS Ch.80).
Indicates karmic debt to father/ancestors. Check Sun's state and 9th house condition.

### Guru Chaṇḍāla Yoga
**Definition**: Jupiter conjunct Rahu (within 15° orb in same sign). Corrupts Jupiter's wisdom — poor judgment, unconventional beliefs, guru-related problems. Check whether Jupiter is the stronger planet (mitigates) or Rahu dominates (amplifies).

### Kemādruma Doṣa
**Definition**: No planet in the 2nd or 12th house from Moon (BPHS Ch.24).
**Cancellations**: Planet in kendra from Lagna or Moon; Moon in kendra; strong Venus or Jupiter aspecting Moon.

### Pāpakartarī Yoga
**Definition**: A house hemmed between two malefics (one in the house before, one in the house after).
Check for all 12 houses. Flag any house under Pāpakartarī — that domain is constricted.

### Ghata Doṣa
**Definition**: Mars conjunct Saturn within a tight orb (15°), same sign — the classical "collision" doṣa between the two most aggressive/restrictive malefics. Indicates accident-proneness, friction between initiative (Mars) and discipline/restriction (Saturn), and health/injury risk during their shared daśā/transit windows.
**Disclosure (Cardinal Rule 5)**: added to this registry via `build_plan.md` Phase 4's dosha-registry recheck against PyJHora's `dosha.py` coverage. This is a widely-cited Parashari-tradition convention, not yet independently confirmed chapter/verse against a primary BPHS passage — `citation_status: pending_audit`, same disclosed treatment already applied to Kāla Sarpa above. Treat verdicts as directionally useful, not textually air-tight, until audited.

### Śrāpit Doṣa
**Definition**: Rāhu conjunct Saturn within a tight orb (15°), same sign — the "cursed" doṣa, associated with karmic/ancestral curses, prolonged obstacles, and delays that resist ordinary remedial effort.
**Disclosure (Cardinal Rule 5)**: same provenance and same `citation_status: pending_audit` caveat as Ghata Doṣa above — added via the Phase 4 registry recheck, a widely-cited convention pending primary-text confirmation.

---

## Sade Sati Protocol

**Definition**: Saturn transiting through the 12th house from Moon, over Moon, and through the 2nd house from Moon (~7.5 years total).

| Phase | Saturn's Position | Duration | Effect |
|-------|-------------------|----------|--------|
| **Rising (1st phase)** | 12th from Moon sign | ~2.5 years | Financial pressure, mental anxiety, preparation phase |
| **Peak (2nd phase)** | Over Moon sign | ~2.5 years | Maximum intensity — career upheaval, health concerns, transformation |
| **Setting (3rd phase)** | 2nd from Moon sign | ~2.5 years | Financial adjustment, family matters, resolution phase |

**Mandatory checks**:
1. Is native currently in Sade Sati? If yes, which phase?
2. List all historical Sade Sati periods (past and future up to age 75)
3. Map historical periods to known life events for validation

**Mitigation factors** (reduce severity):
- Saturn in own/exalted sign during transit
- Saturn as yogakāraka for the Lagna (e.g., Taurus/Libra Lagna)
- Strong natal Moon (in kendra, own/exalted sign, well-aspected)
- Jupiter's concurrent transit in kendra/trikoṇa from Moon
- Moon sign lord well-placed and strong
