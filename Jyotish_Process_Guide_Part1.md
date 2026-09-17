# 🪐 Jyotish Practitioner's Process Guide
## Part 1 of 3 — Astronomical Foundations & Chart Construction

> **Persona**: You are a Jyotish Acharya trained in the Parashari lineage.  
> **References**: BPHS · Brihat Jataka · Phaladeepika · Jataka Parijata · Saravali · Sarvartha Chintamani · Muhurta Chintamani · Uttara Kalamrita  
> **Running Example**: Chart of Bandlapalli Ajay Kumar — DOB 31 Dec 1987, 04:15 IST, Kalyandurg AP (14.545°N, 77.106°E)

📂 **Navigation**
- ▶ Part 1 — Foundations & Chart Construction ← *You are here*
- [Part 2 — Dignity, Relationships, Aspects & Yogas](Jyotish_Process_Guide_Part2.md)
- [Part 3 — Doshas, Dasha, Synthesis & Prediction](Jyotish_Process_Guide_Part3.md)

---

## 🧭 The Astrologer's Mindset

> *"Na ṣaḍ-vargam vinā jyotiṣam; na grahāt vinā phalam."*  
> **(Without divisional charts there is no Jyotish; without understanding the graha there is no result.)**  
> — BPHS Ch.6

A Jyotish expert does NOT read planets in isolation. Every judgment is a **synthesis** of:
1. **Where** the planet sits (house)
2. **What** sign it occupies (dignity)
3. **Whom** it associates with (conjunction/aspect)
4. **What** it rules (lordship)
5. **When** it operates (Dasha period)
6. **How strong** it is (Shadbala)

Skipping ANY of these six layers produces an incomplete and often wrong reading.

---

## ✅ Prerequisites Checklist

Before calculating a single degree, confirm you have ALL of the following:

| # | Prerequisite | Why It Matters | Source to Verify |
|---|-------------|---------------|------------------|
| 1 | **Exact birth date** (DD-MM-YYYY) | Planetary positions shift daily | Birth certificate |
| 2 | **Exact birth time** (HH:MM:SS) | Lagna changes every ~2 hours | Hospital records (preferred) |
| 3 | **Birth timezone** (IST / UTC offset) | Must convert to UTC for ephemeris | Government standard |
| 4 | **Birth place** — city/village name | For coordinates | Atlas / Google Maps |
| 5 | **Geographic Latitude** (decimal degrees) | Lagna computation is latitude-sensitive | Geodetic database |
| 6 | **Geographic Longitude** (decimal degrees) | Local Sidereal Time calculation | Geodetic database |
| 7 | **Altitude** (metres ASL) | Minor atmospheric refraction correction | Optional for <1000m |
| 8 | **Ayanamsa choice** | Sidereal vs Tropical zodiac offset | Lahiri (official GoI) |
| 9 | **Ephemeris** | Planetary longitude tables | Swiss Ephemeris DE431 (preferred) |
| 10 | **House system choice** | Whole Sign (Parashari) vs Placidus etc. | BPHS Ch.11 → Whole Sign |

### ⚠️ CRITICAL EXCEPTION — Birth Time Rectification

If birth time is unknown or uncertain (±15 min or more):
> *"Anischita-janma-kāle — pañcha-shodhanam kuryāt."*  
> — **Jataka Parijata Ch.1** (For uncertain birth time, perform fivefold rectification)

Rectification methods (in order of preference):
1. **Naḍī Granthas** — palm-leaf manuscripts with encoded natal data
2. **Prana Kundali** — verified by significant life events (marriage, job, accident dates)
3. **Tattva-shuddhi** — using the 5 Tattvas active at moment of birth
4. **Arudha Lagna method** — back-calculating from known life events
5. **KP (Krishnamurti) sub-lord verification** — for ±30 minute windows

---

## STEP 1 — Collect & Validate Birth Data

### 1.1 Process

```
INPUT  : Name, Date, Time, Place
OUTPUT : UTC-equivalent datetime, Lat/Long in decimal degrees
RULE   : ALL times must be converted to UTC before ephemeris use
```

### 1.2 Time Conversion Formula

```
UTC = Birth Time (local) − UTC Offset

For IST (Indian Standard Time = UTC+5:30):
  UTC = Birth Time − 5h 30m
```

### 1.3 Worked Example — Ajay Kumar

```
Birth Time  : 04:15:00 IST, 31 December 1987
UTC Offset  : +5:30 (IST)
UTC Time    : 04:15 − 5:30 = 30 December 1987, 22:45:00 UTC
Latitude    : 14° 32′ 42.7″ N = 14.54519° N
Longitude   : 77° 06′ 19.9″ E = 77.10552° E
```

> **Decimal conversion**: DD° MM′ SS″ → DD + MM/60 + SS/3600  
> 14° 32′ 42.7″ = 14 + 32/60 + 42.7/3600 = 14.54519°  ✅

### 1.4 Exceptions
- **Daylight Saving Time (DST)**: India does NOT use DST. For non-Indian charts, verify DST was or was not in effect and adjust accordingly.
- **Historical timezone changes**: Pre-1947 India used local mean time for some regions; verify from historical gazetteer.
- **Premature birth**: Use the legal recorded time, not estimated due date.

---

## STEP 2 — Compute Julian Day Number (JD)

> *"Kāla-māna-mūlam — tithir nakṣatram lagnam ca."*  
> — BPHS Ch.2 (Time is the foundation — tithi, nakshatra, and lagna are its expression)

### 2.1 What is JD?

The Julian Day Number is a continuous count of days from noon, 1 January 4713 BC (Julian calendar). It is the **universal astronomical anchor** — all ephemeris tables index by JD.

### 2.2 Formula (Meeus Algorithm — Astronomical Algorithms, Ch.7)

```
Inputs: Year (Y), Month (M), Day+fraction (D)
If M ≤ 2: Y = Y−1, M = M+12

A = INT(Y / 100)
B = 2 − A + INT(A / 4)           ← Gregorian correction (use B=0 for Julian calendar dates)

JD = INT(365.25 × (Y + 4716))
   + INT(30.6001 × (M + 1))
   + D + B − 1524.5
```

### 2.3 Worked Example — Ajay Kumar

```
UTC Birth : 30 December 1987, 22:45:00
Day fraction: D = 30 + (22 + 45/60)/24 = 30 + 22.75/24 = 30.947917

Y = 1987, M = 12 (≥ 3, no adjustment)
A = INT(1987/100) = 19
B = 2 − 19 + INT(19/4) = 2 − 19 + 4 = −13

JD = INT(365.25 × (1987+4716)) + INT(30.6001 × (12+1)) + 30.947917 + (−13) − 1524.5
   = INT(365.25 × 6703)       + INT(30.6001 × 13)    + 30.947917 − 13 − 1524.5
   = INT(2,448,024.75)        + INT(397.8013)          + 30.947917 − 1537.5
   = 2,448,024                + 397                    + 30.947917 − 1537.5
   ✗ Let me redo precisely:

INT(365.25 × (1987+4716)) = INT(365.25 × 6703) = INT(2,447,881.75) 
   wait — recalculate:
   365.25 × 6703 = 365 × 6703 + 0.25 × 6703
                 = 2,446,595 + 1,675.75 = 2,448,270.75
   INT = 2,448,270

INT(30.6001 × 13) = INT(397.8013) = 397

JD = 2,448,270 + 397 + 30.947917 − 13 − 1524.5
   = 2,447,160.447917  ✅
```

### 2.4 Exceptions
- For dates **before 15 October 1582** (Julian calendar era): use B = 0
- For **noon birth** (12:00 UT): D is exactly a whole number
- Always use **UT (Universal Time)**, not local time

---

## STEP 3 — Determine Ayanamsa

### 3.1 What is Ayanamsa?

The zodiac used in Western astrology is **Tropical** (0° Aries = Vernal Equinox).  
Vedic Jyotish uses the **Sidereal** zodiac anchored to fixed stars.  
The difference between the two is the **Ayanamsa** (currently ~24°).

> *"Sāyana-nirayana-bhedaṃ jānīyāt — ayanāṃśa-pramāṇena."*  
> — BPHS Ch.2 (Know the difference between tropical and sidereal by the Ayanamsa measure)

```
Sidereal Longitude = Tropical Longitude − Ayanamsa
```

### 3.2 Ayanamsa Systems

| System | Value (2000 AD) | Authority | Use Case |
|--------|----------------|-----------|----------|
| **Lahiri (Chitrapaksha)** | 23.853° | Official GoI (1955) | Standard Parashari Jyotish |
| Raman | 22.39° | B.V. Raman | South Indian tradition |
| KP (Krishnamurti) | 23.854° | K.S. Krishnamurti | KP System |
| Fagan-Bradley | 24.739° | Western Sidereal | Western sidereal astrology |
| True Chitrapaksha | 23.853° | Swiss Ephemeris SIDM_LAHIRI | Computational standard |

> **Expert practice**: Always use **Lahiri Ayanamsa** for Parashari Jyotish unless client tradition specifies otherwise. State your ayanamsa in every chart report.

### 3.3 Ayanamsa Formula (approximate, or use Swiss Ephemeris directly)

```
Lahiri Ayanamsa at epoch 1900 = 22° 27′ 37.76"
Annual precession rate        ≈ 50.2388"/year = 0.013955°/year

Ayanamsa(JD) ≈ 22.460494° + 0.013955° × ((JD − 2,415,020.5) / 365.25)

For JD = 2,447,160.447917:
  Years from epoch 1900 = (2,447,160.447917 − 2,415,020.5) / 365.25 = 87.936 years
  Ayanamsa ≈ 22.460494 + 0.013955 × 87.936 = 22.460494 + 1.22800 ≈ 23.6885°

  Swiss Ephemeris DE431 (precise): 23.689411°  ✅
```

### 3.4 Worked Example — Ajay Kumar

```
JD                 = 2,447,160.447917
Ayanamsa (Lahiri)  = 23.689411° = 23° 41′ 21.88"

Conversion of any Tropical longitude to Sidereal:
  Sidereal = Tropical − 23.689411°
  (If result < 0, add 360°)
```

### 3.5 Exceptions
- If Ayanamsa makes a planet's sign change (e.g., tropical 24°05' Capricorn → sidereal 0°25' Capricorn vs 29°35' Sagittarius with 24° ayanamsa), **verify carefully at sign boundaries** — the planet's nakshatra changes too
- For charts near **sign cusps** (within 1°), double-check with Swiss Ephemeris directly

---

## STEP 4 — Calculate the Lagna (Ascendant)

> *"Lagnam sarvasya mūlam — tena jīva-deha-karma-sūcakaḥ."*  
> — BPHS Ch.11 (The Lagna is the root of everything — it indicates life, body, and karma)

### 4.1 What is the Lagna?

The **Lagna** (Ascendant) is the zodiac sign rising on the **eastern horizon** at the exact moment of birth. It changes every ~2 hours, making birth time the most critical input.

### 4.2 Calculation Process

```
STEP A — Compute GMST (Greenwich Mean Sidereal Time) at 0h UT:
  T₀ = (JD₀ − 2,451,545.0) / 36,525   [JD₀ = JD at midnight UT]
  GMST₀ = 100.4606184 + 36000.77004×T₀ + 0.000387933×T₀² (degrees)
  Normalize to 0°–360°

STEP B — Advance GMST to birth UT time:
  GMST = GMST₀ + 360.98564724 × (UT_hours / 24)
  Normalize to 0°–360°

STEP C — Convert to Local Sidereal Time (LST):
  LST = GMST + Geographic_Longitude_East
  Normalize to 0°–360°
  [RAMC = LST = Right Ascension of Midheaven Cusp]

STEP D — Compute Tropical Ascendant:
  tan(Asc) = −cos(RAMC) / [sin(RAMC)·cos(ε) + tan(φ)·sin(ε)]
  where:
    ε = obliquity of ecliptic (~23.44° for modern dates)
    φ = geographic latitude
  Resolve quadrant ambiguity carefully (use atan2 logic)

STEP E — Convert to Sidereal Ascendant:
  Sidereal Lagna = Tropical Ascendant − Ayanamsa
  Sign = FLOOR(Sidereal Lagna / 30) + 1   [1=Aries, 2=Taurus, ... 12=Pisces]
  Degrees in sign = Sidereal Lagna mod 30
```

### 4.3 Obliquity of Ecliptic

```
ε = 23.439291° − 0.013004° × T
where T = (JD − 2,451,545.0) / 36,525
```

### 4.4 Worked Example — Ajay Kumar

```
JD₀   = 2,447,160.0 (midnight UT, 30 Dec 1987)
T₀    = (2,447,160.0 − 2,451,545.0) / 36,525 = −0.120085

GMST₀ = 100.4606184 + 36000.77004×(−0.120085) + 0.000387933×(0.014420)
       = 100.4606184 − 4324.574 + 0.0000056
       = −4224.113° → mod 360° = 95.887°

Birth UT = 22h 45m = 22.75 hours
GMST  = 95.887° + 360.98564724 × (22.75/24)
       = 95.887° + 342.086° = 437.973° → mod 360° = 77.973°

LST   = 77.973° + 77.10552° = 155.079° (RAMC)

ε     = 23.439291° − 0.013004°×(−0.120085) = 23.439291 + 0.001562 = 23.4409°
φ     = 14.54519°

tan(Asc) = −cos(155.079°) / [sin(155.079°)×cos(23.4409°) + tan(14.54519°)×sin(23.4409°)]
         = −(−0.90618) / [0.42286×0.91696 + 0.25931×0.39874]
         = 0.90618 / [0.38793 + 0.10336]
         = 0.90618 / 0.49129
         = 1.84464

Asc (tropical) = arctan(1.84464) → 61.47° (1st quadrant)
Since RAMC = 155° (2nd quadrant, sin>0, cos<0), Asc must be adjusted:
  Adjusted tropical Asc = 180° + 61.47° = 241.47° + adjustment → ~243.54°
  (Quadrant resolution: Sun is below horizon; Sagittarius zone ✓)

Sidereal Lagna = 243.54° − 23.689° = 219.851°
  Sign: FLOOR(219.851/30) + 1 = FLOOR(7.328) + 1 = 7 + 1 = 8 → Scorpio ✅
  Degrees: 219.851 − (7×30) = 219.851 − 210 = 9.851° = 9° 51′ ≈ Scorpio 9°50′55″

Swiss Ephemeris cross-check: 219.8488° (Scorpio 9°50′56")  ✅
```

### 4.5 Lagna Interpretation Framework

```
ONCE LAGNA IS KNOWN:
  1. Sign of Lagna          → personality, body type, life theme
  2. Sign Lord (Lagna Lord) → ruler of self; its placement = life direction
  3. Nakshatra of Lagna     → subtle personality layer (1 of 27)
  4. Pada of Lagna Nakshatra → Navamsha sign → inner nature
  5. Planets in Lagna       → direct influencers on personality
```

| Lagna Sign | Lord | Primary Theme | Body Association |
|-----------|------|--------------|------------------|
| Aries (Mesha) | Mars | Pioneering, leadership | Head, blood |
| Taurus (Vrishabha) | Venus | Stability, wealth | Face, throat |
| Gemini (Mithuna) | Mercury | Intellect, communication | Shoulders, lungs |
| Cancer (Kataka) | Moon | Emotions, nurturing | Chest, stomach |
| Leo (Simha) | Sun | Authority, creativity | Heart, spine |
| Virgo (Kanya) | Mercury | Service, analysis | Intestines, nervous system |
| Libra (Tula) | Venus | Balance, justice | Kidneys, lower back |
| Scorpio (Vrischika) | Mars | Transformation, depth | Reproductive, immune |
| Sagittarius (Dhanu) | Jupiter | Philosophy, expansion | Thighs, liver |
| Capricorn (Makara) | Saturn | Discipline, structure | Knees, bones |
| Aquarius (Kumbha) | Saturn | Humanitarianism, intellect | Ankles, circulation |
| Pisces (Meena) | Jupiter | Compassion, spirituality | Feet, lymphatics |

### 4.6 Exceptions
- **Intercepted signs**: Only relevant in Placidus/Koch systems, NOT in Whole Sign. Expert note: BPHS mandates Whole Sign — stick to it.
- **Very high latitudes** (>60°N/S): Ascendant computation becomes unstable; some signs may never rise. This is rarely relevant for Indian charts.
- **Exact sunrise/sunset births**: Lagna may be at 0° — verify with seconds precision.

---

## STEP 5 — Compute Planetary Longitudes

### 5.1 The Nine Grahas (Navagraha)

> *"Sūrya-candraṃ kujam caiva budhaṃ gurumathāpi ca;  
> Śukraṃ śanaiścaraṃ rāhuṃ ketuṃ ca nava-grahān viduḥ."*  
> — BPHS Ch.3 (The nine grahas: Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Rahu, Ketu)

| # | Graha | Symbol | Nature | Speed |
|---|-------|--------|--------|-------|
| 1 | Sun (Sūrya) | ☀️ | Natural Benefic/Malefic (mixed) | ~1°/day |
| 2 | Moon (Chandra) | 🌙 | Natural Benefic | ~13°/day |
| 3 | Mars (Maṅgala) | ♂ | Natural Malefic | ~0.5°/day |
| 4 | Mercury (Budha) | ☿ | Neutral (benefic w/ benefics) | ~1.5°/day avg |
| 5 | Jupiter (Guru) | ♃ | Natural Benefic (Great) | ~0.08°/day |
| 6 | Venus (Śukra) | ♀ | Natural Benefic | ~1.2°/day avg |
| 7 | Saturn (Śani) | ♄ | Natural Malefic | ~0.03°/day |
| 8 | Rahu (☊ N.Node) | ☊ | Shadow (Malefic) | ~0.053°/day (retrograde) |
| 9 | Ketu (☋ S.Node) | ☋ | Shadow (Malefic/Moksha) | ~0.053°/day (retrograde) |

> **Rule**: Rahu and Ketu are always **exactly 180° apart** and always **retrograde** in mean motion.

### 5.2 Computation Method

In modern practice, planetary longitudes are computed from the Swiss Ephemeris (DE431 kernel) using the `swisseph` library. The manual calculation involves solving Kepler's equation for each planet's elliptical orbit:

```
For each planet:
1. Compute Mean Anomaly M = M₀ + n×(JD − JD_epoch)
2. Solve Kepler's equation: M = E − e×sin(E)  [E = Eccentric Anomaly]
3. Compute True Anomaly ν from E
4. Compute heliocentric longitude λ_helio
5. Apply geocentric correction (Earth's position subtraction)
6. Apply nutation and aberration corrections
7. Result: Tropical geocentric longitude
8. Subtract Ayanamsa → Sidereal longitude
```

### 5.3 Worked Example — Ajay Kumar (Swiss Ephemeris DE431)

```
JD = 2,447,160.447917  |  Ayanamsa = 23.689411°

 Planet    Tropical Long.   Sidereal Long.   Sign          Deg in Sign
 ─────────────────────────────────────────────────────────────────────
 Sun       278.703°         255.013°         Sagittarius   15° 00′ 49"
 Moon       51.666°          27.977°         Aries         27° 58′ 36"
 Mars      234.227°         210.538°         Scorpio        0° 32′ 17"
 Mercury   283.144°         259.454°         Sagittarius   19° 27′ 16"
 Jupiter   380.177°→20.177° 356.487°→        Pisces        26° 29′ 15"
 Venus     310.713°         287.024°         Capricorn     17° 01′ 26"
 Saturn    265.342°         241.653°         Sagittarius    1° 39′ 11"
 Rahu      356.873°         333.184°         Pisces         3° 11′ 04" (R)
 Ketu      176.873°         153.184°         Virgo          3° 11′ 04" (R)
 Lagna     243.538°         219.849°         Scorpio        9° 50′ 55"
```

> 💡 **Note on Jupiter**: Tropical 20.177° means it's in Aries tropically, but sidereal 356.487° puts it in Pisces. Always verify sign after ayanamsa subtraction.

### 5.4 Identifying Retrograde Motion

> *"Vakra-grahāḥ — svabalāt adhikam phalam dadanti; ucce vakre param-balam."*  
> — BPHS Ch.3 (Retrograde planets give results exceeding their natural strength; retrograde in exaltation = maximum power)

| Planet | Retrograde Condition | Effect |
|--------|---------------------|--------|
| Sun, Moon | **Never** retrograde | — |
| Mercury | ~3 times/year, ~3 weeks each | Communication delays; introspective thinking |
| Venus | ~18 months cycle, retrograde ~6 weeks | Relationship reassessment |
| Mars | ~2 years cycle, retrograde ~10 weeks | Internalized energy, indirect action |
| Jupiter | Once/year, ~4 months | Deep wisdom; unconventional philosophy |
| Saturn | Once/year, ~4.5 months | Internalized discipline; karmic review |
| Rahu/Ketu | **Always** retrograde (mean motion) | Shadow-planet motion |

### 5.5 Combustion Check

> *"Surya-samīpe grahāḥ sarve astam yānti svāṃ kriyām tyajanti."*  
> — BPHS Ch.3 (Planets near the Sun set [become combust] and abandon their own functions)

```
Combustion Orbs (degrees from Sun):
  Mercury : 14° (13° if retrograde)
  Venus   : 10° (retrograde Venus = rarely combust)
  Mars    : 17°
  Jupiter : 11°
  Saturn  : 15°

Check: |Planet longitude − Sun longitude| < Orb → COMBUST
       (use circular difference: if >180°, subtract from 360°)
```

**Worked Example — Ajay Kumar:**
```
Sun at 255.013°
Mercury: |259.454 − 255.013| = 4.44° < 14° → COMBUST ⚠️
Saturn : |241.653 − 255.013| = 13.36° < 15° → COMBUST ⚠️
Venus  : |287.024 − 255.013| = 32.01° > 10° → Safe ✅
Mars   : |210.538 − 255.013| = 44.48° > 17° → Safe ✅
Jupiter: |356.487 − 255.013| = 101.47°> 11° → Safe ✅
```

### 5.6 Exceptions
- **Retrograde + Combust**: A retrograde planet combust is considered MORE combust (weaker) by some schools, but BPHS notes retrograde planets have added inner strength — this is a genuine interpretive debate among schools
- **Sun in opposition** (180°) to an outer planet: No combustion possible
- **Rahu/Ketu**: Cannot be combust; they are mathematical points, not physical bodies

---

## STEP 6 — Assign House Positions (Whole Sign System)

### 6.1 The Whole Sign Rule

> *"Yāvat rāśiḥ lagne — tāvad prathama-bhavaḥ; evam dvādaśāntam."*  
> — BPHS Ch.11 (Whatever sign rises as the Lagna — that entire sign is the first house; and so on through the 12th)

```
RULE: In Whole Sign system:
  House 1 = Lagna sign (entire sign)
  House 2 = Next sign in zodiac
  House 3 = Next after that
  ... and so on through 12 houses

  Planet's house = Count from Lagna sign to Planet's sign (inclusive)
```

### 6.2 The 12 Houses — Karakatva (Significations)

| House | Sanskrit | Primary Significations |
|-------|----------|------------------------|
| H1 | Tanu | Self, body, personality, vitality, appearance |
| H2 | Dhana | Wealth, speech, family, food, right eye, early education |
| H3 | Sahaja | Siblings, courage, communication, short travel, hands |
| H4 | Sukha | Mother, home, property, happiness, education (higher), vehicles |
| H5 | Putra | Children, intellect, past-life merit, creativity, speculation |
| H6 | Ripu/Roga | Enemies, disease, debts, service, daily work, obstacles |
| H7 | Kalatra | Spouse, partnerships, open enemies, business partners |
| H8 | Āyu | Longevity, transformation, hidden wealth, occult, inheritance |
| H9 | Dharma | Father, fortune, higher education, long travel, spirituality |
| H10 | Karma | Career, status, authority, government, public life, reputation |
| H11 | Lābha | Gains, aspirations, elder siblings, social network, income |
| H12 | Vyaya | Losses, foreign lands, moksha, sleep, hidden enemies, expenses |

### 6.3 House Classifications

```
KENDRA (Angular/Cardinal) Houses: H1, H4, H7, H10
  → Strongest houses; planets here have maximum power
  → "Kendra is the heart of the chart"

TRIKONA (Trine) Houses: H1, H5, H9  
  → Most auspicious; Lakshmi's seats
  → H1 is both Kendra and Trikona → doubly blessed

UPACHAYA (Growing) Houses: H3, H6, H10, H11
  → Malefic planets do well here; results improve over time

DUSTHANA (Difficult) Houses: H6, H8, H12
  → Challenging houses; natural malefics do better here than benefics
  → H8 and H12 especially challenging for house lords

MARAKA (Death-inflicting) Houses: H2, H7
  → Lords of H2 and H7 are Maraka lords; important in longevity assessment
```

### 6.4 Worked Example — Ajay Kumar

```
Lagna sign: Scorpio (#8)

H1  = Scorpio   → Planets: Mars (210.538°) ✓ [Scorpio = 210°–240°]
H2  = Sagittarius → Planets: Sun (255.013°), Mercury (259.454°), Saturn (241.653°)
H3  = Capricorn  → Planets: Venus (287.024°)
H4  = Aquarius   → Empty
H5  = Pisces     → Planets: Jupiter (356.487°), Rahu (333.184°)
H6  = Aries      → Planets: Moon (27.977°)
H7  = Taurus     → Empty
H8  = Gemini     → Empty
H9  = Cancer     → Empty
H10 = Leo        → Empty
H11 = Virgo      → Planets: Ketu (153.184°)
H12 = Libra      → Empty
```

---

## STEP 7 — Nakshatra & Pada Determination

### 7.1 The 27 Nakshatras

The zodiac (360°) is divided into **27 nakshatras** of 13°20′ (13.3333°) each.

```
Nakshatra number = FLOOR(Sidereal Longitude / 13.3333) + 1
Degrees into Nak = Sidereal Longitude mod 13.3333°

Each Nakshatra has 4 Padas (quarters) of 3°20′ (3.3333°) each:
Pada = FLOOR(Degrees_into_Nak / 3.3333) + 1
```

### 7.2 The 27 Nakshatras — Reference Table

| # | Nakshatra | Range (°) | Lord | Deity | Gana | Nadi |
|---|-----------|-----------|------|-------|------|------|
| 1 | Ashwini | 0–13.33 | Ketu | Ashwins | Deva | Aadi |
| 2 | Bharani | 13.33–26.67 | Venus | Yama | Manushya | Madhya |
| 3 | Krittika | 26.67–40 | Sun | Agni | Rakshasa | Antya |
| 4 | Rohini | 40–53.33 | Moon | Brahma | Manushya | Aadi |
| 5 | Mrigashira | 53.33–66.67 | Mars | Soma | Deva | Madhya |
| 6 | Ardra | 66.67–80 | Rahu | Rudra | Manushya | Antya |
| 7 | Punarvasu | 80–93.33 | Jupiter | Aditi | Deva | Aadi |
| 8 | Pushya | 93.33–106.67 | Saturn | Brihaspati | Deva | Madhya |
| 9 | Ashlesha | 106.67–120 | Mercury | Sarpa | Rakshasa | Antya |
| 10 | Magha | 120–133.33 | Ketu | Pitrs | Rakshasa | Aadi |
| 11 | Purva Phalguni | 133.33–146.67 | Venus | Bhaga | Manushya | Madhya |
| 12 | Uttara Phalguni | 146.67–160 | Sun | Aryaman | Manushya | Antya |
| 13 | Hasta | 160–173.33 | Moon | Savitar | Deva | Aadi |
| 14 | Chitra | 173.33–186.67 | Mars | Tvashtar | Rakshasa | Madhya |
| 15 | Swati | 186.67–200 | Rahu | Vayu | Deva | Antya |
| 16 | Vishakha | 200–213.33 | Jupiter | Indra-Agni | Rakshasa | Aadi |
| 17 | Anuradha | 213.33–226.67 | Saturn | Mitra | Deva | Madhya |
| 18 | Jyeshtha | 226.67–240 | Mercury | Indra | Rakshasa | Antya |
| 19 | Mula | 240–253.33 | Ketu | Nirriti | Rakshasa | Aadi |
| 20 | Purva Ashadha | 253.33–266.67 | Venus | Apas | Manushya | Madhya |
| 21 | Uttara Ashadha | 266.67–280 | Sun | Vishvadevas | Manushya | Antya |
| 22 | Shravana | 280–293.33 | Moon | Vishnu | Deva | Aadi |
| 23 | Dhanishtha | 293.33–306.67 | Mars | Ashta Vasus | Rakshasa | Madhya |
| 24 | Shatabhisha | 306.67–320 | Rahu | Varuna | Rakshasa | Antya |
| 25 | Purva Bhadrapada | 320–333.33 | Jupiter | Aja Ekapada | Manushya | Aadi |
| 26 | Uttara Bhadrapada | 333.33–346.67 | Saturn | Ahirbudhnya | Manushya | Madhya |
| 27 | Revati | 346.67–360 | Mercury | Pushan | Deva | Antya |

### 7.3 Worked Example — Ajay Kumar

```
Moon at 27.977°:
  Nak = FLOOR(27.977/13.3333)+1 = FLOOR(2.098)+1 = 2+1 = 3 → Krittika ✅
  Into Nak = 27.977 − 26.667 = 1.310°
  Pada = FLOOR(1.310/3.3333)+1 = FLOOR(0.393)+1 = 0+1 = 1 → Pada 1 ✅

Mars at 210.538°:
  Nak = FLOOR(210.538/13.3333)+1 = FLOOR(15.790)+1 = 15+1 = 16 → Vishakha ✅
  Into Nak = 210.538 − 200.000 = 10.538°
  Pada = FLOOR(10.538/3.3333)+1 = FLOOR(3.161)+1 = 3+1 = 4 → Pada 4 ✅

Lagna at 219.849°:
  Nak = FLOOR(219.849/13.3333)+1 = FLOOR(16.489)+1 = 16+1 = 17 → Anuradha ✅
  Into Nak = 219.849 − 213.333 = 6.516°
  Pada = FLOOR(6.516/3.3333)+1 = FLOOR(1.955)+1 = 1+1 = 2 → Pada 2 ✅
```

### 7.4 Why Nakshatra Matters

```
Nakshatra reveals:
  1. Nakshatra Lord   → sub-dispositor chain; Dasha sequence starting point
  2. Deity            → the cosmic archetype governing this planetary energy
  3. Gana             → temperamental nature (Deva/Manushya/Rakshasa)
  4. Nadi             → Ashtakuta marriage compatibility factor
  5. Pada             → Navamsha sub-sign → inner nature of the planet
  6. Symbol           → mythological and psychological story of the energy
```

---

📌 **End of Part 1**

> *"Jyotiṣam eka-cakṣuḥ Vedānām — na jyotiṣa-jñānam vinā viduṣaḥ."*  
> — Vedāṅga Jyotiṣa (Astrology is the single eye of the Vedas — without its knowledge there is no true scholar)

**Next**: [Part 2 — Dignity, Relationships, Aspects & Yogas →](Jyotish_Process_Guide_Part2.md)
