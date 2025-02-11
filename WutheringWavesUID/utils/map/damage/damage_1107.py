# 珂莱塔
import copy

from .buff import shouanren_buff, zhezhi_buff
from .damage import echo_damage, weapon_damage, phase_damage
from ...api.model import RoleDetailData
from ...ascension.char import WavesCharResult, get_char_detail2
from ...damage.damage import DamageAttribute, calc_percent_expression
from ...damage.utils import (
    skill_damage_calc,
    SkillType,
    SkillTreeMap,
    cast_skill,
    cast_attack,
    cast_hit,
    skill_damage,
    cast_liberation,
    add_comma_separated_numbers,
)


def calc_damage(
    attr: DamageAttribute, role: RoleDetailData, isGroup: bool = False
) -> (str, str):
    title = "默认手法"
    if isGroup:
        msg = "变奏入场 ee aa aaa z qr aaaaa"
    else:
        msg = "ee aa aaa z qr aaaaa"

    attr.add_effect(title, msg)
    init_len = len(attr.effect)
    attr1 = copy.deepcopy(attr)
    crit_damage1, expected_damage1 = calc_damage_r(attr1, role, isGroup)
    attr1.add_effect("r伤害", f"期望伤害:{crit_damage1}; 暴击伤害:{expected_damage1}")

    attr2 = copy.deepcopy(attr)
    crit_damage2, expected_damage2 = calc_damage_3(
        attr2, role, isGroup, trigger_times=4
    )
    attr2.add_effect(
        "死兆*4伤害", f"期望伤害:{crit_damage2}; 暴击伤害:{expected_damage2}"
    )

    attr3 = copy.deepcopy(attr)
    crit_damage3, expected_damage3 = calc_damage_2(attr3, role, isGroup)
    attr3.add_effect(
        "r尾刀伤害", f"期望伤害:{crit_damage3}; 暴击伤害:{expected_damage3}"
    )

    crit_damage = add_comma_separated_numbers(crit_damage1, crit_damage2, crit_damage3)
    expected_damage = add_comma_separated_numbers(
        expected_damage1, expected_damage2, expected_damage3
    )

    attr.add_effect(" ", " ")
    attr.effect.extend(attr1.effect[init_len + 1 :])
    attr.add_effect(" ", " ")
    attr.effect.extend(attr2.effect[init_len + 1 :])
    attr.add_effect(" ", " ")
    attr.effect.extend(attr3.effect[init_len + 1 :])

    return crit_damage, expected_damage


def calc_damage_1(
    attr: DamageAttribute, role: RoleDetailData, isGroup: bool = False
) -> (str, str):
    # 设置角色伤害类型
    attr.set_char_damage(skill_damage)
    # 设置角色模板  "temp_atk", "temp_life", "temp_def"
    attr.set_char_template("temp_atk")

    title = "默认手法"
    if isGroup:
        msg = "变奏入场 ee aa aaa qz"
    else:
        msg = "ee aa aaa qz"
    attr.add_effect(title, msg)

    role_name = role.role.roleName
    # 获取角色详情
    char_result: WavesCharResult = get_char_detail2(role)

    skill_type: SkillType = "共鸣回路"
    # 获取角色技能等级
    skillLevel = role.get_skill_level(skill_type)
    # 技能技能倍率
    skill_multi = skill_damage_calc(
        char_result.skillTrees, SkillTreeMap[skill_type], "1", skillLevel
    )
    title = f"末路见行"
    msg = f"技能倍率{skill_multi}"
    attr.add_skill_multi(skill_multi, title, msg)

    # 设置角色施放技能
    damage_func = [cast_attack, cast_skill, cast_hit]
    phase_damage(attr, role, damage_func, isGroup)

    # 设置角色等级
    attr.set_character_level(role.role.level)

    # 设置角色固有技能
    role_breach = role.role.breach
    if role_breach and role_breach >= 3:
        title = f"{role_name}-固有技能-艺术至上"
        msg = f"为命中的目标附加解离效果"
        attr.add_effect(title, msg)

    # 设置角色技能施放是不是也有加成 eg：守岸人
    title = f"{role_name}-解离状态"
    msg = f"造成伤害时忽视目标18%防御"
    attr.add_defense_reduction(0.18, title, msg)

    # 设置声骸属性
    attr.set_phantom_dmg_bonus()

    # 设置共鸣链
    chain_num = role.get_chain_num()
    if chain_num >= 1:
        title = f"{role_name}-一链"
        msg = f"对拥有解离效果的目标攻击造成伤害时，该次伤害的暴击提升12.5%"
        attr.add_crit_rate(0.125, title, msg)

    if chain_num >= 4:
        title = f"{role_name}-四链"
        msg = f"珂莱塔施放重击末路见行时，队伍中的角色共鸣技能伤害加成提升25%"
        attr.add_dmg_bonus(0.25, title, msg)

    if chain_num >= 5:
        title = f"{role_name}-五链"
        msg = f"重击末路见行的伤害倍率提升47%"
        attr.add_skill_ratio(0.47, title, msg)

    # 声骸
    echo_damage(attr, isGroup)

    # 武器
    weapon_damage(attr, role.weaponData, damage_func, isGroup)

    # 暴击伤害
    crit_damage = f"{attr.calculate_crit_damage():,.0f}"
    # 期望伤害
    expected_damage = f"{attr.calculate_expected_damage():,.0f}"
    return crit_damage, expected_damage


def calc_damage_2(
    attr: DamageAttribute, role: RoleDetailData, isGroup: bool = False
) -> (str, str):
    # 设置角色伤害类型
    attr.set_char_damage(skill_damage)
    # 设置角色模板  "temp_atk", "temp_life", "temp_def"
    attr.set_char_template("temp_atk")

    title = "默认手法"
    if isGroup:
        msg = "变奏入场 ee aa aaa z qr aaaaa"
    else:
        msg = "ee aa aaa z qr aaaaa"
    attr.add_effect(title, msg)

    role_name = role.role.roleName
    # 获取角色详情
    char_result: WavesCharResult = get_char_detail2(role)

    skill_type: SkillType = "共鸣解放"
    # 获取角色技能等级
    skillLevel = role.get_skill_level(skill_type)
    # 技能技能倍率
    skill_multi = skill_damage_calc(
        char_result.skillTrees, SkillTreeMap[skill_type], "4", skillLevel
    )
    title = f"致死以终"
    msg = f"技能倍率{skill_multi}"
    attr.add_skill_multi(skill_multi, title, msg)

    # 设置角色施放技能
    damage_func = [cast_attack, cast_skill, cast_hit, cast_liberation]
    phase_damage(attr, role, damage_func, isGroup)

    # 设置角色等级
    attr.set_character_level(role.role.level)

    # 设置角色固有技能
    role_breach = role.role.breach
    if role_breach and role_breach >= 3:
        title = f"{role_name}-固有技能-艺术至上"
        msg = f"为命中的目标附加解离效果"
        attr.add_effect(title, msg)

    # 设置角色技能施放是不是也有加成 eg：守岸人

    title = f"{role_name}-解离状态"
    msg = f"造成伤害时忽视目标18%防御"
    attr.add_defense_reduction(0.18, title, msg)

    title = f"{role_name}-揭幕者状态"
    msg = f"共鸣解放致死以终的伤害倍率提升80%"
    attr.add_skill_ratio_in_skill_description(0.8, title, msg)

    # 设置声骸属性
    attr.set_phantom_dmg_bonus()

    # 设置共鸣链
    chain_num = role.get_chain_num()
    if chain_num >= 1:
        title = f"{role_name}-一链"
        msg = f"对拥有解离效果的目标攻击造成伤害时，该次伤害的暴击提升12.5%"
        attr.add_crit_rate(0.125, title, msg)

    if chain_num >= 2:
        title = f"{role_name}-二链"
        msg = f"共鸣解放致死以终的伤害倍率提升126%"
        attr.add_skill_ratio(1.26, title, msg)

    if chain_num >= 4:
        title = f"{role_name}-四链"
        msg = f"珂莱塔施放重击末路见行时，队伍中的角色共鸣技能伤害加成提升25%"
        attr.add_dmg_bonus(0.25, title, msg)

    # 声骸
    echo_damage(attr, isGroup)

    # 武器
    weapon_damage(attr, role.weaponData, damage_func, isGroup)

    # 暴击伤害
    crit_damage = f"{attr.calculate_crit_damage():,.0f}"
    # 期望伤害
    expected_damage = f"{attr.calculate_expected_damage():,.0f}"
    return crit_damage, expected_damage


def calc_damage_3(
    attr: DamageAttribute, role: RoleDetailData, isGroup: bool = False, trigger_times=1
) -> (str, str):
    # 设置角色伤害类型
    attr.set_char_damage(skill_damage)
    # 设置角色模板  "temp_atk", "temp_life", "temp_def"
    attr.set_char_template("temp_atk")

    title = "默认手法"
    if isGroup:
        msg = "变奏入场 ee aa aaa z qr aaaaa"
    else:
        msg = "ee aa aaa z qr aaaaa"
    attr.add_effect(title, msg)

    role_name = role.role.roleName
    # 获取角色详情
    char_result: WavesCharResult = get_char_detail2(role)

    skill_type: SkillType = "共鸣解放"
    # 获取角色技能等级
    skillLevel = role.get_skill_level(skill_type)
    # 技能技能倍率
    skill_multi = skill_damage_calc(
        char_result.skillTrees, SkillTreeMap[skill_type], "2", skillLevel
    )
    title = f"死兆"
    msg = f"技能倍率{skill_multi}"
    attr.add_skill_multi(skill_multi, title, msg)

    # 设置角色施放技能
    damage_func = [cast_attack, cast_skill, cast_hit, cast_liberation]
    phase_damage(attr, role, damage_func, isGroup)

    # 设置角色等级
    attr.set_character_level(role.role.level)

    # 设置角色固有技能
    role_breach = role.role.breach
    if role_breach and role_breach >= 3:
        title = f"{role_name}-固有技能-艺术至上"
        msg = f"为命中的目标附加解离效果"
        attr.add_effect(title, msg)

    # 设置角色技能施放是不是也有加成 eg：守岸人

    title = f"{role_name}-解离状态"
    msg = f"造成伤害时忽视目标18%防御"
    attr.add_defense_reduction(0.18, title, msg)

    title = f"{role_name}-揭幕者状态"
    msg = f"共鸣解放死兆的伤害倍率提升80%"
    attr.add_skill_ratio_in_skill_description(0.8, title, msg)

    # 设置声骸属性
    attr.set_phantom_dmg_bonus()

    # 设置共鸣链
    chain_num = role.get_chain_num()
    if chain_num >= 1:
        title = f"{role_name}-一链"
        msg = f"对拥有解离效果的目标攻击造成伤害时，该次伤害的暴击提升12.5%"
        attr.add_crit_rate(0.125, title, msg)

    if chain_num >= 4:
        title = f"{role_name}-四链"
        msg = f"珂莱塔施放重击末路见行时，队伍中的角色共鸣技能伤害加成提升25%"
        attr.add_dmg_bonus(0.25, title, msg)

    if chain_num >= 6:
        title = f"{role_name}-六链"
        msg = f"共鸣解放死兆伤害倍率提升186.6%"
        attr.add_skill_ratio(1.866, title, msg)

    # 声骸
    echo_damage(attr, isGroup)

    # 武器
    weapon_damage(attr, role.weaponData, damage_func, isGroup)

    # 暴击伤害
    crit_damage = f"{attr.calculate_crit_damage() * trigger_times:,.0f}"
    # 期望伤害
    expected_damage = f"{attr.calculate_expected_damage() * trigger_times:,.0f}"
    return crit_damage, expected_damage


def calc_damage_33(
    attr: DamageAttribute, role: RoleDetailData, isGroup: bool = False, trigger_times=1
) -> (str, str):
    # 设置角色伤害类型
    attr.set_char_damage(skill_damage)
    # 设置角色模板  "temp_atk", "temp_life", "temp_def"
    attr.set_char_template("temp_atk")

    title = "默认手法"
    if isGroup:
        msg = "变奏入场 ee aa aaa z qr aaaaa"
    else:
        msg = "ee aa aaa z qr aaaaa"
    attr.add_effect(title, msg)

    role_name = role.role.roleName
    # 获取角色详情
    char_result: WavesCharResult = get_char_detail2(role)

    # 设置共鸣链
    chain_num = role.get_chain_num()

    # 设置角色施放技能
    damage_func = [cast_attack, cast_skill, cast_hit, cast_liberation]
    phase_damage(attr, role, damage_func, isGroup)

    # 设置角色等级
    attr.set_character_level(role.role.level)

    # 设置角色固有技能
    role_breach = role.role.breach
    if role_breach and role_breach >= 3:
        title = f"{role_name}-固有技能-艺术至上"
        msg = f"为命中的目标附加解离效果"
        attr.add_effect(title, msg)

    # 设置角色技能施放是不是也有加成 eg：守岸人

    title = f"{role_name}-解离状态"
    msg = f"造成伤害时忽视目标18%防御"
    attr.add_defense_reduction(0.18, title, msg)

    title = f"{role_name}-揭幕者状态"
    msg = f"共鸣解放死兆的伤害倍率提升80%"
    attr.add_skill_ratio_in_skill_description(0.8, title, msg)

    # 设置声骸属性
    attr.set_phantom_dmg_bonus()

    if chain_num >= 1:
        title = f"{role_name}-一链"
        msg = f"对拥有解离效果的目标攻击造成伤害时，该次伤害的暴击提升12.5%"
        attr.add_crit_rate(0.125, title, msg)

    if chain_num >= 4:
        title = f"{role_name}-四链"
        msg = f"珂莱塔施放重击末路见行时，队伍中的角色共鸣技能伤害加成提升25%"
        attr.add_dmg_bonus(0.25, title, msg)
    # 声骸
    echo_damage(attr, isGroup)

    # 武器
    weapon_damage(attr, role.weaponData, damage_func, isGroup)

    skill_type: SkillType = "共鸣解放"
    # 获取角色技能等级
    skillLevel = role.get_skill_level(skill_type)
    # 技能技能倍率
    skill_multi = skill_damage_calc(
        char_result.skillTrees, SkillTreeMap[skill_type], "2", skillLevel
    )

    title = f"死兆"
    msg = f"技能倍率{skill_multi}"
    attr.add_effect(title, msg)

    sm = skill_multi.split("+")
    s1 = calc_percent_expression(sm[0])
    s2 = calc_percent_expression(sm[1])
    if chain_num >= 6:
        title = f"{role_name}-六链"
        msg = f"共鸣解放死兆伤害倍率提升186.6%"
        attr.add_effect(title, msg)
        s1_ratio = ((s1 + s2) * 2.866 - s2 * 2) / s1 - 1
        s2_ratio = 1
        attr.add_effect("六链技能倍率加成", f"{1 + s1_ratio:.4f} + {1 + s2_ratio}")
    else:
        s1_ratio = 0
        s2_ratio = 0

    attr1 = copy.deepcopy(attr)
    attr2 = copy.deepcopy(attr)

    attr1.add_skill_multi(s1)
    attr1.add_skill_ratio(s1_ratio)
    # 暴击伤害
    s1_crit_damage = f"{attr1.calculate_crit_damage():,.0f}"
    # 期望伤害
    s1_expected_damage = f"{attr1.calculate_expected_damage():,.0f}"

    attr2.add_skill_multi(s2)
    attr2.add_skill_ratio(s2_ratio)
    # 暴击伤害
    s2_crit_damage = f"{attr2.calculate_crit_damage():,.0f}"
    # 期望伤害
    s2_expected_damage = f"{attr2.calculate_expected_damage():,.0f}"

    crit_damage = f"{s1_crit_damage} + {s2_crit_damage}"
    expected_damage = f"{s1_expected_damage} + {s2_expected_damage}"
    return crit_damage, expected_damage


def calc_damage_r(
    attr: DamageAttribute, role: RoleDetailData, isGroup: bool = False
) -> (str, str):
    # 设置角色伤害类型
    attr.set_char_damage(skill_damage)
    # 设置角色模板  "temp_atk", "temp_life", "temp_def"
    attr.set_char_template("temp_atk")

    title = "默认手法"
    if isGroup:
        msg = "变奏入场 ee aa aaa z qr aaaaa"
    else:
        msg = "ee aa aaa z qr aaaaa"
    attr.add_effect(title, msg)

    role_name = role.role.roleName
    # 获取角色详情
    char_result: WavesCharResult = get_char_detail2(role)

    skill_type: SkillType = "共鸣解放"
    # 获取角色技能等级
    skillLevel = role.get_skill_level(skill_type)
    # 技能技能倍率
    skill_multi = skill_damage_calc(
        char_result.skillTrees, SkillTreeMap[skill_type], "1", skillLevel
    )
    title = f"新浪潮时代"
    msg = f"技能倍率{skill_multi}"
    attr.add_skill_multi(skill_multi, title, msg)

    # 设置角色施放技能
    damage_func = [cast_attack, cast_skill, cast_hit, cast_liberation]
    phase_damage(attr, role, damage_func, isGroup)

    # 设置角色等级
    attr.set_character_level(role.role.level)

    # 设置角色固有技能
    role_breach = role.role.breach
    if role_breach and role_breach >= 3:
        title = f"{role_name}-固有技能-艺术至上"
        msg = f"为命中的目标附加解离效果"
        attr.add_effect(title, msg)

    # 设置角色技能施放是不是也有加成 eg：守岸人

    title = f"{role_name}-解离状态"
    msg = f"造成伤害时忽视目标18%防御"
    attr.add_defense_reduction(0.18, title, msg)

    title = f"{role_name}-揭幕者状态"
    msg = f"共鸣解放死兆的伤害倍率提升80%"
    attr.add_skill_ratio_in_skill_description(0.8, title, msg)

    # 设置声骸属性
    attr.set_phantom_dmg_bonus()

    # 设置共鸣链
    chain_num = role.get_chain_num()
    if chain_num >= 1:
        title = f"{role_name}-一链"
        msg = f"对拥有解离效果的目标攻击造成伤害时，该次伤害的暴击提升12.5%"
        attr.add_crit_rate(0.125, title, msg)

    if chain_num >= 4:
        title = f"{role_name}-四链"
        msg = f"珂莱塔施放重击末路见行时，队伍中的角色共鸣技能伤害加成提升25%"
        attr.add_dmg_bonus(0.25, title, msg)

    # 声骸
    echo_damage(attr, isGroup)

    # 武器
    weapon_damage(attr, role.weaponData, damage_func, isGroup)

    # 暴击伤害
    crit_damage = f"{attr.calculate_crit_damage():,.0f}"
    # 期望伤害
    expected_damage = f"{attr.calculate_expected_damage():,.0f}"
    return crit_damage, expected_damage


def calc_damage_10(
    attr: DamageAttribute, role: RoleDetailData, isGroup: bool = True
) -> (str, str):
    """
    0+1守/0折枝/致死以终伤害
    """
    attr.set_char_damage(skill_damage)
    attr.set_char_template("temp_atk")

    # 守岸人buff
    shouanren_buff(attr, 0, 1, isGroup)

    # 折枝buff
    zhezhi_buff(attr, 0, 1, isGroup)

    return calc_damage_2(attr, role, isGroup)


def calc_damage_11(
    attr: DamageAttribute, role: RoleDetailData, isGroup: bool = True
) -> (str, str):
    """
    6+5守/6折/致死以终伤害
    """
    attr.set_char_damage(skill_damage)
    attr.set_char_template("temp_atk")

    # 守岸人buff
    shouanren_buff(attr, 6, 5, isGroup)

    # 折枝buff
    zhezhi_buff(attr, 6, 1, isGroup)

    return calc_damage_2(attr, role, isGroup)


damage_detail = [
    {
        "title": "末路见行伤害",
        "func": lambda attr, role: calc_damage_1(attr, role),
    },
    {
        "title": "死兆伤害",
        "func": lambda attr, role: calc_damage_33(attr, role),
    },
    {
        "title": "致死以终伤害",
        "func": lambda attr, role: calc_damage_2(attr, role),
    },
    {
        "title": "r总伤害",
        "func": lambda attr, role: calc_damage(attr, role),
    },
    {
        "title": "0+1守/0折/致死以终伤害",
        "func": lambda attr, role: calc_damage_10(attr, role),
    },
    {
        "title": "6+5守/6折/致死以终伤害",
        "func": lambda attr, role: calc_damage_11(attr, role),
    },
]

rank = damage_detail[3]
