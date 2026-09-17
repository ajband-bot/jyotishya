"""Chart interpretation engine.
Synthesizes planet positions, houses, dashas → human-readable Telugu/English analysis.
Sources: Saravali, BPHS, Phaladeepika, Brihat Jataka.
"""
from __future__ import annotations
from typing import Dict, List, Any
from app.astro.constants import SIGNS, PLANETS, NAKSHATRAS, PLANET_STATES
from app.astro.engine import planet_state, get_nakshatra, navamsha_d9, darakaraka
from app.knowledge.planets import KARAKATVA, PLANET_IN_HOUSE
from app.knowledge.houses import HOUSES, house_nature, RAJ_YOGA_COMBOS, DUSTHANA

KENDRA = [1,4,7,10]
TRIKONA = [1,5,9]


def _sign(n: int) -> Dict:
    return SIGNS[n-1]

def _planet_info(name: str) -> Dict:
    return PLANETS.get(name, {})


# ── Lagna Analysis ────────────────────────────────────────────────────────
LAGNA_DESC = {
    1:  {"name":"మేష లగ్నం","char":"Energetic, independent, leadership, impulsive. Natural leader. Pioneer spirit.",
         "tel":"చురుకుగా, స్వతంత్రంగా, నాయకత్వ లక్షణాలు. మొండిగా అయినా ముందుకు సాగుతారు."},
    2:  {"name":"వృషభ లగ్నం","char":"Patient, sensual, stubborn, love of beauty and comfort. Practical and reliable.",
         "tel":"ఓపిగ్గా, ఆచరణాత్మకంగా, సౌందర్యప్రియులు. స్థిరంగా నిలబడతారు."},
    3:  {"name":"మిథున లగ్నం","char":"Witty, dual nature, communicative, adaptable. Loves knowledge and variety.",
         "tel":"తెలివైన, ద్వంద్వ స్వభావం, వాక్పటుత్వం, అనేక విషయాలలో ఆసక్తి."},
    4:  {"name":"కర్కాటక లగ్నం","char":"Intuitive, emotional, protective, home-loving. Strong maternal instinct.",
         "tel":"భావోద్వేగ, ఇంటిపై ప్రేమ, తల్లి వంటి రక్షణ భావన, అంతర్జ్ఞానం."},
    5:  {"name":"సింహ లగ్నం","char":"Regal, generous, dramatic, proud, leadership. Born to lead and inspire.",
         "tel":"రాజసంగా, ఉదారంగా, గర్వంగా, నాయకత్వం కోసం జన్మించారు."},
    6:  {"name":"కన్య లగ్నం","char":"Analytical, perfectionist, service-oriented, health-conscious. Sharp intellect.",
         "tel":"విశ్లేషణాత్మక, పరిపూర్ణత కోసం ప్రయత్నం, సేవా మనస్తత్వం, తీక్షణ బుద్ధి."},
    7:  {"name":"తుల లగ్నం","char":"Balanced, diplomatic, artistic, relationship-focused. Seeks harmony always.",
         "tel":"సమతుల్యత, దౌత్యం, కళలపై ప్రేమ, సంబంధాలను ప్రాధాన్యత ఇస్తారు."},
    8:  {"name":"వృశ్చిక లగ్నం","char":"Intense, secretive, transformative, magnetic, investigative. Deep & powerful.",
         "tel":"తీవ్రంగా, రహస్యంగా, పరివర్తన శక్తి, అయస్కాంత వ్యక్తిత్వం."},
    9:  {"name":"ధనుస్సు లగ్నం","char":"Philosophical, optimistic, freedom-loving, generous, truth-seeker.",
         "tel":"తత్వజ్ఞానం, ఆశావాదం, స్వాతంత్ర్య ప్రేమ, సత్యం కోసం అన్వేషణ."},
    10: {"name":"మకర లగ్నం","char":"Ambitious, disciplined, practical, patient. Achieves through hard work.",
         "tel":"మహా పరిశ్రమశీలి, క్రమశిక్షణ, ఆచరణాత్మకత, ఓపికతో లక్ష్యాన్ని చేరుకుంటారు."},
    11: {"name":"కుంభ లగ్నం","char":"Humanitarian, innovative, unconventional, intellectual, social.",
         "tel":"మానవతావాది, నూతన ఆలోచనలు, అసాంప్రదాయిక మార్గాలు, సామాజిక చింతన."},
    12: {"name":"మీన లగ్నం","char":"Spiritual, compassionate, intuitive, dreamy, artistic. Connects with the divine.",
         "tel":"ఆధ్యాత్మిక, కరుణాపూర్వక, అంతర్జ్ఞానం, దివ్యత్వంతో అనుసంధానం."},
}


def analyze_navamsha(d1_chart: Dict) -> Dict:
    """Compute D9 chart and produce human-readable soul-level analysis.

    Returns the raw D9 dict plus derived insights:
      vargottama_planets  – planets in same sign in D1 and D9 (maximum strength)
      dk_summary          – concise Darakaraka partner profile
      notable_d9_dignities– list of {planet, state, house, note} for non-neutral planets
    """
    d9 = navamsha_d9(d1_chart)
    d9_planets = d9["planets"]
    d9_lagna_sign = d9["lagna_sign"]

    # Vargottama: D1 sign == D9 sign for a planet
    vargottama: list[str] = []
    for name in ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn","Lagna"]:
        d1_sign = d1_chart.get(name, {}).get("sign")
        d9_sign = d9_planets.get(name, {}).get("sign")
        if d1_sign and d9_sign and d1_sign == d9_sign:
            vargottama.append(name)

    # Notable dignities: any non-neutral planets (exalted / own-sign / debilitated)
    notable: list[Dict] = []
    for name, pd in d9_planets.items():
        if name == "Lagna" or pd["state"] == "neutral":
            continue
        house = pd["house"]
        house_type = "Kendra" if house in [1,4,7,10] else \
                     "Trikona" if house in [1,5,9] else \
                     "Upachaya" if house in [3,6,10,11] else \
                     "Dusthana" if house in [6,8,12] else "Other"
        note_parts = [f"{pd['state']} in D9 {pd['sign_en']} (H{house} — {house_type})",]
        if name == d9["darakaraka"]:
            note_parts.append("Darakaraka (spouse indicator) — DK dignity in D9 is paramount")
        notable.append({
            "planet": name,
            "state":  pd["state"],
            "sign":   pd["sign_en"],
            "house":  house,
            "house_type": house_type,
            "note":   " | ".join(note_parts),
        })

    # DK partner summary
    dk_name  = d9["darakaraka"]
    dk_state = d9["dk_d9_state"]
    dk_sign  = d9["dk_d9_sign_en"]
    dk_house = d9["dk_d9_house"]
    dk_summary = (
        f"DK = {dk_name} • D9 sign: {dk_sign} (H{dk_house} from D9 {d9['lagna_sign_en']} Lagna)"
        f" • D9 dignity: {dk_state}."
        f" The spouse carries {dk_name}’s energy; their soul-level quality is {dk_state} in {dk_sign}."
    )

    return {
        "d9_lagna_sign":     d9_lagna_sign,
        "d9_lagna_sign_en":  d9["lagna_sign_en"],
        "d9_lagna_sign_tel": d9["lagna_sign_tel"],
        "planets":           d9_planets,
        "darakaraka":        dk_name,
        "dk_d9_sign":        dk_sign,
        "dk_d9_state":       dk_state,
        "dk_d9_house":       dk_house,
        "dk_summary":        dk_summary,
        "vargottama":        vargottama,
        "notable_dignities": notable,
    }


def analyze_lagna(chart: Dict) -> Dict:
    lagna_sign = chart["Lagna"]["sign"]
    lagna_deg  = chart["Lagna"]["deg_in_sign"]
    ld = LAGNA_DESC.get(lagna_sign, {})
    sign_data = _sign(lagna_sign)
    return {
        "sign": sign_data["name"],
        "sign_en": sign_data["en"],
        "lord": sign_data["lord"],
        "degree": round(lagna_deg, 2),
        "character": ld.get("char",""),
        "tel_desc": ld.get("tel",""),
        "lagna_name": ld.get("name",""),
        "element": sign_data["element"],
        "quality": sign_data["quality"],
    }


def analyze_moon(chart: Dict) -> Dict:
    m = chart.get("Moon", {})
    sign_data = _sign(m["sign"])
    from app.astro.engine import get_nakshatra
    nak_info = get_nakshatra(m["longitude"])
    nak = nak_info["nakshatra"]
    return {
        "sign": sign_data["name"], "sign_en": sign_data["en"],
        "house": m["house"], "nakshatra": nak["name"],
        "nakshatra_en": nak["en"], "nakshatra_lord": nak["lord"],
        "pada": nak_info["pada"],
        "rashi_name": sign_data["name"],
        "tel_desc": f"రాశి: {sign_data['name']} | నక్షత్రం: {nak['name']} {nak_info['pada']}వ పాదం | నక్షత్రాధిపతి: {nak['lord']}",
    }


def detect_yogas(chart: Dict) -> List[Dict]:
    yogas = []
    planets = {k:v for k,v in chart.items() if k not in ("Lagna","_ayanamsa")}

    # Gajakesari: Jupiter in kendra from Moon
    moon_house = chart.get("Moon",{}).get("house",0)
    jup_house  = chart.get("Jupiter",{}).get("house",0)
    if jup_house and moon_house:
        diff = ((jup_house - moon_house) % 12) + 1
        if diff in [1,4,7,10]:
            yogas.append({"name":"గజకేసరి యోగం","effect":"Fame, wisdom, noble character like lion-elephant","tel":"చంద్రుని నుండి కేంద్రంలో గురుడు — జ్ఞానం, కీర్తి, గజేంద్ర తేజస్సు","strength":"strong"})

    # Budha-Aditya: Mercury + Sun within 14° in same sign
    if chart.get("Sun",{}).get("sign") == chart.get("Mercury",{}).get("sign"):
        sun_deg = chart["Sun"]["deg_in_sign"]
        mer_deg = chart["Mercury"]["deg_in_sign"]
        if abs(sun_deg - mer_deg) < 14:
            yogas.append({"name":"బుధ ఆదిత్య యోగం","effect":"Sharp intellect, eloquent speech, fame through communication","tel":"సూర్య-బుధ సంయోగం — తీక్షణ బుద్ధి, వాక్పటుత్వం, కీర్తి","strength":"moderate"})

    # Chandra-Mangala: Moon + Mars same sign
    if chart.get("Moon",{}).get("sign") == chart.get("Mars",{}).get("sign"):
        yogas.append({"name":"చంద్ర మంగళ యోగం","effect":"Wealth through real estate/mother's side, strong emotions","tel":"చంద్ర-కుజ సంయోగం — సంపద, భూ లాభాలు, ధైర్యం","strength":"moderate"})

    # Pancha Mahapurusha Yogas
    mahap = {"Mars":"రుచక","Mercury":"భద్ర","Jupiter":"హంస","Venus":"మాలవ్య","Saturn":"శష"}
    for pl, yoga_name in mahap.items():
        p = chart.get(pl,{})
        from app.astro.constants import PLANET_STATES
        ps = PLANET_STATES.get(pl,{})
        in_own  = p.get("sign") in ps.get("own",[])
        in_exalt = p.get("sign") == ps.get("exalt")
        if (in_own or in_exalt) and p.get("house") in KENDRA:
            yogas.append({"name":f"{yoga_name} యోగం (పంచ మహాపురుష)","effect":f"{pl} is exalted/own in kendra — maharaja qualities of {pl}","tel":f"{pl} కేంద్రంలో స్వక్షేత్రం/ఉచ్చంలో — {yoga_name} మహాపురుష గుణాలు","strength":"very strong"})

    # Neechabhanga Raja Yoga
    from app.astro.constants import PLANET_STATES
    for pl, ps in PLANET_STATES.items():
        p = chart.get(pl,{})
        if p.get("sign") == ps.get("debil"):
            # check if dispositor of debilitation sign is in kendra
            debil_sign_lord = _sign(ps["debil"])["lord"]
            dispositor = chart.get(debil_sign_lord,{})
            if dispositor.get("house") in KENDRA:
                yogas.append({"name":f"నీచభంగ రాజయోగం ({pl})","effect":f"{pl} debilitation cancelled — becomes raj yoga","tel":f"{pl} నీచస్థితి రద్దు — రాజయోగంగా పరిణమిస్తుంది","strength":"strong"})

    # Veshi Yoga: planet in 2nd from Sun
    sun_house = chart.get("Sun",{}).get("house",0)
    if sun_house:
        second_from_sun = (sun_house % 12) + 1
        for pl, p in planets.items():
            if pl not in ("Sun","Rahu","Ketu","Moon") and p.get("house") == second_from_sun:
                yogas.append({"name":f"వేశీ యోగం ({pl})","effect":"Eloquent, prosperous, virtuous","tel":f"సూర్యుని నుండి 2వ స్థానంలో {pl} — సౌభాగ్యవంతుడు","strength":"moderate"})

    return yogas


def planet_analysis(chart: Dict) -> List[Dict]:
    results = []
    for planet_name in ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn","Rahu","Ketu"]:
        p = chart.get(planet_name,{})
        if not p:
            continue
        sign_no = p["sign"]
        house   = p["house"]
        deg     = p["deg_in_sign"]
        s = _sign(sign_no)
        from app.astro.engine import planet_state
        state = planet_state(planet_name, sign_no)
        kv = KARAKATVA.get(planet_name,{})
        house_effect = PLANET_IN_HOUSE.get(planet_name,{}).get(house,"")
        results.append({
            "planet": planet_name,
            "tel": PLANETS.get(planet_name,{}).get("tel",""),
            "sign": s["name"], "sign_en": s["en"],
            "house": house, "degree": round(deg,2),
            "state": state,
            "house_name": HOUSES.get(house,{}).get("name",""),
            "house_en":   HOUSES.get(house,{}).get("en",""),
            "house_nature": house_nature(house),
            "karakatva": kv.get("tel_desc",""),
            "house_effect": house_effect,
            "character_trait": kv.get("character",""),
        })
    return results


def career_analysis(chart: Dict, planet_list: List[Dict]) -> Dict:
    """Determine career based on 10th house, 10th lord, planets in 10th."""
    lagna_sign = chart["Lagna"]["sign"]
    tenth_sign_no = ((lagna_sign - 1 + 9) % 12) + 1
    tenth_lord_name = _sign(tenth_sign_no)["lord"]
    tenth_lord = chart.get(tenth_lord_name,{})

    planets_in_10 = [p for p in planet_list if p["house"] == 10]

    professions = []
    for p in planets_in_10:
        profs = KARAKATVA.get(p["planet"],{}).get("professions",[])
        professions.extend(profs)

    # 10th lord's karakatva
    kv = KARAKATVA.get(tenth_lord_name,{})
    professions.extend(kv.get("professions",[]))

    # Sun/Saturn in 10th: government/hard work
    sun_house  = chart.get("Sun",{}).get("house")
    sat_house  = chart.get("Saturn",{}).get("house")
    jup_house  = chart.get("Jupiter",{}).get("house")

    career_hints = []
    if sun_house == 10:   career_hints.append("Government/Authority role (Sun in 10th)")
    if sat_house == 10:   career_hints.append("Engineering/Technical/Long-term career (Saturn in 10th)")
    if jup_house == 10:   career_hints.append("Teaching/Law/Religion/Medicine (Jupiter in 10th)")

    return {
        "10th_sign": _sign(tenth_sign_no)["name"],
        "10th_lord": tenth_lord_name,
        "10th_lord_house": tenth_lord.get("house","?"),
        "10th_lord_state": planet_state(tenth_lord_name, tenth_lord.get("sign",1)),
        "planets_in_10th": [p["planet"] for p in planets_in_10],
        "suggested_professions": list(dict.fromkeys(professions))[:8],
        "career_hints": career_hints,
        "tel_desc": f"10వ భావాధిపతి {tenth_lord_name} — {kv.get('tel_desc','')}",
    }


def character_analysis(chart: Dict, lagna_info: Dict, moon_info: Dict) -> Dict:
    traits = []
    # Lagna traits
    traits.append(lagna_info.get("character",""))
    # Moon sign traits (mind)
    moon_sign = chart.get("Moon",{}).get("sign",1)
    ld = LAGNA_DESC.get(moon_sign,{})
    traits.append("Mental nature: " + ld.get("char",""))
    # Jupiter — wisdom
    jup = chart.get("Jupiter",{})
    if jup.get("house") in TRIKONA:
        traits.append("Jupiter in trikona — philosophical wisdom, natural teacher/guide")
    # Mercury — intellect
    mer = chart.get("Mercury",{})
    if mer.get("house") in [1,4,5,9,10]:
        traits.append("Mercury in prominent house — sharp analytical mind, good communicator")
    return {
        "traits": [t for t in traits if t],
        "lagna_element": lagna_info.get("element",""),
        "lagna_quality": lagna_info.get("quality",""),
        "moon_nakshatra": moon_info.get("nakshatra",""),
        "moon_sign": moon_info.get("sign",""),
    }


def full_analysis(chart: Dict, birth_date_str: str) -> Dict:
    from datetime import date
    lagna_info  = analyze_lagna(chart)
    moon_info   = analyze_moon(chart)
    yogas       = detect_yogas(chart)
    planets     = planet_analysis(chart)
    career      = career_analysis(chart, planets)
    character   = character_analysis(chart, lagna_info, moon_info)
    navamsha    = analyze_navamsha(chart)      # D9 — now computed correctly every time
    return {
        "lagna":     lagna_info,
        "moon":      moon_info,
        "yogas":     yogas,
        "planets":   planets,
        "career":    career,
        "character": character,
        "navamsha":  navamsha,                 # always present, always correct
        "ayanamsa":  chart.get("_ayanamsa"),
    }
