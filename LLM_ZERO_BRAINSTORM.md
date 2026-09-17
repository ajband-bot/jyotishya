# 🧠 Jyotisha LLM-Zero Architecture — Brainstorm
> **Date**: 2026-04-06 | **Goal**: Eliminate LLM dependency for predictions, run fully offline.

---

## 📍 Current State Assessment

### What's ALREADY offline & solid ✅

| Layer | Status | Files |
|-------|--------|-------|
| Astronomical calc | ✅ Swiss Ephemeris | `engine.py` |
| Planet positions | ✅ Arc-second precision | `engine.py` |
| Dasha computation | ✅ Vimshottari | `dashas.py` |
| Basic karakatvas | ✅ 9 planets × 12 houses | `planets.py` |
| House meanings | ✅ 12 bhavas | `houses.py` |
| Basic yogas (6) | ✅ Gajakesari, Budha-Aditya, etc. | `interpreter.py` |
| Lagna descriptions | ✅ 12 signs | `interpreter.py` |

### What STILL needs LLM 🔴 (the gap)

| Prediction Domain | Why LLM is needed today |
|-------------------|------------------------|
| **Dasha-by-dasha narrative** | No rule engine for "Mars MD + Jupiter AD = X" |
| **10-Layer Synthesis** | Process Guide Part 4 has the protocol but it's only prose |
| **Marriage timing** | Marriage Guide Parts 1-4 have rules but not coded |
| **Dosha detection + cancellation** | Process Guide Part 3 has 11 cancellation rules, not coded |
| **Career specifics** | Only basic 10th-house check; no dasha-triggered career events |
| **Remedies** | Entire remedy system exists in docs but not encoded |
| **Character depth** | Only 2-line Lagna desc; docs have 7-layer character model |
| **Navamsa cross-ref** | D9 chart not computed, crucial for prediction depth |
| **Ashtakavarga** | Not implemented — needed for transit predictions |
| **Exception handling** | "Saturn in 10th BUT combust AND retrograde" — no logic |

### Source Material Inventory (~400KB across 20+ .md files)

| Document Set | Files | Key Knowledge |
|-------------|-------|---------------|
| Learning Guide (5 parts) | `Jyotish_Learning_Part1-5` | Structure → Calculations → Interpretation → Examples → Reference |
| Process Guide (4 parts) | `Jyotish_Process_Guide_Part1-4` | Chart construction → Dignity/Aspects/Yogas → Doshas/Dasha → 10-Layer Synthesis |
| Marriage Guide (4 parts) | `Marriage_Guide_Part1-4` | 5 Pillars → Ashtakuta → Timing → Synastry |
| Shad Darshana (3 parts) | `Shad_Darshana_Part1-3` | Philosophy → Logic Engine → Applied Logic |
| Madhuri Analysis (3 parts) | `Madhuri_Jyotish_Part1-3` | Worked example: positions → yogas → dasha narrative |

---

## 🏗️ Architecture Options

### Option 1: Structured Rule Engine (YAML rules + Python evaluator + Jinja templates) ⭐ RECOMMENDED

```
knowledge/
├── rules/
│   ├── planet_in_house.yaml      # 9 planets × 12 houses × modifiers
│   ├── planet_in_sign.yaml       # 9 × 12 sign placements
│   ├── yogas.yaml                # 50+ yogasitions + cancellations
│   ├── doshas.yaml               # Mangal, Kala Sarpa, etc. + cancellations
│   ├── dasha_effects.yaml        # 9 MD lords × 9 AD lords = 81 combos
│   ├── marriage.yaml             # Ashtakuta, timing rules, synastry
│   ├── career.yaml               # Planet→profession mapping + dasha triggers
│   ├── remedies.yaml             # Gemstones, mantras, donation per planet
│   └── character.yaml            # Multi-layer character synthesis rules
├── templates/
│   ├── dasha_narrative.jinja     # "During {md_lord} Mahadasha, {ad_lord} Antardasha..."
│   ├── yoga_description.jinja    # Yoga found → paragraph
│   ├── marriage_report.jinja     # Full marriage analysis
│   └── synthesis.jinja           # 10-layer life narrative
└── engine.py                     # Rule evaluator: chart_data + rules → predictions
```

#### Example YAML Rule — Yoga Definition

```yaml
# yogas.yaml
- name: "గజకేసరి యోగం"
  name_en: "Gajakesari Yoga"
  source: "BPHS Ch.36"
  conditions:
    - type: "kendra_from"
      planet: "Jupiter"
      reference: "Moon"
  cancellations:
    - type: "combust"
      planet: "Jupiter"
    - type: "debilitated"
      planet: "Jupiter"
  strength_modifiers:
    - condition: {planet: "Jupiter", state: "exalted"}
      boost: 2
    - condition: {planet: "Jupiter", state: "own-sign"}
      boost: 1
  effects:
    strong: "Fame, wisdom, noble character. Commands respect like a lion among elephants."
    moderate: "Intellectual respect, good reputation in community."
    weak: "Mild increase in wisdom, partial recognition."
  tel_effects:
    strong: "జ్ఞానం, కీర్తి, గజేంద్ర తేజస్సు — సమాజంలో గొప్ప గౌరవం"
  dasha_trigger: ["Jupiter", "Moon"]
  remedies:
    gemstone: "Yellow Sapphire"
    mantra: "Om Guru Devaya Namah"
```

#### Example YAML Rule — Dasha MD×AD Combo

```yaml
# dasha_effects.yaml
- mahadasha: "Mars"
  antardasha: "Jupiter"
  general: "Period of righteous action. Career leaps through courage guided by wisdom."
  if_yoga:
    ruchaka: "Peak manifestation of Ruchaka — authority, land, leadership achieved."
  house_context:
    mars_in_kendra: "Maximum career thrust. Promotions, recognition."
    mars_in_dusthana: "Battles won, but with scars. Health needs attention."
  tel: "కుజ మహాదశ, గురు అంతర్దశ — ధర్మబద్ధమైన చర్యల కాలం"
```

#### Example YAML Rule — Dosha with Cancellations

```yaml
# doshas.yaml
- name: "Mangal Dosha"
  name_tel: "మంగళ దోషం"
  source: "Jataka Parijata Ch.9, Muhurta Chintamani"
  trigger_houses: [1, 2, 4, 7, 8, 12]
  check_from: ["Lagna", "Moon", "Venus"]
  cancellations:
    - id: 1
      condition: {planet: "Mars", state: ["own-sign"]}
      source: "Phaladeepika Ch.7"
    - id: 2
      condition: {planet: "Mars", state: ["exalted"]}
      source: "Jyotish Ratnakar Ch.5"
    - id: 3
      condition: {lagna_sign: 1, mars_house: 1}
      source: "BPHS Ch.36"
    - id: 9
      condition: {planet: "Jupiter", aspects: "Mars"}
      source: "Jyotish Ratnakar Ch.5"
    - id: 10
      condition: "partner_also_manglik"
      source: "JR: Ubhayoh kuja-doṣa-yukte"
    - id: 11
      condition: {planet: "Mars", conjunct: ["Jupiter", "Full Moon"]}
      source: "Sarvartha Chintamani"
```

**Pros:**
- Deterministic, testable, version-controlled
- No LLM needed, works fully offline
- Easy to add/edit rules — just edit YAML + commit
- Can generate diffs when rules change
- Each rule has classical source attribution

**Cons:**
- Initial extraction effort is large (~200-300 rules from docs)
- Templates need careful writing to avoid sounding robotic

---

### Option 2: Knowledge Graph (NetworkX or SQLite-based)

```
Nodes: Planet, Sign, House, Nakshatra, Yoga, Dosha, Dasha, Remedy
Edges: "placed_in", "lords", "aspects", "cancels", "triggers", "remedied_by"

Query: "What happens when Mars(node) → placed_in → H1(node)
        AND Mars(node) → state → own-sign(node)
        AND Jupiter(node) → aspects → Mars(node)?"

Answer: Traverse edges → collect all effect nodes → template render
```

**Pros:**
- Beautiful for complex multi-factor queries
- Natural for "what aspects what" relationships
- Can power the UI knowledge graph tab already in the app

**Cons:**
- Overkill for initial version
- Harder to debug than flat YAML
- Graph traversal logic adds complexity

---

### Option 3: Vector DB (ChromaDB / SQLite-VSS) ❌ NOT RECOMMENDED

Store all .md chunks as embeddings, retrieve relevant rules at prediction time.

**Pros:** Handles fuzzy/exceptional cases well, easy to add new knowledge.

**Cons:** **STILL NEEDS AN LLM** to synthesize retrieved chunks into predictions. This defeats the "LLM-zero" goal. It just moves the dependency from "generate" to "summarize."

---

### Option 4: Single mega .md file as knowledge base ❌ NOT RECOMMENDED

Consolidate everything into one structured machine-readable markdown.

**Pros:** Simple, human-readable.

**Cons:** Parsing markdown is fragile, no query capability, scales poorly. It's documentation, not an engine.

---

## 🎯 Recommended Approach: Option 1 (Rule Engine) → Option 2 (Graph) later

---

## 📦 Phase 1: Rule Extraction & YAML Knowledge Base (2-3 weeks)

Extract from the 400KB of .md files into structured YAML:

| Rule Set | Count | Source Documents |
|----------|-------|-----------------|
| Planet-in-house effects | ~108 (9×12) | `planets.py` (80% done!), Learning Part 3 |
| Planet-in-sign effects | ~108 (9×12) | Learning Part 3, Saravali references |
| Yoga definitions | ~50+ | Process Guide Part 2, Learning Part 3 |
| Dasha MD×AD combos | ~81 (9×9) | Madhuri Part 3, Process Guide Part 3 |
| Dosha rules + cancellations | ~15 | Process Guide Part 3 |
| Career rules | ~30 | Learning Part 3, planets.py |
| Marriage rules | ~40 | Marriage Guide Parts 1-4 |
| Remedy prescriptions | ~20 | Process Guide Part 4 |
| Lagna character profiles (deep) | 12 | Learning Part 3, Process Guide Part 4 |
| Nakshatra personality profiles | 27 | Learning Part 1 |
| **TOTAL** | **~500 rules** | |

---

## 🔧 Phase 2: Rule Evaluator Engine (1-2 weeks)

```python
# Pseudocode for the rule engine
class RuleEngine:
    def __init__(self, rules_dir: str = "knowledge/rules"):
        self.yogas = load_yaml("yogas.yaml")
        self.doshas = load_yaml("doshas.yaml")
        self.dasha_effects = load_yaml("dasha_effects.yaml")
        # ... etc

    def evaluate_chart(self, chart_data, dasha_data):
        findings = []

        # Yoga detection
        for rule in self.yogas:
            if all(check_condition(chart_data, c) for c in rule["conditions"]):
                if not any(check_condition(chart_data, x) for x in rule["cancellations"]):
                    strength = compute_strength(chart_data, rule["strength_modifiers"])
                    findings.append(Finding(rule, strength, category="yoga"))

        # Dosha detection
        for rule in self.doshas:
            # ... similar pattern

        # Dasha narrative
        current_md, current_ad = get_current_dasha(dasha_data)
        combo = find_dasha_combo(self.dasha_effects, current_md, current_ad)
        findings.append(Finding(combo, category="dasha"))

        return findings
```

---

## 📝 Phase 3: Template-Based Narrative Generation (1 week)

```python
# Instead of LLM generating text, Jinja templates compose it
def generate_narrative(findings, chart_data, dasha_data):
    env = jinja2.Environment(loader=FileSystemLoader("knowledge/templates"))
    template = env.get_template("full_report.jinja")
    return template.render(
        findings=findings,
        chart=chart_data,
        dashas=dasha_data
    )
```

### Template example:

```jinja
{# dasha_narrative.jinja #}
## {{ md.planet }} మహాదశ ({{ md.start }} – {{ md.end }})

{{ md.planet }} as lord of H{{ md.houses|join(', H') }} occupies
H{{ md.current_house }} in {{ md.dignity }} state.

{% if md.planet in active_yogas %}
**Yoga Activation**: {{ active_yogas[md.planet].name }} manifests during this period.
{{ active_yogas[md.planet].effects[strength] }}
{% endif %}

{% for ad in md.antardashas %}
### {{ ad.planet }} అంతర్దశ ({{ ad.start }} – {{ ad.end }})
{{ dasha_combo_effect(md.planet, ad.planet) }}
{% endfor %}
```

---

## 🔄 Phase 4: Feedback Loop (1 week setup, ongoing)

```
┌─────────────────────────────────────────────────────────┐
│                   FEEDBACK LOOP                          │
│                                                          │
│  User submits chart → Engine generates prediction        │
│       ↓                                                  │
│  User flags: "This prediction was wrong/incomplete"      │
│       ↓                                                  │
│  Feedback stored in feedback.jsonl:                      │
│    {chart_hash, rule_id, user_note, timestamp,           │
│     status: "pending_review"}                            │
│       ↓                                                  │
│  Review queue (admin UI or CLI):                         │
│    - Show the rule that fired                            │
│    - Show the chart context                              │
│    - Options: [Adjust rule] [Add exception] [Dismiss]    │
│       ↓                                                  │
│  If accepted → rule YAML updated + git commit            │
│  If new exception → new condition added to rule          │
│  If dismissed → marked "reviewed, no change"             │
│       ↓                                                  │
│  Audit trail: every rule change tracked in git           │
│  Test suite: regression tests ensure old charts          │
│              still produce correct results               │
└─────────────────────────────────────────────────────────┘
```

### Feedback data model:

```jsonl
{"id":"fb-001","ts":"2026-04-06T12:00:00","chart_hash":"abc123","rule_id":"yoga-gajakesari","field":"effects.strong","user_note":"Prediction said fame but native is unknown — Jupiter was combust","status":"pending_review","reviewer":null,"resolution":null}
```

### Validation before incorporating:

1. Cross-check against at least 2 classical texts
2. Verify the exception doesn't break existing test charts
3. Require a "source" citation for any new rule/exception
4. Run regression: all previously validated charts must still pass

---

## 🔑 The Key Insight: Why LLM-Zero IS Achievable

Looking at Madhuri Part 3 (dasha narrative) and Process Guide Part 4 (10-layer synthesis), the LLM isn't doing anything *creative*. It's doing this:

```
INPUT:  Mars in H1 + own sign + Jupiter aspect + Ruchaka Yoga + Mars MD active
OUTPUT: "During Mars Mahadasha, the native experiences peak leadership energy.
         Ruchaka Yoga manifests — authority, land acquisition, and physical
         vitality are at their strongest..."
```

That's **template composition**, not intelligence.

The "art" is in:
1. **Knowing which rules apply** → the evaluator (deterministic)
2. **Composing them gracefully** → the templates (deterministic)

Both are deterministic. The learning materials literally contain the templates already:

- `"Venus (YOGA KARAKA, EXALTED in H2) — Activated from Infancy"` is just `{planet} ({yoga_status}, {dignity} in H{house}) — {activation_context}`
- The dasha narratives in Madhuri Part 3 follow a consistent fill-in-the-blanks pattern

---

## 📊 Effort Estimate & LLM Dependency Reduction

| Phase | Effort | LLM Dependency After |
|-------|--------|---------------------|
| Phase 1: YAML extraction | 2-3 weeks | ~60% eliminated |
| Phase 2: Rule engine | 1-2 weeks | ~85% eliminated |
| Phase 3: Templates | 1 week | ~95% eliminated |
| Phase 4: Feedback loop | 1 week setup | ~98% eliminated |
| Phase 5: Graph UI (optional) | Nice-to-have | 98% stays |

The remaining ~2% = truly novel edge cases no classical text covers. A real astrologer would also struggle with those. Solution: "flag for manual review" bucket.

---

## 🚀 Possible Starting Points

1. **Start with YAML rule schema** — extract rules from .md files into structured YAML
2. **Build rule evaluator prototype** — evaluate yogas/doshas against chart data
3. **Design feedback loop data model** — feedback.jsonl + review workflow
4. **Design Jinja template system** — narrative generation from rule findings

---

## 🗂️ Files to Reference During Extraction

| Knowledge Domain | Primary Source Files |
|-----------------|---------------------|
| Interpretation rules | `Jyotish_Learning_Part3_Interpretations.md` |
| 10-Layer Synthesis | `Jyotish_Process_Guide_Part4.md` (Step 18) |
| Dosha rules | `Jyotish_Process_Guide_Part3.md` (Step 14) |
| Yoga verification | `Jyotish_Process_Guide_Part2.md` |
| Dasha narratives | `Madhuri_Jyotish_Part3.md` (Section 11) |
| Marriage rules | `Marriage_Guide_Part1-4.md` |
| Career mapping | `Jyotish_Learning_Part3.md` + `planets.py` |
| Existing code base | `interpreter.py`, `planets.py`, `houses.py` |
