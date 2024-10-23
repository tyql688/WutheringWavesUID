from typing import Dict, List

from .char_detail import WavesCharResult, get_char_detail
from .weapon_detail import WavesWeaponResult
from ..utils.api.model import Props
from ..utils.sonata_detail import WavesSonataResult, get_sonata_detail


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
                                    weapon_result: WavesWeaponResult,
                                    result: Dict[str, str]):
    char_result: WavesCharResult = get_char_detail(role_id, role_level, role_breach)

    # weapon_result: WavesWeaponResult = get_weapon_detail(weapon_id, weapon_level, weapon_breach, weapon_reson_level)

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
