"""House (Bhava) significations — BPHS Ch.11, Saravali Ch.4, Phaladeepika Ch.7."""

HOUSES = {
    1:  {"name":"లగ్న భావం",    "en":"Lagna/Self",            "tel_desc":"శరీరం, వ్యక్తిత్వం, ఆరోగ్యం, కీర్తి",          "body_part":"head/brain",         "karakas":["Sun","Mars"]},
    2:  {"name":"ధన భావం",      "en":"Wealth/Family",         "tel_desc":"ధనం, కుటుంబం, వాక్శక్తి, ముఖం",              "body_part":"face/throat/teeth",   "karakas":["Jupiter","Mercury"]},
    3:  {"name":"సహోదర భావం",   "en":"Courage/Siblings",      "tel_desc":"సోదరులు, సాహసం, లఘు ప్రయాణం, వ్రాత",         "body_part":"arms/shoulders",      "karakas":["Mars","Mercury"]},
    4:  {"name":"సుఖ భావం",     "en":"Home/Mother",           "tel_desc":"మాత, గృహం, భూమి, వాహనం, ఆనందం",             "body_part":"chest/heart",         "karakas":["Moon","Venus"]},
    5:  {"name":"పుత్ర భావం",   "en":"Children/Intelligence", "tel_desc":"సంతానం, బుద్ధి, ప్రేమ, మంత్ర, విద్య",        "body_part":"stomach",             "karakas":["Jupiter"]},
    6:  {"name":"రోగ భావం",     "en":"Disease/Enemies",       "tel_desc":"శత్రువులు, రోగం, ఋణం, సేవ",                  "body_part":"intestines/waist",    "karakas":["Mars","Saturn"]},
    7:  {"name":"కళత్ర భావం",   "en":"Marriage/Partnership",  "tel_desc":"భార్య/భర్త, వ్యాపార భాగస్వామి, విదేశీ",      "body_part":"kidneys/bladder",     "karakas":["Venus","Jupiter"]},
    8:  {"name":"ఆయుర్ భావం",   "en":"Longevity/Occult",      "tel_desc":"ఆయుస్సు, రహస్యాలు, ఆకస్మిక ఘటనలు",          "body_part":"reproductive system", "karakas":["Saturn"]},
    9:  {"name":"ధర్మ భావం",    "en":"Fortune/Dharma",        "tel_desc":"పితృ, భాగ్యం, ధర్మం, గురువు, దీర్ఘ ప్రయాణం", "body_part":"thighs/hips",        "karakas":["Jupiter","Sun"]},
    10: {"name":"కర్మ భావం",    "en":"Career/Status",         "tel_desc":"వృత్తి, కీర్తి, ప్రభుత్వం, అధికారం, కర్మ",   "body_part":"knees/back",          "karakas":["Sun","Mercury","Jupiter","Saturn"]},
    11: {"name":"లాభ భావం",     "en":"Gains/Income",          "tel_desc":"లాభం, ఆదాయం, మిత్రులు, జ్యేష్ఠ సోదరులు",     "body_part":"calves/ankles",       "karakas":["Jupiter"]},
    12: {"name":"వ్యయ భావం",    "en":"Loss/Moksha",           "tel_desc":"వ్యయం, విదేశాలు, మోక్షం, ఏకాంతం",            "body_part":"feet/left eye",       "karakas":["Saturn","Ketu"]},
}

TRIKONA  = [1, 5, 9]
KENDRA   = [1, 4, 7, 10]
DUSTHANA = [6, 8, 12]
UPACHAYA = [3, 6, 10, 11]


def house_nature(house: int) -> str:
    if house in TRIKONA:  return "trikona (శుభ)"
    if house in KENDRA:   return "kendra (బలమైన)"
    if house in DUSTHANA: return "dusthana (కష్టమైన)"
    if house in UPACHAYA: return "upachaya (వర్ధమాన)"
    return "neutral"


RAJ_YOGA_COMBOS = [
    {"name":"గజకేసరి యోగం",       "condition":"Jupiter in kendra from Moon",
     "effect":"Noble character, fame — జ్ఞానం, కీర్తి, గౌరవం"},
    {"name":"లక్ష్మీ యోగం",        "condition":"9th lord in kendra in own/exalt sign",
     "effect":"Immense wealth — మహా సంపద, భాగ్యం"},
    {"name":"బుధ ఆదిత్య యోగం",    "condition":"Mercury conjunct Sun",
     "effect":"Intelligence & eloquence — మేధా, వాక్పటుత్వం"},
    {"name":"చంద్ర మంగళ యోగం",    "condition":"Moon conjunct Mars",
     "effect":"Wealth through real estate — సంపద, భూ లాభాలు"},
    {"name":"నీచభంగ రాజయోగం",    "condition":"Debilitated planet with dispositor in kendra",
     "effect":"Debility cancelled — raj yoga — పతనం నుండి ఉద్ధారం"},
    {"name":"పంచ మహాపురుష యోగం", "condition":"Mars/Mercury/Jupiter/Venus/Saturn in own/exalt in kendra",
     "effect":"Maharaja-level qualities — మహారాజ గుణాలు"},
    {"name":"ఉభయచారి యోగం",      "condition":"Planets in both 2nd and 12th from Sun",
     "effect":"Prosperous on all sides — రాజుగా సంపన్నత"},
    {"name":"వేశీ యోగం",          "condition":"Planet(s) in 2nd from Sun",
     "effect":"Eloquent and prosperous — సౌభాగ్యవంతుడు"},
]
