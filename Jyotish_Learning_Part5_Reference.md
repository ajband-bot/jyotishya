# 🎓 Jyotisha Vidyā — Complete Learning Guide
## Part 5 of 5 — Mermaid Diagrams, Cheat Sheets & Quick Reference

> **Goal**: Visual learning aids, quick-lookup tables, and diagrams
> that you can print, pin to your wall, or pull up during practice.

📂 **Navigation**
- [← Part 1 — Structure](Jyotish_Learning_Part1_Structure.md)
- [← Part 2 — Calculations](Jyotish_Learning_Part2_Calculations.md)
- [← Part 3 — Interpretation](Jyotish_Learning_Part3_Interpretations.md)
- [← Part 4 — Worked Examples](Jyotish_Learning_Part4_Examples.md)
- ▶ Part 5 — Diagrams & Cheat Sheets ← *You are here*

---

## 📊 MERMAID DIAGRAM 1 — The Complete Jyotish Reading Pipeline

```mermaid
flowchart TD
    A[🎂 Birth Data<br/>Date, Time, Place] --> B[🔢 CALC-1: UTC Conversion]
    B --> C[📅 CALC-2: Julian Day Number]
    C --> D[🌐 CALC-3: Lahiri Ayanamsa]
    D --> E[🪐 CALC-4+5: Planet Longitudes<br/>Sign, Degree, House]
    D --> F[🏠 Lagna Computation<br/>GMST → LST → Ascendant]

    E --> G[⭐ CALC-6: Nakshatra & Pada]
    E --> H[🔥 CALC-7: Combustion Check]
    E --> I[↩️ CALC-8: Retrograde Check]
    E --> J[🔮 CALC-9: Navamsha D9]

    F --> K[📋 House Assignment<br/>Whole Sign from Lagna]

    G --> L[⏱️ CALC-10: Dasha Balance<br/>Moon Nakshatra → Starting MD]
    L --> M[📊 CALC-11: Antardasha Sequence]

    K --> N[🏗️ CHART CONSTRUCTED]
    E --> N
    G --> N
    H --> N
    I --> N
    J --> N
    M --> N

    N --> O{ANALYSIS PHASE}

    O --> P[👑 Dignity Assessment<br/>Exalt/Own/Friend/Enemy/Debil]
    O --> Q[👀 Aspects Mapping<br/>7th + Mars/Jup/Sat specials]
    O --> R[🏛️ Lordship Matrix<br/>Functional Benefic/Malefic]
    O --> S[✨ Yoga Detection<br/>8-Step Verification]
    O --> T[⚠️ Dosha Analysis<br/>+ Cancellation Check]

    P --> U{SYNTHESIS}
    Q --> U
    R --> U
    S --> U
    T --> U

    U --> V[🔟 10-Layer Synthesis Protocol]
    V --> W[📖 Life Narrative + Timing]
    W --> X[💊 Remedies Prescription]
    W --> Y[📊 Summary Dashboard]

    style A fill:#0053e2,color:#fff
    style N fill:#2a8703,color:#fff
    style U fill:#ffc220,color:#000
    style W fill:#0053e2,color:#fff
```

---

## 📊 MERMAID DIAGRAM 2 — Planet Strength Assessment Tree

```mermaid
flowchart TD
    A[🪐 Planet to Assess] --> B{In Own or<br/>Exalted Sign?}

    B -->|Yes| C[✅ HIGH Dignity]
    B -->|No| D{In Friendly<br/>Sign?}

    D -->|Yes| E[⚡ MODERATE Dignity]
    D -->|No| F{In Enemy or<br/>Debilitated Sign?}

    F -->|Yes| G[⚠️ LOW Dignity]
    F -->|No| H[😐 NEUTRAL Dignity]

    C --> I{Combust?}
    E --> I
    G --> I
    H --> I

    I -->|Yes| J[❌ WEAKENED<br/>Sun suppresses]
    I -->|No| K{Retrograde?}

    K -->|Yes| L[↩️ INTERNALIZED<br/>Strong but delayed]
    K -->|No| M{In Kendra<br/>or Trikona?}

    J --> N{Check D9}
    L --> N
    M -->|Yes| O[⭐ POWERFUL<br/>position]
    M -->|No| P{In Dusthana<br/>H6/H8/H12?}

    P -->|Yes| Q[🔻 RESTRICTED<br/>unless Viparita Yoga]
    P -->|No| R[📊 MODERATE<br/>position]

    O --> N
    Q --> N
    R --> N

    N --> S{D9 Dignified?}
    S -->|Yes| T[🌟 CONFIRMED<br/>STRONG overall]
    S -->|No| U[⚠️ OUTER strong<br/>INNER weak]

    style A fill:#0053e2,color:#fff
    style T fill:#2a8703,color:#fff
    style U fill:#ea1100,color:#fff
```

---

## 📊 MERMAID DIAGRAM 3 — Marriage Timing Decision Tree

```mermaid
flowchart TD
    A[💍 Marriage Timing?] --> B{Dasha involves<br/>H7L/Venus/DK/UL?}

    B -->|No| C[❌ Not this period]
    B -->|Yes| D{Jupiter transiting<br/>H1/H5/H7/H9/H11<br/>from Moon?}

    D -->|No| E[⏳ Dasha ready<br/>but transit not aligned]
    D -->|Yes| F{Saturn NOT in<br/>H8 from Moon?}

    F -->|Ashtama Shani| G[⚠️ Possible but<br/>with challenges]
    F -->|Clear| H[✅ TRIPLE AGREEMENT<br/>Marriage likely!]

    E --> I[Wait for next<br/>Jupiter cycle<br/>~1 year]

    style A fill:#ffc220,color:#000
    style H fill:#2a8703,color:#fff
    style C fill:#ea1100,color:#fff
```

---

## 📊 MERMAID DIAGRAM 4 — Learning Progression Map

```mermaid
graph LR
    A[L1: Observer<br/>Read chart grid] --> B[L2: Calculator<br/>JD, Ayanamsa, Lagna]
    B --> C[L3: Mapper<br/>Houses, Nakshatras]
    C --> D[L4: Analyst<br/>Dignity, Aspects, Lords]
    D --> E[L5: Pattern-Finder<br/>Yogas & Doshas]
    E --> F[L6: Timer<br/>Dasha & Transit]
    F --> G[L7: Interpreter<br/>Life Narrative]
    G --> H[L8: Predictor<br/>Specific Timing]
    H --> I[L9: Advisor<br/>Remedies]
    I --> J[L10: Master<br/>D9/D10, Jaimini]

    style A fill:#0053e2,color:#fff
    style E fill:#ffc220,color:#000
    style G fill:#0053e2,color:#fff
    style J fill:#2a8703,color:#fff
```

---

## 📊 MERMAID DIAGRAM 5 — Yoga Karaka by Lagna

```mermaid
graph TD
    subgraph "Lagnas WITH Yoga Karaka"
        AR[Aries] -->|Saturn H9+H10| YK1[♄ Saturn]
        TA[Taurus] -->|Saturn H9+H10| YK2[♄ Saturn]
        CA[Cancer] -->|Mars H5+H10| YK3[♂ Mars]
        LE[Leo] -->|Mars H4+H9| YK4[♂ Mars]
        LI[Libra] -->|Saturn H4+H5| YK5[♄ Saturn]
        CP[Capricorn] -->|Venus H5+H10| YK6[♀ Venus]
        AQ[Aquarius] -->|Venus H4+H9| YK7[♀ Venus]
    end

    subgraph "Lagnas WITHOUT Yoga Karaka"
        GE[Gemini] --> NONE1[No single YK]
        VI[Virgo] --> NONE2[No single YK]
        SC[Scorpio] --> NONE3[No single YK]
        SG[Sagittarius] --> NONE4[No single YK]
        PI[Pisces] --> NONE5[No single YK]
    end

    style YK1 fill:#ffc220,color:#000
    style YK2 fill:#ffc220,color:#000
    style YK3 fill:#ea1100,color:#fff
    style YK4 fill:#ea1100,color:#fff
    style YK5 fill:#ffc220,color:#000
    style YK6 fill:#2a8703,color:#fff
    style YK7 fill:#2a8703,color:#fff
```

---

## 📊 MERMAID DIAGRAM 8 — Planetary Dignity at a Glance

```mermaid
graph TD
    subgraph "⭐ EXALTATION — Maximum Strength"
        EX_SU["☀️ Sun → ♈ Aries 10°"]
        EX_MO["🌙 Moon → ♉ Taurus 3°"]
        EX_MA["♂ Mars → ♑ Capricorn 28°"]
        EX_ME["☿ Mercury → ♍ Virgo 15°"]
        EX_JU["♃ Jupiter → ♋ Cancer 5°"]
        EX_VE["♀ Venus → ♓ Pisces 27°"]
        EX_SA["♄ Saturn → ♎ Libra 20°"]
    end

    subgraph "🔴 DEBILITATION — Minimum Strength (opposite sign)"
        DE_SU["☀️ Sun → ♎ Libra 10°"]
        DE_MO["🌙 Moon → ♏ Scorpio 3°"]
        DE_MA["♂ Mars → ♋ Cancer 28°"]
        DE_ME["☿ Mercury → ♓ Pisces 15°"]
        DE_JU["♃ Jupiter → ♑ Capricorn 5°"]
        DE_VE["♀ Venus → ♍ Virgo 27°"]
        DE_SA["♄ Saturn → ♈ Aries 20°"]
    end

    subgraph "🟢 OWN SIGN — High Comfort"
        OWN_SU["☀️ Sun → ♌ Leo"]
        OWN_MO["🌙 Moon → ♋ Cancer"]
        OWN_MA["♂ Mars → ♈ Aries / ♏ Scorpio"]
        OWN_ME["☿ Mercury → ♊ Gemini / ♍ Virgo"]
        OWN_JU["♃ Jupiter → ♐ Sagittarius / ♓ Pisces"]
        OWN_VE["♀ Venus → ♉ Taurus / ♎ Libra"]
        OWN_SA["♄ Saturn → ♑ Capricorn / ♒ Aquarius"]
    end

    RULE["⚠️ NEECHABHANGA RULE:\nDebilitation CANCELLED if:\n• Debilitation sign lord is in Kendra\n• Exaltation sign lord is in Kendra\n• Debilitated planet is retrograde\n• Debilitated planet conjuncts exalted planet\n• Exaltation lord aspects the debilitated planet\n→ Cancelled debilitation = very powerful planet!"]

    style EX_SU fill:#ffc220,color:#000
    style EX_MO fill:#cce5ff,color:#000
    style EX_MA fill:#ea1100,color:#fff
    style EX_ME fill:#2a8703,color:#fff
    style EX_JU fill:#ffc220,color:#000
    style EX_VE fill:#6f42c1,color:#fff
    style EX_SA fill:#0053e2,color:#fff
    style RULE fill:#ffd5d5,color:#000
```

---

## 📋 CHEAT SHEET 1 — The 12 Signs at a Glance

| # | Sign | Element | Mode | Lord | Exalts | Debilitates | Body |
|---|------|---------|------|------|--------|-------------|------|
| 1 | Aries ♈ | Fire | Movable | Mars | Sun 10° | Saturn 20° | Head |
| 2 | Taurus ♉ | Earth | Fixed | Venus | Moon 3° | — | Face/Throat |
| 3 | Gemini ♊ | Air | Dual | Mercury | Rahu* | — | Shoulders |
| 4 | Cancer ♋ | Water | Movable | Moon | Jupiter 5° | Mars 28° | Chest |
| 5 | Leo ♌ | Fire | Fixed | Sun | — | — | Heart/Spine |
| 6 | Virgo ♍ | Earth | Dual | Mercury | Mercury 15° | Venus 27° | Intestines |
| 7 | Libra ♎ | Air | Movable | Venus | Saturn 20° | Sun 10° | Kidneys |
| 8 | Scorpio ♏ | Water | Fixed | Mars | — | Moon 3° | Reproductive |
| 9 | Sagitt. ♐ | Fire | Dual | Jupiter | Ketu* | — | Thighs |
| 10 | Capricorn ♑ | Earth | Movable | Saturn | Mars 28° | Jupiter 5° | Knees |
| 11 | Aquarius ♒ | Air | Fixed | Saturn | — | — | Ankles |
| 12 | Pisces ♓ | Water | Dual | Jupiter | Venus 27° | Mercury 15° | Feet |

*Rahu/Ketu exaltation: schools differ. Gemini/Sagittarius per BPHS Ch.3.

---

## 📋 CHEAT SHEET 2 — Natural Friendships

```
         FRIENDS           NEUTRAL          ENEMIES
Sun    : Mo, Ma, Ju      | Me              | Ve, Sa
Moon   : Su, Me          | Ma, Ju, Ve, Sa  | (none)
Mars   : Su, Mo, Ju      | Ve, Sa          | Me
Mercury: Su, Ve          | Ma, Ju, Sa      | Mo
Jupiter: Su, Mo, Ma      | Sa              | Me, Ve
Venus  : Me, Sa          | Ma, Ju          | Su, Mo
Saturn : Me, Ve          | Ju              | Su, Mo, Ma
```

```mermaid
graph TD
    subgraph "🤝 PLANETARY NATURAL FRIENDSHIPS"
        SU["☀️ SUN"]
        MO["🌙 MOON"]
        MA["♂ MARS"]
        ME["☿ MERCURY"]
        JU["♃ JUPITER"]
        VE["♀ VENUS"]
        SA["♄ SATURN"]

        SU <-->|"Friends"| MO
        SU <-->|"Friends"| MA
        SU <-->|"Friends"| JU

        MA <-->|"Friends"| MO
        MA <-->|"Friends"| JU

        ME <-->|"Friends"| SU
        ME <-->|"Friends"| VE

        VE <-->|"Friends"| ME
        VE <-->|"Friends"| SA

        SA <-->|"Friends"| ME

        SU -.-|"Enemy"| VE
        SU -.-|"Enemy"| SA
        MA -.-|"Enemy"| ME
        ME -.-|"Enemy"| MO
        JU -.-|"Enemy"| ME
        JU -.-|"Enemy"| VE
        SA -.-|"Enemy"| SU
        SA -.-|"Enemy"| MO
        SA -.-|"Enemy"| MA
    end

    LEGEND["Legend:\n—— Friends (mutual enhancement)\n........ Enemies (tension/conflict)\nNo line = Neutral"]

    style SU fill:#ffc220,color:#000
    style MO fill:#cce5ff,color:#000
    style MA fill:#ea1100,color:#fff
    style ME fill:#2a8703,color:#fff
    style JU fill:#ffc220,color:#000
    style VE fill:#6f42c1,color:#fff
    style SA fill:#0053e2,color:#fff
```

---

## 📋 CHEAT SHEET 3 — House Classifications

```
KENDRA (Angular):    H1   H4   H7   H10    ← Power houses
TRIKONA (Trine):     H1   H5   H9          ← Lakshmi's seats
UPACHAYA (Growing):  H3   H6   H10  H11    ← Malefics do well
DUSTHANA (Difficult):H6   H8   H12         ← Challenge houses
MARAKA (Death):      H2   H7               ← Longevity-sensitive

H1 = BOTH Kendra AND Trikona → doubly auspicious!
H10 = BOTH Kendra AND Upachaya → career planets thrive here
```

```mermaid
graph TD
    subgraph "🏠 12 HOUSES — Classifications & Significations"
        H1["H1 — SELF\n♑/♈ etc (Lagna sign)\n🟦 KENDRA + TRIKONA\nBody, personality, vitality\n★ Most powerful house"]
        H2["H2 — WEALTH\n🔴 MARAKA\nWealth, family, speech, food"]
        H3["H3 — COURAGE\n🟨 UPACHAYA\nSiblings, effort, communication\nShort journeys"]
        H4["H4 — HOME\n🟦 KENDRA\nMother, property, vehicles\nEmotional comfort"]
        H5["H5 — CHILDREN\n🟩 TRIKONA\nCreativity, intellect, romance\nPast-life merit"]
        H6["H6 — OBSTACLES\n🟨 UPACHAYA + ⚠️ DUSTHANA\nEnemies, disease, litigation\nService, daily work"]
        H7["H7 — MARRIAGE\n🟦 KENDRA + 🔴 MARAKA\nSpouse, partnerships\nOpen enemies, business"]
        H8["H8 — TRANSFORMATION\n⚠️ DUSTHANA\nLongevity, secrets, inheritance\nOccult, sudden events"]
        H9["H9 — FORTUNE\n🟩 TRIKONA\nFather, dharma, higher learning\nGuruji, long journeys"]
        H10["H10 — CAREER\n🟦 KENDRA + 🟨 UPACHAYA\nProfession, reputation\nGovernment, status"]
        H11["H11 — GAINS\n🟨 UPACHAYA\nFulfillment of desires\nElder siblings, networks"]
        H12["H12 — LIBERATION\n⚠️ DUSTHANA\nForeign lands, expenses\nSpiritual growth, losses"]
    end

    style H1 fill:#0053e2,color:#fff
    style H4 fill:#0053e2,color:#fff
    style H7 fill:#0053e2,color:#fff
    style H10 fill:#0053e2,color:#fff
    style H5 fill:#2a8703,color:#fff
    style H9 fill:#2a8703,color:#fff
    style H3 fill:#ffc220,color:#000
    style H6 fill:#ffc220,color:#000
    style H11 fill:#ffc220,color:#000
    style H2 fill:#ea1100,color:#fff
    style H8 fill:#666,color:#fff
    style H12 fill:#666,color:#fff
```

---

## 📋 CHEAT SHEET 4 — Vimshottari Dasha Quick Ref

```
PLANET   YEARS   NAKSHATRA LORDS (starting dashas)
Ketu      7      Ashwini(1), Magha(10), Mula(19)
Venus    20      Bharani(2), P.Phalguni(11), P.Ashadha(20)
Sun       6      Krittika(3), U.Phalguni(12), U.Ashadha(21)
Moon     10      Rohini(4), Hasta(13), Shravana(22)
Mars      7      Mrigashira(5), Chitra(14), Dhanishtha(23)
Rahu     18      Ardra(6), Swati(15), Shatabhisha(24)
Jupiter  16      Punarvasu(7), Vishakha(16), P.Bhadrapada(25)
Saturn   19      Pushya(8), Anuradha(17), U.Bhadrapada(26)
Mercury  17      Ashlesha(9), Jyeshtha(18), Revati(27)

TOTAL = 120 YEARS

SEQUENCE: Ke → Ve → Su → Mo → Ma → Ra → Ju → Sa → Me → (repeat)

AD FORMULA: AD_years = (AD_lord_years / 120) × MD_lord_years
```

```mermaid
flowchart TD
    subgraph "⏱️ 5-LAYER DASHA READING PROTOCOL"
        MD["Active MAHADASHA Lord\n(Sets the SEASON / Theme)"]
        AD["Active ANTARDASHA Lord\n(Triggers specific EVENTS)"]

        L1D["LAYER 1 — HOUSES OWNED\nMD lord rules which houses?\n→ Those house themes ACTIVATE\nEx: Mercury MD → H6+H9 themes"]
        L2D["LAYER 2 — HOUSE OCCUPIED\nWhere is the MD lord sitting?\n→ WHERE events play out\nEx: Mercury in H1 → self-reinvention"]
        L3D["LAYER 3 — DIGNITY\nExalted/own = full expression\nCombust = severely reduced\nRetrograde = internalized/delayed"]
        L4D["LAYER 4 — ASPECTS\nBenefic aspects on MD lord?\n→ Support & grace\nMalefic aspects?\n→ Obstacles & pressure"]
        L5D["LAYER 5 — D9 STATUS\nD9 dignity of MD lord?\n→ Inner quality of the period\nD9 strong = inner fulfillment\nD9 weak = outer gain, inner void"]

        MD --> L1D & L2D & L3D & L4D & L5D
        AD -->|"Triggers specific event\nwithin MD theme"| L1D

        COMBINE["🎯 COMBINED READING\nMD = The Season (Career? Love? Wealth?)\nAD = The Weather (specific event/month)\nExample: Mercury MD + Saturn AD\n= Fortune (H9) + Career (H10)\n= Career pinnacle through\nstrategic structured effort"]

        L1D & L2D & L3D & L4D & L5D --> COMBINE
    end

    style MD fill:#0053e2,color:#fff
    style AD fill:#ffc220,color:#000
    style COMBINE fill:#2a8703,color:#fff
```

---

## 📋 CHEAT SHEET 5 — Aspect Quick Reference

```
PLANET        ASPECTS HOUSES (from its position)
─────────────────────────────────────────────────
Sun           7th
Moon          7th
MARS          4th,  7th,  8th      ← 3 aspects!
Mercury       7th
JUPITER       5th,  7th,  9th      ← 3 aspects!
Venus         7th
SATURN        3rd,  7th,  10th     ← 3 aspects!
Rahu/Ketu     7th (standard view)

MEMORY AID:
  Mars    = "forward warrior" → 4, 7, 8 (aggressive reach)
  Jupiter = "wise teacher"   → 5, 7, 9 (trikona reach = grace)
  Saturn  = "slow builder"   → 3, 7, 10 (upachaya reach = structure)
```

---

## 📋 CHEAT SHEET 6 — Combustion Orbs

```
PLANET     ORB (degrees from Sun)    RETROGRADE ORB
Moon       12°                       (never retrograde)
Mercury    14°                       13°
Venus      10°                       8°
Mars       17°                       17°
Jupiter    11°                       11°
Saturn     15°                       15°
Rahu/Ketu  CANNOT be combust (mathematical points)

FORMULA: |Planet° − Sun°| < Orb → COMBUST
  Use circular distance: if diff > 180°, use 360° − diff
```

```mermaid
graph LR
    subgraph "🔥 COMBUSTION ORBS — Distance from Sun"
        SUN["☀️ SUN\n(0°)"]
        MO_C["🌙 Moon\n±12°"]
        ME_C["☿ Mercury\n±14° (13° retro)"]
        VE_C["♀ Venus\n±10° (8° retro)"]
        MA_C["♂ Mars\n±17°"]
        JU_C["♃ Jupiter\n±11°"]
        SA_C["♄ Saturn\n±15°"]
        RK_C["☊☋ Rahu/Ketu\nCANNOT be combust\n(mathematical points)"]

        SUN --- MA_C
        SUN --- ME_C
        SUN --- SA_C
        SUN --- MO_C
        SUN --- JU_C
        SUN --- VE_C
        SUN --- RK_C
    end

    WARN["⚠️ IMPACT RANKING:\nCombust Jupiter = most damaging\nCombust Venus = very harmful\nCombust Mercury = very common (≤28° from Sun)\n  but less severe than Jupiter/Venus"]

    style SUN fill:#ffc220,color:#000
    style MA_C fill:#ea1100,color:#fff
    style JU_C fill:#ffc220,color:#000
    style VE_C fill:#6f42c1,color:#fff
    style RK_C fill:#333,color:#fff
    style WARN fill:#ffd5d5,color:#000
```

---

## 📋 CHEAT SHEET 7 — Mangal Dosha + Cancellations

```
DOSHA HOUSES for Mars: H1, H2, H4, H7, H8, H12
CHECK FROM: Lagna, Moon, Venus (all three!)

CANCELLATIONS (any ONE = cancelled):
  ✅ Mars in own sign (Aries/Scorpio)
  ✅ Mars in exaltation (Capricorn)
  ✅ Jupiter aspects Mars
  ✅ Mars conjunct Jupiter or waxing Moon
  ✅ Mars in H1 for Aries/Leo/Sagittarius Lagna
  ✅ Mars in H2 for Gemini/Virgo Lagna
  ✅ Mars in H4 for Scorpio/Cancer Lagna
  ✅ Mars in H7 for Cancer/Capricorn Lagna
  ✅ Mars in H8 for Sagittarius/Pisces Lagna
  ✅ Mars in H12 for Taurus/Libra Lagna
  ✅ Partner also Manglik
```

---

## 📋 CHEAT SHEET 8 — Yoga Karaka by Lagna

```
LAGNA       YOGA KARAKA    HOUSES OWNED    WHY
Aries       Saturn         H10 + H11...   wait, H9+H10 ✓ Kendra+Trikona
Taurus      Saturn         H9 + H10       Trikona + Kendra
Cancer      Mars           H5 + H10       Trikona + Kendra
Leo         Mars           H4 + H9        Kendra + Trikona
Libra       Saturn         H4 + H5        Kendra + Trikona
Capricorn   Venus          H5 + H10       Trikona + Kendra
Aquarius    Venus          H4 + H9        Kendra + Trikona

NO YOGA KARAKA: Gemini, Virgo, Scorpio, Sagittarius, Pisces
  For these: identify the MOST BENEFIC by Trikona lordship (H5 or H9 lord)
```

---

## 📋 CHEAT SHEET 9 — Navamsha (D9) Start Signs

```
D1 SIGN TYPE       D9 STARTS FROM
Movable (1,4,7,10) → Aries      (Cardinal: Ar/Ca/Li/Cp)
Fixed   (2,5,8,11) → Capricorn  (Stable: Ta/Le/Sc/Aq)
Dual    (3,6,9,12) → Libra      (Mutable: Ge/Vi/Sg/Pi)

FORMULA:
  pada_index = FLOOR(degree_in_sign / 3.3333)   [0–8]
  D9_sign = (start_index + pada_index) MOD 12
  Map: 0=Ar, 1=Ta, 2=Ge, 3=Ca, 4=Le, 5=Vi, 6=Li, 7=Sc, 8=Sg, 9=Cp, 10=Aq, 11=Pi
```

---

## 📝 ROUGH NOTES — Expert Rules to Internalize

### The "Golden Rules" — Memorize These

```
1. "Exalted ≠ always good. Exalted in H6/H8/H12 = restricted."
2. "Debilitated ≠ always bad. Debilitated + retrograde ≈ exalted."
3. "Combust = #1 strength-reducer. Always check before declaring yogas."
4. "Natural benefic as Kendra-ONLY lord = Kendradhipati Dosha."
5. "H1 is BOTH Kendra AND Trikona — the single most powerful house."
6. "Trikona lordship overrides Maraka/Dusthana lordship."
7. "D9 is the tiebreaker — when D1 is ambiguous, D9 resolves."
8. "Dasha of a planet in H6/H8/H12 ≠ bad IF it also rules a Trikona."
9. "Jupiter's 5th and 9th aspects protect everything they touch."
10. "Saturn's 10th aspect structures and delays but doesn't destroy."
```

### The "Trap Rules" — Things That Catch Experts Too

```
1. "Yoga exists on paper ≠ yoga manifests."
   → Check: Is the yoga planet's Dasha within the native's lifetime?
   → Venus MD starting at age 85 = theoretical, not practical.

2. "Functional malefic in dusthana CAN be good (Viparita Raja Yoga)."
   → H8 lord in H12 = losses prevent death = PROTECTION.

3. "Retrograde planet in D9 exaltation = extraordinary inner resources."
   → Saturn retrograde + D9 exalted = invincible inner discipline.

4. "Parivartana (sign exchange) = planets act as if in own sign."
   → H9 lord in H10 + H10 lord in H9 = SUPREME Raja Yoga.

5. "Moon sign matters more for transits than Lagna."
   → All Gochara predictions START from Moon, then confirm from Lagna.
```

### The "Sequence of Importance" — What to Read First

```
PRIORITY ORDER in chart reading:
  1st: Lagna lord — sets the life direction
  2nd: Moon sign + nakshatra — emotional and mental foundation
  3rd: Yoga Karaka planet — the fortune-engine
  4th: Strongest yoga — the chart's gift
  5th: Weakest planet / area — the chart's challenge
  6th: Current Dasha — what's happening NOW
  7th: D9 Venus — marriage truth
  8th: Transits — what's triggering events

If you only have 5 minutes, read #1 through #5.
If you have 30 minutes, cover all 8.
```

```mermaid
flowchart TD
    START["📋 NEW CHART — Where to BEGIN?"]

    P1["1️⃣ LAGNA LORD\nWhat sign? What house?\nDignified? Combust?\n→ Sets primary life direction"]
    P2["2️⃣ MOON\nSign + Nakshatra\nWaxing or waning?\n→ Emotional foundation\n+ Starting Dasha lord"]
    P3["3️⃣ YOGA KARAKA\nDoes one exist for this Lagna?\nWhere placed? Dignified?\n→ The fortune engine"]
    P4["4️⃣ STRONGEST YOGA\nAny Mahapurusha?\nRaja Yoga? Viparita?\n→ The chart's gift"]
    P5["5️⃣ WEAKEST PLANET\nCombust? Debilitated?\nIn dusthana?\n→ The chart's challenge area"]
    P6["6️⃣ CURRENT DASHA\nMD + AD lords\n5-Layer reading each\n→ What's active NOW?"]
    P7["7️⃣ D9 VENUS\nOwn/exalt = marriage blessed\nDebil = work needed\n→ Marriage deep truth"]
    P8["8️⃣ TRANSITS\nJupiter position from Moon\nSaturn position from Moon\nSade Sati phase?\n→ Current triggers"]

    VERDICT["📖 FINAL VERDICT\n'The chart's signature'\n+ Timing windows\n+ Guidance"]

    START --> P1 --> P2 --> P3 --> P4 --> P5
    P5 -->|"5 min reading stops here"| P5
    P5 --> P6 --> P7 --> P8 --> VERDICT

    style START fill:#0053e2,color:#fff
    style P1 fill:#ea1100,color:#fff
    style P2 fill:#0053e2,color:#fff
    style P3 fill:#2a8703,color:#fff
    style P4 fill:#ffc220,color:#000
    style P6 fill:#6f42c1,color:#fff
    style P7 fill:#6f42c1,color:#fff
    style VERDICT fill:#000,color:#fff
```

---

## 📊 MERMAID DIAGRAM 6 — House Lordship for Capricorn Lagna

```mermaid
graph TD
    subgraph "Capricorn Lagna — Functional Classification"
        SA[♄ Saturn<br/>H1+H2] -->|Lagna Lord| SELF[🟢 Personal Planet]
        VE[♀ Venus<br/>H5+H10] -->|YOGA KARAKA| BEST[⭐ SUPREME BENEFIC]
        ME[☿ Mercury<br/>H6+H9] -->|H9 Trikona| MIXED[🟡 Mixed: H9 good, H6 hard]
        MA[♂ Mars<br/>H4+H11] -->|Kendra+Upachaya| NEUT[🔵 Neutral-Benefic]
        JU[♃ Jupiter<br/>H3+H12] -->|Both challenging| MILD[🟠 Mild Malefic]
        MO[🌙 Moon<br/>H7] -->|Maraka| MARAK[🔴 Maraka Lord]
        SU[☀️ Sun<br/>H8] -->|Dusthana| FUNC[🔴 Functional Malefic]
    end

    style BEST fill:#2a8703,color:#fff
    style SELF fill:#0053e2,color:#fff
    style MARAK fill:#ea1100,color:#fff
    style FUNC fill:#ea1100,color:#fff
```

---

## 📊 MERMAID DIAGRAM 7 — The 3 Lenses of Prediction

```mermaid
flowchart LR
    A[📋 D1 Chart<br/>PROMISE] --> D{All 3<br/>Align?}
    B[🔮 D9 Chart<br/>CONFIRMATION] --> D
    C[⏱️ Dasha + Transit<br/>TIMING] --> D

    D -->|Yes| E[✅ Event WILL<br/>Manifest]
    D -->|Partial| F[⚡ Partial or<br/>Delayed Result]
    D -->|No| G[❌ Promise exists<br/>but won't manifest<br/>in this period]

    style A fill:#0053e2,color:#fff
    style B fill:#ffc220,color:#000
    style C fill:#2a8703,color:#fff
    style E fill:#2a8703,color:#fff
    style G fill:#ea1100,color:#fff
```

---

## 🗓️ STUDY PLANNER — 12-Week Curriculum

| Week | Focus | Read | Practice |
|------|-------|------|----------|
| 1 | Big picture + signs | Part 1 + Cheat Sheet 1 | Memorize 12 signs, lords, elements |
| 2 | Birth data + JD + Ayanamsa | Part 2 (CALC 1-3) | Calculate JD for 3 people |
| 3 | Lagna + Planets + Houses | Part 2 (CALC 4-6) | Assign houses for 2 charts |
| 4 | Nakshatras + Combustion | Part 2 (CALC 6-8) | Find nakshatra for each planet |
| 5 | Dignity + Relationships | Part 3 (Level 1-2) | Write 1-sentence for all planets |
| 6 | Aspects + Conjunctions | Part 3 (Level 3) | Map all aspects for 1 chart |
| 7 | Lordship + Yoga Karaka | Part 3 (Level 3) | Classify all planets for 3 Lagnas |
| 8 | Yoga detection | Part 3 (Level 4) | Find yogas in 2 charts |
| 9 | D9 cross-reference | Part 3 (Level 5) | Compare D1 vs D9 for all planets |
| 10 | Dasha + Timing | Part 3 (Level 6) | Calculate dasha balance for 2 charts |
| 11 | Full synthesis | Part 3 (Level 7) + Part 4 | Write full reading for 1 chart |
| 12 | Comparison + Review | Part 4 (all examples) | Compare 2 charts side-by-side |

---

📌 **End of Part 5 — Learning Guide Complete!**

**Full Learning Guide Index**:
| Part | Title | Focus |
|------|-------|-------|
| [Part 1](Jyotish_Learning_Part1_Structure.md) | Curriculum Structure | Big picture, modules, milestones, axioms |
| [Part 2](Jyotish_Learning_Part2_Calculations.md) | Calculation Engine | 15 calc steps with I/O and formulas |
| [Part 3](Jyotish_Learning_Part3_Interpretations.md) | Interpretation | 7 levels from simple to synthesis |
| [Part 4](Jyotish_Learning_Part4_Examples.md) | Worked Examples | Multi-chart comparisons + exercises |
| **Part 5** | **Reference** | **Mermaid diagrams, cheat sheets, study plan** |

---
*Jyotisha Vidyā Learning Guide · Part 5 of 5 · Created April 2026*
*"Jyotiṣam eka-cakṣuḥ Vedānām" — Astrology is the single eye of the Vedas*
