from typing import Dict, Optional

from pydantic import BaseModel

from .calc import WuWaCalc
from .calculate import get_calc_map, calc_phantom_score, get_total_score_bg
from .char_info_utils import get_all_role_detail_info
from .damage.abstract import DamageRankRegister
from .damage.utils import comma_separated_number
from ..utils.api.model import RoleDetailData


class WavesCharRank(BaseModel):
    roleId: int  # 角色id
    roleName: str  # 角色名字
    starLevel: int  # 角色星级
    level: int  # 角色等级
    chain: int  # 命座
    chainName: str  # 命座
    score: float  # 角色评分
    score_bg: str  # 评分背景
    expected_damage: Optional[float]  # 期望伤害


async def get_waves_char_rank(uid, all_role_detail, need_expected_damage=False):
    if not all_role_detail:
        all_role_detail = await get_all_role_detail_info(uid)
    if isinstance(all_role_detail, Dict):
        temp = all_role_detail.values()
    else:
        temp = all_role_detail
    waves_char_rank = []
    for role_detail in temp:
        if not isinstance(role_detail, RoleDetailData):
            role_detail = RoleDetailData(**role_detail)

        phantom_score = 0
        calc: WuWaCalc = WuWaCalc(role_detail)
        # calc_temp = None
        expected_damage = None
        weaponData = role_detail.weaponData

        if role_detail.phantomData and role_detail.phantomData.equipPhantomList:
            equipPhantomList = role_detail.phantomData.equipPhantomList

            calc.phantom_pre = calc.prepare_phantom()
            calc.phantom_card = calc.enhance_summation_phantom_value(calc.phantom_pre)
            calc.calc_temp = get_calc_map(calc.phantom_card, role_detail.role.roleName)

            # phantom_sum_value = prepare_phantom(equipPhantomList)
            # phantom_sum_value = enhance_summation_phantom_value(
            #     role_detail.role.roleId,
            #     role_detail.role.level,
            #     role_detail.role.breach,
            #     weaponData.weapon.weaponId,
            #     weaponData.level,
            #     weaponData.breach,
            #     weaponData.resonLevel,
            #     phantom_sum_value,
            # )
            # calc_temp = get_calc_map(phantom_sum_value, role_detail.role.roleName)
            for i, _phantom in enumerate(equipPhantomList):
                if _phantom and _phantom.phantomProp:
                    props = _phantom.get_props()
                    _score, _bg = calc_phantom_score(
                        role_detail.role.roleName, props, _phantom.cost, calc.calc_temp
                    )
                    phantom_score += _score

            if need_expected_damage:
                rankDetail = DamageRankRegister.find_class(str(role_detail.role.roleId))
                if rankDetail:

                    calc.role_card = calc.enhance_summation_card_value(
                        calc.phantom_card
                    )
                    calc.damageAttribute = calc.card_sort_map_to_attribute(
                        calc.role_card
                    )
                    # temp_card_sort_map = copy.deepcopy(card_sort_map)
                    # card_map = enhance_summation_card_value(
                    #     role_detail.role.roleId,
                    #     role_detail.role.level,
                    #     role_detail.role.breach,
                    #     role_detail.role.attributeName,
                    #     weaponData.weapon.weaponId,
                    #     weaponData.level,
                    #     weaponData.breach,
                    #     weaponData.resonLevel,
                    #     phantom_sum_value,
                    #     temp_card_sort_map,
                    # )
                    # damageAttribute = card_sort_map_to_attribute(card_map)
                    _, expected_damage = rankDetail["func"](
                        calc.damageAttribute, role_detail
                    )
                    expected_damage = comma_separated_number(expected_damage)

        wcr = WavesCharRank(
            **{
                "roleId": role_detail.role.roleId,
                "roleName": role_detail.role.roleName,
                "starLevel": role_detail.role.starLevel,
                "level": role_detail.level,
                "chain": role_detail.get_chain_num(),
                "chainName": role_detail.get_chain_name(),
                "score": phantom_score,
                "score_bg": get_total_score_bg(
                    role_detail.role.roleName, phantom_score, calc.calc_temp
                ),
                "expected_damage": expected_damage,
            }
        )
        waves_char_rank.append(wcr)

    return waves_char_rank


#
# def prepare_phantom(equipPhantomList):
#     result = {'ph_detail': [], 'echo_id': 0}
#     temp_result = {}
#     for i, _phantom in enumerate(equipPhantomList):
#         if _phantom and _phantom.phantomProp:
#             if i == 0:
#                 result['echo_id'] = _phantom.phantomProp.phantomId
#             props = _phantom.get_props()
#             result = sum_phantom_value(result, props)
#             sonata_result: WavesSonataResult = get_sonata_detail(_phantom.fetterDetail.name)
#             if sonata_result.name not in temp_result:
#                 temp_result[sonata_result.name] = {"phantomIds": [_phantom.phantomProp.phantomId],
#                                                    "result": sonata_result}
#             else:
#                 temp_result[sonata_result.name]['phantomIds'].append(_phantom.phantomProp.phantomId)
#
#     for key, value in temp_result.items():
#         num = len(value['phantomIds'])
#         result['ph_detail'].append({
#             'ph_num': num,
#             'ph_name': key,
#         })
#         if num >= 2:
#             name = value['result'].set['2']['effect']
#             effect = value['result'].set['2']['param'][0]
#             result['ph'] = value['result'].name
#             if name not in result:
#                 result[name] = effect
#                 continue
#             old = float(result[name].replace("%", ""))
#             new = float(effect.replace("%", ""))
#             result[name] = f"{old + new:.1f}%"
#
#     return result
#
#
# def sum_phantom_value(result: Dict[str, str], prop_list: List[Props]):
#     name_per = ["攻击", "生命", "防御"]
#
#     for prop in prop_list:
#         per = "%" in prop.attributeValue
#         name = prop.attributeName
#         if per and name in name_per:
#             name = f'{name}%'
#         if name not in result:
#             result[name] = prop.attributeValue
#             continue
#
#         if per:
#             old = float(result[name].replace("%", ""))
#             new = float(prop.attributeValue.replace("%", ""))
#             result[name] = f"{old + new:.1f}%"
#         else:
#             old = int(result[name])
#             new = int(prop.attributeValue)
#             result[name] = f"{old + new:d}"
#
#     return result
#
#
# def enhance_summation_phantom_value(role_id, role_level, role_breach,
#                                     weapon_id, weapon_level, weapon_breach, weapon_reson_level,
#                                     result: Dict[str, Union[str, float]]):
#     char_result: WavesCharResult = get_char_detail(role_id, role_level, role_breach)
#
#     weapon_result: WavesWeaponResult = get_weapon_detail(weapon_id, weapon_level, weapon_breach, weapon_reson_level)
#
#     # 基础生命
#     _life = char_result.stats['life']
#     # 基础攻击
#     _atk = char_result.stats['atk']
#     # 基础防御
#     _def = char_result.stats['def']
#
#     # 武器基础攻击
#     _weapon_atk = weapon_result.stats[0]['value']
#     result["atk_flat"] = float(result.get("攻击", "0"))
#     result["life_flat"] = float(result.get("生命", "0"))
#     result["def_flat"] = float(result.get("防御", "0"))
#
#     base_atk = float(_atk) + float(_weapon_atk)
#     per_atk = percent_to_float(result.get("攻击%", "0%"))
#     result['atk_percent'] = per_atk
#     new_atk = int(base_atk * per_atk) + int(result.get("攻击", "0"))
#     result["攻击"] = f"{new_atk}"
#
#     base_life = float(_life)
#     per_life = percent_to_float(result.get("生命%", "0%"))
#     result['life_percent'] = per_life
#     new_life = int(base_life * per_life) + int(result.get("生命", "0"))
#     result["生命"] = f"{new_life}"
#
#     base_def = float(_def)
#     per_def = percent_to_float(result.get("防御%", "0%"))
#     result['def_percent'] = per_def
#     new_def = int(base_def * per_def) + int(result.get("防御", "0"))
#     result["防御"] = f"{new_def}"
#
#     # 声骸首位
#     if 'echo_id' in result:
#         echo_clz = WavesEchoRegister.find_class(result['echo_id'])
#         if echo_clz:
#             e = echo_clz()
#             temp = e.do_equipment_first()
#             logger.debug(f"首位声骸数据 {e.name}-{e.id}-{temp}")
#             for key, value in temp.items():
#                 if key not in result:
#                     result[key] = value
#                 else:
#                     old = float(result[key].replace("%", ""))
#                     new = float(value.replace("%", ""))
#                     result[key] = f"{old + new:.1f}%"
#
#     return result
#
#
# def enhance_summation_card_value(role_id, role_level, role_breach, role_attr,
#                                  weapon_id, weapon_level, weapon_breach, weapon_reson_level,
#                                  result, card_sort_map):
#     shuxing = f"{role_attr}伤害加成"
#     card_sort_map = copy.deepcopy(card_sort_map)
#     char_result: WavesCharResult = get_char_detail(role_id, role_level, role_breach)
#     weapon_result: WavesWeaponResult = get_weapon_detail(weapon_id, weapon_level, weapon_breach, weapon_reson_level)
#
#     # 基础生命
#     _life = char_result.stats['life']
#     # 基础攻击
#     _atk = char_result.stats['atk']
#     # 基础防御
#     _def = char_result.stats['def']
#     # 武器基础攻击
#     _weapon_atk = weapon_result.stats[0]['value']
#     card_sort_map['char_atk'] = float(_atk)
#     card_sort_map['weapon_atk'] = float(_weapon_atk)
#     card_sort_map['char_life'] = float(_life)
#     card_sort_map['char_def'] = float(_def)
#     # 武器副词条
#     weapon_sub_name = weapon_result.stats[1]['name']
#     weapon_sub_value = weapon_result.stats[1]['value']
#     card_sort_map[weapon_sub_name] = sum_percentages(
#         weapon_sub_value,
#         card_sort_map[weapon_sub_name])
#
#     # 武器谐振
#     if weapon_result.sub_effect:
#         # sub_name = ["生命提升", "共鸣效率提升", "攻击提升", "全属性伤害加成提升"]
#         sub_effect_name = weapon_result.sub_effect['name']
#         card_sort_map[sub_effect_name] = sum_percentages(
#             weapon_result.sub_effect['value'],
#             card_sort_map[sub_effect_name])
#
#     # 角色固有技能
#     for name, value in char_result.fixed_skill.items():
#         if name not in card_sort_map:
#             card_sort_map[name] = '0%'
#         card_sort_map[name] = sum_percentages(
#             value,
#             card_sort_map[name])
#
#     base_atk = float(sum_numbers(_atk, _weapon_atk))
#     # 各种攻击百分比 = 武器副词条+武器谐振+固有技能
#     per_temp = percent_to_float(card_sort_map['攻击'])
#     card_sort_map['atk_percent'] = per_temp + result.get('atk_percent', 0)
#     card_sort_map['atk_flat'] = float(result.get("atk_flat", 0))
#     card_sort_map['攻击'] = sum_numbers(base_atk, result.get("攻击", 0), round(base_atk * per_temp))
#     card_sort_map['攻击'] = f"{card_sort_map['攻击'].split('.')[0]}"
#
#     base_life = float(_life)
#     per_life = percent_to_float(card_sort_map['生命'])
#     card_sort_map['life_percent'] = per_life + result.get('life_percent', 0)
#     card_sort_map['life_flat'] = float(result.get("life_flat", 0))
#     card_sort_map["生命"] = sum_numbers(_life, result.get("生命", 0), round(base_life * per_life))
#     card_sort_map['生命'] = f"{card_sort_map['生命'].split('.')[0]}"
#
#     base_def = float(_def)
#     per_def = percent_to_float(card_sort_map['防御'])
#     card_sort_map['def_percent'] = per_def + result.get('def_percent', 0)
#     card_sort_map['def_flat'] = float(result.get("def_flat", 0))
#     card_sort_map["防御"] = sum_numbers(_def, result.get("防御", 0), round(base_def * per_def))
#     card_sort_map['防御'] = f"{card_sort_map['防御'].split('.')[0]}"
#
#     # 固定暴击
#     char_crit_rate = '5%'
#     # 固定爆伤
#     char_crit_dmg = '150%'
#
#     card_sort_map['暴击'] = sum_percentages(char_crit_rate, result.get("暴击", "0%"), card_sort_map['暴击'])
#     card_sort_map['crit_rate'] = percent_to_float(card_sort_map['暴击'])
#     card_sort_map['暴击伤害'] = sum_percentages(char_crit_dmg, result.get("暴击伤害", "0%"), card_sort_map['暴击伤害'])
#     card_sort_map['crit_dmg'] = percent_to_float(card_sort_map['暴击伤害'])
#
#     char_regen = '100%'
#     card_sort_map['共鸣效率'] = sum_percentages(char_regen, result.get("共鸣效率", "0%"), card_sort_map['共鸣效率'])
#     card_sort_map['energy_regen'] = percent_to_float(card_sort_map['共鸣效率'])
#
#     card_sort_map[shuxing] = sum_percentages(
#         result.get(shuxing, "0%"),
#         card_sort_map.get(shuxing, "0%"),
#         card_sort_map.get("属性伤害加成", "0%"))
#     card_sort_map['shuxing_bonus'] = percent_to_float(card_sort_map[shuxing])
#     card_sort_map['char_attr'] = role_attr
#
#     if "属性伤害加成" in card_sort_map:
#         del card_sort_map["属性伤害加成"]
#
#     card_sort_map['普攻伤害加成'] = sum_percentages(
#         result.get("普攻伤害加成", "0%"),
#         card_sort_map.get("普攻伤害加成", "0%"))
#     card_sort_map['attack_damage'] = percent_to_float(card_sort_map['普攻伤害加成'])
#
#     card_sort_map['重击伤害加成'] = sum_percentages(
#         result.get("重击伤害加成", "0%"),
#         card_sort_map.get("重击伤害加成", "0%"))
#     card_sort_map['hit_damage'] = percent_to_float(card_sort_map['重击伤害加成'])
#
#     card_sort_map['共鸣技能伤害加成'] = sum_percentages(
#         result.get("共鸣技能伤害加成", "0%"),
#         card_sort_map.get("共鸣技能伤害加成", "0%"))
#     card_sort_map['skill_damage'] = percent_to_float(card_sort_map['共鸣技能伤害加成'])
#
#     card_sort_map['共鸣解放伤害加成'] = sum_percentages(
#         result.get("共鸣解放伤害加成", "0%"),
#         card_sort_map.get("共鸣解放伤害加成", "0%"))
#     card_sort_map['liberation_damage'] = percent_to_float(card_sort_map['共鸣解放伤害加成'])
#
#     card_sort_map['治疗效果加成'] = sum_percentages(
#         result.get("治疗效果加成", "0%"),
#         card_sort_map.get("治疗效果加成", "0%"))
#     card_sort_map['heal_bonus'] = percent_to_float(card_sort_map['治疗效果加成'])
#
#     card_sort_map['ph_detail'] = result.get('ph_detail')
#     card_sort_map['echo_id'] = result.get('echo_id')
#     # logger.debug(f"面板数据: {card_sort_map}")
#     return card_sort_map
#
#
# def card_sort_map_to_attribute(card_sort_map: Dict):
#     attr = DamageAttribute()
#     attr.set_char_atk(card_sort_map['char_atk'])
#     attr.set_char_life(card_sort_map['char_life'])
#     attr.set_char_def(card_sort_map['char_def'])
#     attr.set_weapon_atk(card_sort_map['weapon_atk'])
#     attr.set_atk_flat(card_sort_map['atk_flat'])
#     attr.set_life_flat(card_sort_map['life_flat'])
#     attr.set_def_flat(card_sort_map['def_flat'])
#     attr.add_atk_percent(card_sort_map['atk_percent'])
#     attr.add_life_percent(card_sort_map['life_percent'])
#     attr.add_def_percent(card_sort_map['def_percent'])
#     attr.add_crit_rate(card_sort_map['crit_rate'])
#     attr.add_crit_dmg(card_sort_map['crit_dmg'])
#     attr.add_energy_regen(card_sort_map['energy_regen'])
#     # attr.add_dmg_bonus(card_sort_map['dmg_bonus'])
#     attr.set_dmg_bonus_phantom(card_sort_map)
#     attr.set_echo_id(card_sort_map['echo_id'])
#     attr.set_char_attr(card_sort_map['char_attr'])
#     if card_sort_map.get('ph_detail'):
#         for ph_detail in card_sort_map['ph_detail']:
#             attr.add_ph_detail(ph_detail)
#     return attr
