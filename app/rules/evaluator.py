from __future__ import annotations

from datetime import date
from typing import Any

from app.derived.factors import build_chart_context, sign_name
from app.fixtures import load_chart_fixture
from app.rules.loader import load_rule_pack


def _evaluation(rule_id: str, rule_name: str, evidence: str, outcome: str, quality: str) -> dict[str, str]:
    return {
        "rule_id": rule_id,
        "rule_name": rule_name,
        "evidence": evidence,
        "outcome": outcome,
        "quality": quality,
    }


def evaluate_core_rules(rule_pack: dict[str, Any], context: dict[str, Any]) -> list[dict[str, str]]:
    chart = context["chart"]
    d9 = context["d9"]
    current_dasha = context["current_dasha"]
    house_lords = context["house_lords"]
    marakas = context["maraka_lords"]
    karakas = context["karakas"]
    aspects = context["aspect_map"]
    combustion = context["combustion"]
    yoga_karakas = context["yoga_karakas"]
    lagna_pada = context["lagna_pada"]
    upapada = context["upapada"]
    shadbala = context["shadbala"]
    varga_quality = context["varga_quality"]
    ishta_kashta = context["ishta_kashta"]
    transits = context["transits"]
    argala = context["argala"]
    ashtakavarga = context["ashtakavarga"]

    rows: list[dict[str, str]] = []
    for rule in rule_pack.get("rule_cards", []):
        rid = rule["rule_id"]
        rname = rule["rule_name"]

        if rid == "RC-001":
            rows.append(_evaluation(rid, rname, f"Lagna={sign_name(chart['Lagna']['sign'])}; Lagna lord={house_lords[1]} in H{chart[house_lords[1]]['house']}; H7/H12 lord={house_lords[7]}.", "Functional role can be computed directly from lordship and placement.", "computed"))
        elif rid == "RC-002":
            rows.append(_evaluation(rid, rname, f"Mars={sign_name(chart['Mars']['sign'])} H{chart['Mars']['house']}; Jupiter={sign_name(chart['Jupiter']['sign'])} H{chart['Jupiter']['house']}; Venus={sign_name(chart['Venus']['sign'])} H{chart['Venus']['house']}.", "Rashi properties are available from computed placements.", "computed"))
        elif rid == "RC-003":
            rows.append(_evaluation(rid, rname, f"H10 lord={house_lords[10]} in H{chart[house_lords[10]]['house']}; H7 lord={house_lords[7]} in H{chart[house_lords[7]]['house']}; H5 lord={house_lords[5]} in H{chart[house_lords[5]]['house']}.", "Bhava-domain mapping is executable from computed lord placements.", "computed"))
        elif rid == "RC-004":
            rows.append(_evaluation(rid, rname, f"H10 lord {house_lords[10]} -> H{chart[house_lords[10]]['house']}; H7 lord {house_lords[7]} -> H{chart[house_lords[7]]['house']}; H5 lord {house_lords[5]} -> H{chart[house_lords[5]]['house']}.", "Lord-of-house results can be derived with exact house transfer logic.", "computed"))
        elif rid == "RC-005":
            rows.append(_evaluation(rid, rname, f"Mars aspects {aspects['Mars']}; Jupiter aspects {aspects['Jupiter']}; Saturn aspects {aspects['Saturn']}.", "Special-aspect coverage is now explicit and traceable.", "computed"))
        elif rid == "RC-006":
            rows.append(_evaluation(rid, rname, f"D1 Venus={sign_name(chart['Venus']['sign'])} H{chart['Venus']['house']}; D9 Venus={d9['planets']['Venus']['sign_en']} H{d9['planets']['Venus']['house']} state={d9['planets']['Venus']['state']}.", "D1/D9 comparison is computed; any marriage downgrade must use this actual D9 state.", "computed"))
        elif rid == "RC-007":
            rows.append(_evaluation(rid, rname, f"Mars varga score={varga_quality['Mars']['score']}; Jupiter varga score={varga_quality['Jupiter']['score']}; Venus varga score={varga_quality['Venus']['score']}.", "D1/D9 weighted varga quality is now available as a practical runtime substitute for full Vimsopaka until exact classical scoring is added.", "computed_simplified"))
        elif rid == "RC-008":
            rows.append(_evaluation(rid, rname, f"Mars Shadbala={shadbala['Mars']['total_score']} ({shadbala['Mars']['verdict']}); Jupiter={shadbala['Jupiter']['total_score']} ({shadbala['Jupiter']['verdict']}); Mercury={shadbala['Mercury']['total_score']} ({shadbala['Mercury']['verdict']}).", "Simplified practical Shadbala is now computed from dignity, house, dig, kala, chesta, naisargika, and drik components.", "computed_simplified"))
        elif rid == "RC-009":
            rows.append(_evaluation(rid, rname, f"Mars Ishta/Kashta={ishta_kashta['Mars']['ishta']}/{ishta_kashta['Mars']['kashta']}; Jupiter={ishta_kashta['Jupiter']['ishta']}/{ishta_kashta['Jupiter']['kashta']}; Venus={ishta_kashta['Venus']['ishta']}/{ishta_kashta['Venus']['kashta']}.", "A simplified practical Ishta/Kashta layer is now available to tune benefic/malefic tendency transparently.", "computed_simplified"))
        elif rid == "RC-013":
            rows.append(_evaluation(rid, rname, f"Lagna Argala={argala['lagna']['verdict']} net={argala['lagna']['net_score']}; H7 Argala={argala['marriage']['verdict']} net={argala['marriage']['net_score']}; H10 Argala={argala['career']['verdict']} net={argala['career']['net_score']}.", "A practical Argala layer now evaluates support from 2/4/11 and counter-Argala from 12/10/3 for key houses.", "computed_simplified"))
        elif rid == "RC-018":
            rows.append(_evaluation(rid, rname, "Required calculator is not implemented in the current codebase.", "Rule cannot be fully scored yet.", "data_gap"))
        elif rid == "RC-010":
            rows.append(_evaluation(rid, rname, f"Yoga-karaka planets={yoga_karakas if yoga_karakas else 'none'} for this Lagna.", "Strict yoga-karaka status is derived from actual Kendra+Trikona ownership.", "computed"))
        elif rid == "RC-011":
            rows.append(_evaluation(rid, rname, f"Atmakaraka={karakas['atmakaraka']}; Darakaraka={karakas['darakaraka']}; H7 lord={house_lords[7]} in H{chart[house_lords[7]]['house']}.", "Karaka hierarchy is available from computed D1 degrees and lordship.", "computed"))
        elif rid == "RC-012":
            rows.append(_evaluation(rid, rname, f"Atmakaraka={karakas['atmakaraka']}; AK in D9={d9['planets'][karakas['atmakaraka']]['sign_en']} H{d9['planets'][karakas['atmakaraka']]['house']}.", "Karakamsa layer can now be computed instead of guessed.", "computed"))
        elif rid == "RC-014":
            rows.append(_evaluation(rid, rname, f"Lagna Pada={lagna_pada['pada_sign_en']} (A1) via Lagna lord {lagna_pada['lord']} in H{lagna_pada['lord_house']}; distance={lagna_pada['distance']}; exception_used={lagna_pada['exception_used']}.", "Bhavapada/Lagna Pada is now computed and available for projection-style interpretation.", "computed"))
        elif rid == "RC-015":
            canonical = upapada["canonical"]
            legacy = upapada["project_guides"]
            rows.append(_evaluation(rid, rname, f"UL canonical={canonical['pada_sign_en']} (standard Arudha); UL guide_formula={legacy['pada_sign_en']} ({legacy['formula_mode']}); H12 lord {canonical['lord']} in H{canonical['lord_house']}; recommended={upapada['recommended_formula']}; formulas_match={upapada['matches']}.", "Upapada now preserves both the standard Arudha formula and the guide-compatible inclusive count so corpus disagreements remain explicit and auditable.", "computed_with_conflict" if not upapada['matches'] else "computed"))
        elif rid == "RC-016":
            moon_house = chart['Moon']['house']
            twelfth_from_moon = ((moon_house - 2) % 12) + 1
            second_from_moon = (moon_house % 12) + 1
            rows.append(_evaluation(rid, rname, f"Moon H{moon_house}; planets 12th from Moon(H{twelfth_from_moon})={[p for p in ['Sun','Moon','Mars','Mercury','Jupiter','Venus','Saturn','Rahu','Ketu'] if chart[p]['house'] == twelfth_from_moon]}; planets 2nd from Moon(H{second_from_moon})={[p for p in ['Sun','Moon','Mars','Mercury','Jupiter','Venus','Saturn','Rahu','Ketu'] if chart[p]['house'] == second_from_moon]}.", "Lunar yoga detection is partially computable; exclusion rules still need hard-coding.", "computed"))
        elif rid == "RC-017":
            is_ruchaka = chart['Mars']['house'] in [1, 4, 7, 10] and chart['Mars']['sign'] in [1, 8, 10]
            rows.append(_evaluation(rid, rname, f"Mars in H{chart['Mars']['house']} {sign_name(chart['Mars']['sign'])}; Ruchaka={is_ruchaka}.", "Core canonical yoga detection is computable at least for explicit yogas like Ruchaka.", "computed"))
        elif rid == "RC-019":
            rows.append(_evaluation(rid, rname, f"H2 planets={[p for p in ['Sun','Moon','Mars','Mercury','Jupiter','Venus','Saturn','Rahu','Ketu'] if chart[p]['house'] == 2]}; H2 lord={marakas['house_2_lord']} in H{chart[marakas['house_2_lord']]['house']}; Mercury combust={combustion['Mercury']['combust']}; Saturn combust={combustion['Saturn']['combust']}.", "Dhana vs penury must include both wealth-support and combustion penalties.", "computed"))
        elif rid == "RC-020":
            retro = {p: chart[p]['retrograde'] for p in ['Sun','Moon','Mars','Mercury','Jupiter','Venus','Saturn','Rahu','Ketu']}
            pratyantara = current_dasha.get('pratyantardasha', {})
            jupiter_bindus = ashtakavarga['current_transits']['Jupiter']
            saturn_bindus = ashtakavarga['current_transits']['Saturn']
            rows.append(_evaluation(rid, rname, f"Retrograde flags={retro}; current dasha={current_dasha.get('mahadasha', {}).get('planet')}/{current_dasha.get('antardasha', {}).get('planet')}/{pratyantara.get('planet')}; Jupiter transit from Moon={transits['references']['from_moon']['Jupiter']} with SAV/PAV={jupiter_bindus['sav_bindus']}/{jupiter_bindus['pav_bindus']} ({jupiter_bindus['verdict']}); Saturn transit from Moon={transits['references']['from_moon']['Saturn']} with SAV/PAV={saturn_bindus['sav_bindus']}/{saturn_bindus['pav_bindus']} ({saturn_bindus['verdict']}).", "Retrograde, Pratyantara Dasha, exact transit-state inputs, and a practical Ashtakavarga bindu proxy are now available for timing analysis.", "computed_simplified"))
        else:
            rows.append(_evaluation(rid, rname, "No evaluator implemented yet.", "Rule not wired to runtime yet.", "data_gap"))
    return rows


def evaluate_chart_fixture(chart_id: str, rule_pack_path: str | None = None, today: date | None = None) -> dict[str, Any]:
    fixture = load_chart_fixture(chart_id)
    rule_pack = load_rule_pack(rule_pack_path)
    context = build_chart_context(fixture, today=today)
    evaluations = evaluate_core_rules(rule_pack, context)
    return {
        "chart_id": chart_id,
        "fixture": fixture,
        "current_dasha": context["current_dasha"],
        "evaluations": evaluations,
    }
