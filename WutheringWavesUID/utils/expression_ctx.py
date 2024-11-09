import copy
from typing import Dict, List

from .ascension.char import WavesCharResult, get_char_detail
from .ascension.constant import sum_percentages, sum_numbers
from .ascension.weapon import WavesWeaponResult, get_weapon_detail
from ..utils.api.model import Props
from ..utils.ascension.sonata import WavesSonataResult, get_sonata_detail


def prepare_phantom(equipPhantomList):
    result = {}
    temp_result = {}
    for i, _phantom in enumerate(equipPhantomList):
        if _phantom and _phantom.phantomProp:
            props = []
            if _phantom.mainProps:
                props.extend(_phantom.mainProps)
            if _phantom.subProps:
                props.extend(_phantom.subProps)
            result = sum_phantom_value(result, props)
            sonata_result: WavesSonataResult = get_sonata_detail(_phantom.fetterDetail.name)
            if sonata_result.name not in temp_result:
                temp_result[sonata_result.name] = {"num": 1, "result": sonata_result}
            else:
                temp_result[sonata_result.name]['num'] += 1

    for key, value in temp_result.items():
        if value['num'] >= 2:
            name = value['result'].set['2']['effect']
            effect = value['result'].set['2']['param'][0]
            result['ph'] = value['result'].name
            if name not in result:
                result[name] = effect
                continue
            old = float(result[name].replace("%", ""))
            new = float(effect.replace("%", ""))
            result[name] = f"{old + new:.1f}%"

    return result


def sum_phantom_value(result: Dict[str, str], prop_list: List[Props]):
    name_per = ["攻击", "生命", "防御"]

    for prop in prop_list:
        per = "%" in prop.attributeValue
        name = prop.attributeName
        if per and name in name_per:
            name = f'{name}%'
        if name not in result:
            result[name] = prop.attributeValue
            continue

        if per:
            old = float(result[name].replace("%", ""))
            new = float(prop.attributeValue.replace("%", ""))
            result[name] = f"{old + new:.1f}%"
        else:
            old = int(result[name])
            new = int(prop.attributeValue)
            result[name] = f"{old + new:d}"

    return result


def enhance_summation_phantom_value(role_id, role_level, role_breach,
                                    weapon_id, weapon_level, weapon_breach, weapon_reson_level,
                                    result: Dict[str, str]):
    char_result: WavesCharResult = get_char_detail(role_id, role_level, role_breach)

    weapon_result: WavesWeaponResult = get_weapon_detail(weapon_id, weapon_level, weapon_breach, weapon_reson_level)

    # 基础生命
    _life = char_result.stats['life']
    # 基础攻击
    _atk = char_result.stats['atk']
    # 基础防御
    _def = char_result.stats['def']

    # 武器基础攻击
    _weapon_atk = weapon_result.stats[0]['value']

    base_atk = float(_atk) + float(_weapon_atk)
    per_atk = float(result.get("攻击%", "0%").replace("%", "")) * 0.01
    new_atk = int(base_atk * per_atk) + int(result.get("攻击", "0"))
    result["攻击"] = f"{new_atk}"

    base_life = float(_life)
    per_life = float(result.get("生命%", "0%").replace("%", "")) * 0.01
    new_life = int(base_life * per_life) + int(result.get("生命", "0"))
    result["生命"] = f"{new_life}"

    base_def = float(_def)
    per_def = float(result.get("防御%", "0%").replace("%", "")) * 0.01
    new_def = int(base_def * per_def) + int(result.get("防御", "0"))
    result["防御"] = f"{new_def}"

    return result


def enhance_summation_card_value(role_id, role_level, role_breach, role_attr,
                                 weapon_id, weapon_level, weapon_breach, weapon_reson_level,
                                 result, card_sort_map):
    shuxing = f"{role_attr}伤害加成"
    card_sort_map = copy.deepcopy(card_sort_map)
    char_result: WavesCharResult = get_char_detail(role_id, role_level, role_breach)
    weapon_result: WavesWeaponResult = get_weapon_detail(weapon_id, weapon_level, weapon_breach, weapon_reson_level)

    # 基础生命
    _life = char_result.stats['life']
    # 基础攻击
    _atk = char_result.stats['atk']
    # 基础防御
    _def = char_result.stats['def']
    # 武器基础攻击
    _weapon_atk = weapon_result.stats[0]['value']
    # 武器副词条
    weapon_sub_name = weapon_result.stats[1]['name']
    weapon_sub_value = weapon_result.stats[1]['value']
    card_sort_map[weapon_sub_name] = sum_percentages(
        weapon_sub_value,
        card_sort_map[weapon_sub_name])

    # 武器谐振
    if weapon_result.sub_effect:
        # sub_name = ["生命提升", "共鸣效率提升", "攻击提升", "全属性伤害加成提升"]
        sub_effect_name = weapon_result.sub_effect['name']
        card_sort_map[sub_effect_name] = sum_percentages(
            weapon_result.sub_effect['value'],
            card_sort_map[sub_effect_name])

    # 角色固有技能
    for name, value in char_result.fixed_skill.items():
        if name not in card_sort_map:
            card_sort_map[name] = '0%'
        card_sort_map[name] = sum_percentages(
            value,
            card_sort_map[name])

    base_atk = float(sum_numbers(_atk, _weapon_atk))
    # 各种攻击百分比 = 武器副词条+武器谐振+固有技能
    per_temp = float(card_sort_map['攻击'].rstrip("%")) * 0.01
    card_sort_map['攻击'] = sum_numbers(base_atk, result.get("攻击", 0), round(base_atk * per_temp))
    card_sort_map['攻击'] = f"{card_sort_map['攻击'].split('.')[0]}"

    base_life = float(_life)
    per_life = float(card_sort_map["生命"].rstrip("%")) * 0.01
    card_sort_map["生命"] = sum_numbers(_life, result.get("生命", 0), round(base_life * per_life))
    card_sort_map['生命'] = f"{card_sort_map['生命'].split('.')[0]}"

    base_def = float(_def)
    per_def = float(card_sort_map['防御'].rstrip("%")) * 0.01
    card_sort_map["防御"] = sum_numbers(_def, result.get("防御", 0), round(base_def * per_def))
    card_sort_map['防御'] = f"{card_sort_map['防御'].split('.')[0]}"

    # 固定暴击
    char_crit_rate = '5%'
    # 固定爆伤
    char_crit_dmg = '150%'

    card_sort_map['暴击'] = sum_percentages(char_crit_rate, result.get("暴击", "0%"), card_sort_map['暴击'])
    card_sort_map['暴击伤害'] = sum_percentages(char_crit_dmg, result.get("暴击伤害", "0%"), card_sort_map['暴击伤害'])

    char_regen = '100%'
    card_sort_map['共鸣效率'] = sum_percentages(char_regen, result.get("共鸣效率", "0%"), card_sort_map['共鸣效率'])

    card_sort_map[shuxing] = sum_percentages(
        result.get(shuxing, "0%"),
        card_sort_map.get(shuxing, "0%"),
        card_sort_map.get("属性伤害加成", "0%"))

    if "属性伤害加成" in card_sort_map:
        del card_sort_map["属性伤害加成"]

    card_sort_map['普攻伤害加成'] = sum_percentages(
        result.get("普攻伤害加成", "0%"),
        card_sort_map.get("普攻伤害加成", "0%"))
    card_sort_map['重击伤害加成'] = sum_percentages(
        result.get("重击伤害加成", "0%"),
        card_sort_map.get("重击伤害加成", "0%"))
    card_sort_map['共鸣技能伤害加成'] = sum_percentages(
        result.get("共鸣技能伤害加成", "0%"),
        card_sort_map.get("共鸣技能伤害加成", "0%"))
    card_sort_map['共鸣解放伤害加成'] = sum_percentages(
        result.get("共鸣解放伤害加成", "0%"),
        card_sort_map.get("共鸣解放伤害加成", "0%"))
    card_sort_map['治疗效果加成'] = sum_percentages(
        result.get("治疗效果加成", "0%"),
        card_sort_map.get("治疗效果加成", "0%"))

    # logger.debug(f"面板数据: {card_sort_map}")
    return card_sort_map
