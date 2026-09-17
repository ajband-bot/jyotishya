"""Nakṣatra profile data -- Gaṇa/Tattva/Yoni/Nadi/Motivation for all 27
nakṣatras, transcribed from docs/nakshatra-framework.md §1's master
reference table (itself cited BPHS Ch.86 / Nakṣatra Cintāmaṇi Ch.1).

Deliberately does NOT duplicate name/lord/deity/degree-span -- those
already live in app.astro.constants.NAKSHATRAS (DRY); this module adds
only the columns NAKSHATRAS doesn't carry.

NADI column added during build_plan.md Phase 4a (Marriage Compatibility
engine, Nadi Kuta). Source-critical note: Marriage_Guide_Part2.md contains
TWO nadi tables that disagree with each other -- its quick "Nakshatra
Reference Table" (top of the file) mislabels roughly a third of the Adi
group as Antya/Madhya, while its own detailed "NADI SYSTEM" section (used
correctly in that same document's worked Ajay/Sravani example) is
internally consistent. The values below follow the detailed section, and
were independently cross-checked (AD-4, data-only, no code imported)
against PyJHora's horoscope/match/compatibility.py `naadi_porutham()`
bvk/gvk grouping array -- all 27 nakshatras agree exactly. See
docs/marriage-compatibility-notes.md for the full discrepancy writeup.
"""
from __future__ import annotations

# Keyed by nakshatra id (1-27), matching app.astro.constants.NAKSHATRAS order.
NAKSHATRA_PROFILES: dict[int, dict[str, str]] = {
    1:  {"gana": "Deva",    "tattva": "Earth", "yoni": "Horse (M)",    "motivation": "Dharma", "nadi": "Adi"},
    2:  {"gana": "Manusya", "tattva": "Earth", "yoni": "Elephant (M)", "motivation": "Artha",  "nadi": "Madhya"},
    3:  {"gana": "Rakshasa","tattva": "Earth", "yoni": "Goat (F)",     "motivation": "Kama",   "nadi": "Antya"},
    4:  {"gana": "Manusya", "tattva": "Water", "yoni": "Serpent (M)",  "motivation": "Moksha", "nadi": "Antya"},
    5:  {"gana": "Deva",    "tattva": "Earth", "yoni": "Serpent (F)",  "motivation": "Moksha", "nadi": "Madhya"},
    6:  {"gana": "Manusya", "tattva": "Water", "yoni": "Dog (F)",      "motivation": "Kama",   "nadi": "Adi"},
    7:  {"gana": "Deva",    "tattva": "Water", "yoni": "Cat (F)",      "motivation": "Artha",  "nadi": "Adi"},
    8:  {"gana": "Deva",    "tattva": "Water", "yoni": "Goat (M)",     "motivation": "Dharma", "nadi": "Madhya"},
    9:  {"gana": "Rakshasa","tattva": "Water", "yoni": "Cat (M)",      "motivation": "Dharma", "nadi": "Antya"},
    10: {"gana": "Rakshasa","tattva": "Fire",  "yoni": "Rat (M)",      "motivation": "Artha",  "nadi": "Antya"},
    11: {"gana": "Manusya", "tattva": "Fire",  "yoni": "Rat (F)",      "motivation": "Kama",   "nadi": "Madhya"},
    12: {"gana": "Manusya", "tattva": "Fire",  "yoni": "Cow (M)",      "motivation": "Moksha", "nadi": "Adi"},
    13: {"gana": "Deva",    "tattva": "Fire",  "yoni": "Buffalo (F)",  "motivation": "Moksha", "nadi": "Adi"},
    14: {"gana": "Rakshasa","tattva": "Fire",  "yoni": "Tiger (F)",    "motivation": "Kama",   "nadi": "Madhya"},
    15: {"gana": "Deva",    "tattva": "Air",   "yoni": "Buffalo (M)",  "motivation": "Artha",  "nadi": "Antya"},
    16: {"gana": "Rakshasa","tattva": "Air",   "yoni": "Tiger (M)",    "motivation": "Dharma", "nadi": "Antya"},
    17: {"gana": "Deva",    "tattva": "Air",   "yoni": "Deer (F)",     "motivation": "Dharma", "nadi": "Madhya"},
    18: {"gana": "Rakshasa","tattva": "Air",   "yoni": "Deer (M)",     "motivation": "Artha",  "nadi": "Adi"},
    19: {"gana": "Rakshasa","tattva": "Air",   "yoni": "Dog (M)",      "motivation": "Kama",   "nadi": "Adi"},
    20: {"gana": "Manusya", "tattva": "Air",   "yoni": "Monkey (M)",   "motivation": "Moksha", "nadi": "Madhya"},
    21: {"gana": "Manusya", "tattva": "Air",   "yoni": "Mongoose (M)", "motivation": "Moksha", "nadi": "Antya"},
    22: {"gana": "Deva",    "tattva": "Air",   "yoni": "Monkey (F)",   "motivation": "Artha",  "nadi": "Antya"},
    23: {"gana": "Rakshasa","tattva": "Ether", "yoni": "Lion (F)",     "motivation": "Dharma", "nadi": "Madhya"},
    24: {"gana": "Rakshasa","tattva": "Ether", "yoni": "Horse (F)",    "motivation": "Dharma", "nadi": "Adi"},
    25: {"gana": "Manusya", "tattva": "Ether", "yoni": "Lion (M)",     "motivation": "Artha",  "nadi": "Adi"},
    26: {"gana": "Manusya", "tattva": "Ether", "yoni": "Cow (F)",      "motivation": "Kama",   "nadi": "Madhya"},
    27: {"gana": "Deva",    "tattva": "Ether", "yoni": "Elephant (F)", "motivation": "Moksha", "nadi": "Antya"},
}

# Gana temperament glosses -- docs/nakshatra-framework.md §2's own wording,
# transcribed verbatim rather than re-paraphrased.
GANA_TEMPERAMENT = {
    "Deva": "sattvic, generous",
    "Manusya": "rajasic, practical",
    "Rakshasa": "tamasic, intense, transformative",
}

CITATION = "BPHS Ch.86 / Nakṣatra Cintāmaṇi Ch.1 (docs/nakshatra-framework.md §1 master reference table)"
