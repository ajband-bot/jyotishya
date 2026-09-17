"""Vedic Astrology Constants — Signs, Planets, Nakshatras, Dashas.
Sources: Brihat Parashara Hora Shastra (BPHS), Saravali (Kalyana Varma)."""

# ── Rashis (Signs) ─────────────────────────────────────────────────────────
SIGNS = [
    {"id": 1, "name": "మేషం",    "en": "Aries",       "lord": "Mars",    "element": "Fire",  "quality": "Cardinal", "gender": "M", "symbol": "♈"},
    {"id": 2, "name": "వృషభం",   "en": "Taurus",      "lord": "Venus",   "element": "Earth", "quality": "Fixed",    "gender": "F", "symbol": "♉"},
    {"id": 3, "name": "మిథునం",  "en": "Gemini",      "lord": "Mercury", "element": "Air",   "quality": "Mutable",  "gender": "M", "symbol": "♊"},
    {"id": 4, "name": "కర్కాటకం","en": "Cancer",      "lord": "Moon",    "element": "Water", "quality": "Cardinal", "gender": "F", "symbol": "♋"},
    {"id": 5, "name": "సింహం",   "en": "Leo",         "lord": "Sun",     "element": "Fire",  "quality": "Fixed",    "gender": "M", "symbol": "♌"},
    {"id": 6, "name": "కన్య",    "en": "Virgo",       "lord": "Mercury", "element": "Earth", "quality": "Mutable",  "gender": "F", "symbol": "♍"},
    {"id": 7, "name": "తుల",     "en": "Libra",       "lord": "Venus",   "element": "Air",   "quality": "Cardinal", "gender": "M", "symbol": "♎"},
    {"id": 8, "name": "వృశ్చికం","en": "Scorpio",     "lord": "Mars",    "element": "Water", "quality": "Fixed",    "gender": "F", "symbol": "♏"},
    {"id": 9, "name": "ధనుస్సు", "en": "Sagittarius", "lord": "Jupiter", "element": "Fire",  "quality": "Mutable",  "gender": "M", "symbol": "♐"},
    {"id": 10,"name": "మకరం",    "en": "Capricorn",   "lord": "Saturn",  "element": "Earth", "quality": "Cardinal", "gender": "F", "symbol": "♑"},
    {"id": 11,"name": "కుంభం",   "en": "Aquarius",    "lord": "Saturn",  "element": "Air",   "quality": "Fixed",    "gender": "M", "symbol": "♒"},
    {"id": 12,"name": "మీనం",    "en": "Pisces",      "lord": "Jupiter", "element": "Water", "quality": "Mutable",  "gender": "F", "symbol": "♓"},
]

# ── Grahas (Planets) ──────────────────────────────────────────────────────
PLANETS = {
    "Sun":     {"tel": "సూర్యుడు",  "symbol": "☉", "nature": "Malefic",   "gender": "M", "color": "#FF8C00"},
    "Moon":    {"tel": "చంద్రుడు",  "symbol": "☽", "nature": "Benefic",   "gender": "F", "color": "#C0C0C0"},
    "Mars":    {"tel": "అంగారకుడు","symbol": "♂", "nature": "Malefic",   "gender": "M", "color": "#FF2400"},
    "Mercury": {"tel": "బుధుడు",   "symbol": "☿", "nature": "Neutral",   "gender": "N", "color": "#32CD32"},
    "Jupiter": {"tel": "గురుడు",   "symbol": "♃", "nature": "Benefic",   "gender": "M", "color": "#FFD700"},
    "Venus":   {"tel": "శుక్రుడు", "symbol": "♀", "nature": "Benefic",   "gender": "F", "color": "#FF69B4"},
    "Saturn":  {"tel": "శనిuడు",   "symbol": "♄", "nature": "Malefic",   "gender": "N", "color": "#708090"},
    "Rahu":    {"tel": "రాహువు",   "symbol": "☊", "nature": "Malefic",   "gender": "N", "color": "#4B0082"},
    "Ketu":    {"tel": "కేతువు",   "symbol": "☋", "nature": "Malefic",   "gender": "N", "color": "#8B0000"},
}

# ── Nakshatras (27 Lunar Mansions) ────────────────────────────────────────
NAKSHATRAS = [
    {"id":1,  "name":"అశ్విని",    "en":"Ashwini",     "lord":"Ketu",    "deity":"Ashwins",      "degrees":(0,   13.33)},
    {"id":2,  "name":"భరణి",      "en":"Bharani",     "lord":"Venus",   "deity":"Yama",         "degrees":(13.33,26.67)},
    {"id":3,  "name":"కృత్తిక",   "en":"Krittika",    "lord":"Sun",     "deity":"Agni",         "degrees":(26.67,40)},
    {"id":4,  "name":"రోహిణి",    "en":"Rohini",      "lord":"Moon",    "deity":"Brahma",       "degrees":(40,  53.33)},
    {"id":5,  "name":"మృగశిర",    "en":"Mrigashira",  "lord":"Mars",    "deity":"Soma",         "degrees":(53.33,66.67)},
    {"id":6,  "name":"ఆర్ద్ర",    "en":"Ardra",       "lord":"Rahu",    "deity":"Rudra",        "degrees":(66.67,80)},
    {"id":7,  "name":"పునర్వసు",  "en":"Punarvasu",   "lord":"Jupiter", "deity":"Aditi",        "degrees":(80,  93.33)},
    {"id":8,  "name":"పుష్యమి",   "en":"Pushyami",    "lord":"Saturn",  "deity":"Brihaspati",   "degrees":(93.33,106.67)},
    {"id":9,  "name":"ఆశ్లేష",    "en":"Aslesha",     "lord":"Mercury", "deity":"Sarpa",        "degrees":(106.67,120)},
    {"id":10, "name":"మఘ",        "en":"Magha",       "lord":"Ketu",    "deity":"Pitris",       "degrees":(120, 133.33)},
    {"id":11, "name":"పూర్వఫల్గుణి","en":"Purva Phalguni","lord":"Venus","deity":"Bhaga",      "degrees":(133.33,146.67)},
    {"id":12, "name":"ఉత్తరఫల్గుణి","en":"Uttara Phalguni","lord":"Sun","deity":"Aryama",    "degrees":(146.67,160)},
    {"id":13, "name":"హస్త",      "en":"Hasta",       "lord":"Moon",    "deity":"Savitar",      "degrees":(160, 173.33)},
    {"id":14, "name":"చిత్త",     "en":"Chitra",      "lord":"Mars",    "deity":"Tvashta",      "degrees":(173.33,186.67)},
    {"id":15, "name":"స్వాతి",    "en":"Swati",       "lord":"Rahu",    "deity":"Vayu",         "degrees":(186.67,200)},
    {"id":16, "name":"విశాఖ",     "en":"Vishakha",    "lord":"Jupiter", "deity":"Indragni",     "degrees":(200, 213.33)},
    {"id":17, "name":"అనురాధ",    "en":"Anuradha",    "lord":"Saturn",  "deity":"Mitra",        "degrees":(213.33,226.67)},
    {"id":18, "name":"జ్యేష్ఠ",   "en":"Jyeshtha",    "lord":"Mercury", "deity":"Indra",        "degrees":(226.67,240)},
    {"id":19, "name":"మూల",       "en":"Moola",       "lord":"Ketu",    "deity":"Nirrti",       "degrees":(240, 253.33)},
    {"id":20, "name":"పూర్వాషాఢ","en":"Purvashadha",  "lord":"Venus",   "deity":"Apas",         "degrees":(253.33,266.67)},
    {"id":21, "name":"ఉత్తరాషాఢ","en":"Uttarashadha", "lord":"Sun",     "deity":"Vishvadevas",  "degrees":(266.67,280)},
    {"id":22, "name":"శ్రవణం",    "en":"Shravana",    "lord":"Moon",    "deity":"Vishnu",       "degrees":(280, 293.33)},
    {"id":23, "name":"ధనిష్ఠ",   "en":"Dhanishtha",  "lord":"Mars",    "deity":"Ashta Vasus",  "degrees":(293.33,306.67)},
    {"id":24, "name":"శతభిషం",   "en":"Shatabhisha", "lord":"Rahu",    "deity":"Varuna",       "degrees":(306.67,320)},
    {"id":25, "name":"పూర్వభాద్ర","en":"Purva Bhadra","lord":"Jupiter","deity":"Ajaikapada",   "degrees":(320, 333.33)},
    {"id":26, "name":"ఉత్తరభాద్ర","en":"Uttara Bhadra","lord":"Saturn", "deity":"Ahirbudhnya", "degrees":(333.33,346.67)},
    {"id":27, "name":"రేవతి",     "en":"Revati",      "lord":"Mercury", "deity":"Pusha",        "degrees":(346.67,360)},
]

# ── Vimshottari Dasha — years per planet (BPHS Ch.46) ─────────────────────
DASHA_YEARS = {
    "Ketu": 7, "Venus": 20, "Sun": 6, "Moon": 10, "Mars": 7,
    "Rahu": 18, "Jupiter": 16, "Saturn": 19, "Mercury": 17
}
DASHA_ORDER = ["Ketu","Venus","Sun","Moon","Mars","Rahu","Jupiter","Saturn","Mercury"]
TOTAL_DASHA_YEARS = 120

# ── Exaltation / Debilitation / Own Signs (BPHS Ch.3) ─────────────────────
PLANET_STATES = {
    "Sun":     {"exalt": 1,  "debil": 7,  "own": [5],       "exalt_deg": 10},
    "Moon":    {"exalt": 2,  "debil": 8,  "own": [4],       "exalt_deg": 3},
    "Mars":    {"exalt": 10, "debil": 4,  "own": [1, 8],    "exalt_deg": 28},
    "Mercury": {"exalt": 6,  "debil": 12, "own": [3, 6],    "exalt_deg": 15},
    "Jupiter": {"exalt": 4,  "debil": 10, "own": [9, 12],   "exalt_deg": 5},
    "Venus":   {"exalt": 12, "debil": 6,  "own": [2, 7],    "exalt_deg": 27},
    "Saturn":  {"exalt": 7,  "debil": 1,  "own": [10, 11],  "exalt_deg": 20},
    "Rahu":    {"exalt": 3,  "debil": 9,  "own": [],         "exalt_deg": 20},
    "Ketu":    {"exalt": 9,  "debil": 3,  "own": [],         "exalt_deg": 20},
}

# -- Naisargika (Natural) Graha Maitri (BPHS Ch.4) -------------------------
# Core 7-planet table cross-checked (AD-4, data-only, no code copied)
# against public-git-repos/PyJHora-main/src/jhora/const.py's
# `planet_relations` matrix -- exact agreement on every classical planet's
# friend/enemy/neutral sets. Rahu/Ketu are NOT part of BPHS Ch.4's original
# 7-graha table; the entries below follow the widely-used practical
# convention (Rahu co-friends with Saturn's circle, Ketu with Mars's/
# Sun's) rather than an explicit BPHS verse -- flagged `extended_convention`
# below, distinct from the 7-planet `core_bphs_ch4` tier, per Cardinal
# Rule 5 (cite sources honestly, never blend confidence tiers silently).
NATURAL_RELATIONSHIPS = {
    "Sun":     {"friends": ["Moon", "Mars", "Jupiter"], "enemies": ["Venus", "Saturn"], "neutrals": ["Mercury"]},
    "Moon":    {"friends": ["Sun", "Mercury"], "enemies": [], "neutrals": ["Mars", "Jupiter", "Venus", "Saturn"]},
    "Mars":    {"friends": ["Sun", "Moon", "Jupiter"], "enemies": ["Mercury"], "neutrals": ["Venus", "Saturn"]},
    "Mercury": {"friends": ["Sun", "Venus"], "enemies": ["Moon"], "neutrals": ["Mars", "Jupiter", "Saturn"]},
    "Jupiter": {"friends": ["Sun", "Moon", "Mars"], "enemies": ["Mercury", "Venus"], "neutrals": ["Saturn"]},
    "Venus":   {"friends": ["Mercury", "Saturn"], "enemies": ["Sun", "Moon"], "neutrals": ["Mars", "Jupiter"]},
    "Saturn":  {"friends": ["Mercury", "Venus"], "enemies": ["Sun", "Moon", "Mars"], "neutrals": ["Jupiter"]},
    "Rahu":    {"friends": ["Venus", "Saturn"], "enemies": ["Sun", "Moon", "Mars"], "neutrals": ["Mercury", "Jupiter", "Ketu"]},
    "Ketu":    {"friends": ["Sun", "Mars"], "enemies": ["Venus", "Saturn"], "neutrals": ["Moon", "Mercury", "Jupiter", "Rahu"]},
}
NATURAL_RELATIONSHIP_SOURCE_TIER = {
    "Sun": "core_bphs_ch4", "Moon": "core_bphs_ch4", "Mars": "core_bphs_ch4",
    "Mercury": "core_bphs_ch4", "Jupiter": "core_bphs_ch4", "Venus": "core_bphs_ch4",
    "Saturn": "core_bphs_ch4", "Rahu": "extended_convention", "Ketu": "extended_convention",
}
# Backward-compatible friends-only view (this used to be the sole content here).
NAT_FRIENDS = {planet: data["friends"] for planet, data in NATURAL_RELATIONSHIPS.items()}

# South Indian chart grid position for each sign (1-indexed)
# Grid is 4x4, positions 1-12 going clockwise from top-left
SI_GRID = {
    1: (0,1), 2: (0,2), 3: (0,3),  # Aries Taurus Gemini  — top row
    4: (1,3), 5: (2,3), 6: (3,3),  # Cancer Leo Virgo     — right col
    7: (3,2), 8: (3,1), 9: (3,0),  # Libra Scorpio Sagitt — bottom row
    10:(2,0), 11:(1,0), 12:(0,0),  # Capri Aquar Pisces   — left col
}
# Corner cells (row,col) are merged in real SI charts; we mark them blank
SI_BLANK = {(0,0): False, (0,3): False, (3,0): False, (3,3): False}