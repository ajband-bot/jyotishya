# జ్యోతిష — Vedic Astrology System — PROJECT CONTEXT

> **For Code Puppy:** Start every session by reading this file.
> It has everything you need to continue work without re-explanation.

---

## 📍 Project Location
```
/Users/a0b1803/Documents/jyotisha/
```

## 🚀 How to Start
```bash
cd /Users/a0b1803/Documents/jyotisha
./start.sh          # starts server + opens browser
# OR manually:
.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 7575 --reload
```
App runs at: **http://localhost:7575**  
Logs: `tail -f /tmp/jyotisha.log`

---

## 🏗️ Tech Stack
| Layer | Technology |
|-------|------------|
| Backend | Python + FastAPI |
| Frontend | Jinja2 templates + Tailwind CDN + Chart.js |
| Styling | Walmart brand colors (blue #0053e2, gold #ffc220) |
| Astro math | Pure Python, Jean Meeus algorithms (no external astro API) |
| State | None (stateless, all calcs on-the-fly) |
| Package mgr | uv (venv at `.venv/`) |

---

## 📁 File Structure
```
jyotisha/
├── app/
│   ├── main.py                  # FastAPI app entry point
│   ├── api/
│   │   └── routes.py            # All HTTP routes + SI grid builder + city lookup
│   ├── astro/
│   │   ├── constants.py         # SIGNS, NAKSHATRAS, PLANETS, SI_GRID layout, exaltations
│   │   ├── engine.py            # Julian day, sidereal longitudes, Lahiri ayanamsa, Lagna
│   │   └── dashas.py            # Vimshottari dasha/antardasha computation
│   └── knowledge/
│       ├── planets.py           # Per-planet karakatva, traits, house effects
│       ├── houses.py            # Bhava meanings, natures (kendra/trikona/dusthana etc)
│       └── interpreter.py       # full_analysis() — lagna, moon, yogas, career, character
└── templates/
    ├── base.html                # Nav, CSS vars, Tailwind, shared JS (tabs, accordion)
    ├── index.html               # Input form (birth date/time/place)
    └── chart.html               # 7-tab results: chart, planets, yogas, dashas, analysis, career, knowledge graph
```

---

## ✨ What Works (v2)
- [x] South Indian 4×4 fixed-sign chart rendered in HTML/CSS grid
- [x] **pyswisseph (Swiss Ephemeris) engine** — arc-second precision, replaces broken pure-Python math
- [x] **Lahiri ayanamsa via SIDM_LAHIRI** — verified against Jagannatha Hora / onlinejyotish.com
- [x] **All 9 planets + Lagna match PDF reference to the arcsecond** (validated Dec 31 1987 chart)
- [x] Retrograde flag on all planets (speed < 0)
- [x] Combustion detection built into engine
- [x] Rahu/Ketu always 180° apart (Ketu = Rahu + 180°)
- [x] Whole-sign houses (South Indian style)
- [x] Vimshottari Mahadasha + Antardasha with current period highlighted
- [x] Yoga detection: Gajakesari, Budha-Aditya, Pancha Mahapurusha, Neechabhanga, Chandra-Mangala
- [x] Character analysis from Lagna + Moon sign
- [x] Career analysis from 10th bhava
- [x] Nakshatra + pada from Moon
- [x] Interactive knowledge graph (canvas, click planeils)
- [x] 40+ Indian cities lat/lon lookup built-in
- [x] Telugu text throughout UI

## 🔑 Engine Key Facts (v2)
- `pyswisseph` is installed in `.venv/` — `import swisseph as swe`
- `swe.set_sid_mode(swe.SIDM_LAHIRI)` is called at module load in `engine.py`
- Julian Day: `swe.julday(year, month, day, ut_hour)` — always pass UT (subtract IST 5.5h)
- Planets: `swe.calc_ut(jd, planet_id, FLG_SWIEPH | FLG_SIDEREAL | FLG_SPEED)` → sidereal directly
- Lagna: `swe.houses_ex(jd, lat, lon, b'P', FLG_SIDEREAL)` → ascmc[0] is sidereal ascendant
- UT conversion in `julian_day()`: if `ut = hour - utc_offset < 0`, subtract 1 day + add 24

---

## ⚠️ Next Steps (v2 → v3)

### Still to implement:
- [ ] **Yoga detection** — more yogas from BPHS: Raja Yoga, Dhana Yoga, Viparita Raja Yoga, Saraswati Yoga
- [ ] **Ashtakavarga** — not implemented yet
- [ ] **Navamsa (D9) chart** — not implemented
- [ ] **Shadbala** — not implemented
- [ ] **Combustion flag in UI** — engine detects it, UI doesn't show it yet
- [ ] **Retrograde flag in South Indian chart grid** — show (R) next to planet abbrev

### UI Improvements Planned
- [ ] Print/PDF export of chart
- [ ] Share link (encode birth data in URL)
- [ ] Dark/light mode toggle
- [ ] Animated dasha timeline (Chart.js)

---

## 📚 Classical Text Sources Encoded
| Book | Chapter | What it drives |
|------|---------|----------------|
| BPHS (Brihat Parashara Hora Shastra) | Ch.7, 27, 36 | Yogas, Dashas, house lordship |
| Saravali (Kalyana Varma) | Ch.37 | Planet-in-house effects |
| Phaladeepika (Mantreswara) | Ch.7 | Neechabhanga rules |
| Brihat Jataka (Varahamihira) | Ch.3 | Character from Lagna |

---

## 🔑 Key Code Facts for Code Puppy
- `full_analysis(chart, birth_date)` in `interpreter.py` is the main orchestrator
- `chart` dict returned by `all_planets_sidereal()` has keys: `Lagna`, `Sun`, `Moon`, `Mars`,
  `Mercury`, `Jupiter`, `Venus`, `Saturn`, `Rahu`, `Ketu`, `_ayanamsa`
- Each planet entry: `{sign, house, longitude, deg_in_sign}`
- `SI_GRID` in `constants.py` maps `sign_number → (row, col)` for the 4×4 South Indian grid
- Starlette 1.0 API: `templates.TemplateResponse(request, "template.html", context_dict)` —
  request is the FIRST positional arg (NOT inside context dict — this changed in Starlette 1.0)
- Python venv: `.venv/` inside project folder, use `.venv/bin/python`

---

## 💬 How to Use This File With Code Puppy

At the start of a new Code Puppy session, just say:

> **"Read /Users/a0b1803/Documents/jyotisha/CONTEXT.md and then [describe what you want]"**

Code Puppy will read this file and have full context of the project instantly.
