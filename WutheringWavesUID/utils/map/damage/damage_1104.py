# 凌阳
import copy

from gsuid_core.logger import logger
from .damage import echo_damage, weapon_damage, phase_damage
from ...api.model import RoleDetailData
from ...ascension.char import WavesCharResult, get_char_detail2
from ...damage.damage import DamageAttribute
from ...damage.utils import skill_damage_calc, SkillType, SkillTreeMap, liberation_damage, cast_liberation, \
    attack_damage, cast_attack, cast_skill, skill_damage


def calc_damage(attr: DamageAttribute, role: RoleDetailData, isGroup: bool = False) -> (str, str):
    attr1 = copy.deepcopy(attr)
    crit_damage1, expected_damage1 = calc_damage_1(attr1, role, isGroup)

    attr2 = copy.deepcopy(attr)
    crit_damage2, expected_damage2 = calc_damage_a(attr2, role, isGroup)

    attr3 = copy.deepcopy(attr)
    crit_damage3, expected_damage3 = calc_damage_e(attr3, role, isGroup)

    attr4 = copy.deepcopy(attr)
    crit_damage4, expected_damage4 = calc_damage_ea(attr4, role, isGroup)

    crit_damage = crit_damage1 + crit_damage2 + crit_damage3 + crit_damage4
    expected_damage = expected_damage1 + expected_damage2 + expected_damage3 + expected_damage4
    # 暴击伤害
    crit_damage = f"{crit_damage:,.0f}"
    # 期望伤害
    expected_damage = f"{expected_damage:,.0f}"

    attr.add_effect(' ', ' ')
    attr.effect.extend(attr1.effect[2:])
    attr.add_effect(' ', ' ')
    attr.effect.extend(attr2.effect[2:])
    attr.add_effect(' ', ' ')
    attr.effect.extend(attr3.effect[2:])
    attr.add_effect(' ', ' ')
    attr.effect.extend(attr4.effect[2:])
    return crit_damage, expected_damage


def calc_damage_1(attr: DamageAttribute, role: RoleDetailData, isGroup: bool = False) -> (str, str):
    # 设置角色伤害类型
    attr.set_char_damage(liberation_damage)
    # 设置角色模板  "temp_atk", "temp_life", "temp_def"
    attr.set_char_template('temp_atk')

    role_name = role.role.roleName
    # 获取角色详情
    char_result: WavesCharResult = get_char_detail2(role)

    skill_type: SkillType = "共鸣解放"
    # 获取角色技能等级
    skillLevel = role.get_skill_level(skill_type)
    # 技能技能倍率
    skill_multi = skill_damage_calc(char_result.skillTrees, SkillTreeMap[skill_type], "1", skillLevel)
    title = f"共鸣解放"
    msg = f"技能倍率{skill_multi}"
    attr.add_skill_multi(skill_multi, title, msg)

    # 设置角色施放技能
    damage_func = [cast_liberation]
    phase_damage(attr, role, damage_func, isGroup)

    # 设置角色等级
    attr.set_character_level(role.role.level)

    # 设置角色固有技能
    role_breach = role.role.breach

    # 设置角色技能施放是不是也有加成 eg：守岸人

    # 设置声骸属性
    attr.set_phantom_dmg_bonus()

    # 设置命座
    chain_num = role.get_chain_num()
    if chain_num >= 5:
        title = f"{role_name}-五命"
        msg = f"施放共鸣解放时，将额外造成凌阳200%攻击的冷凝伤害"
        attr.add_skill_multi(2, title, msg)

    # 声骸
    echo_damage(attr, isGroup)

    # 武器
    weapon_damage(attr, role.weaponData, damage_func, isGroup)

    # 暴击伤害
    crit_damage = attr.calculate_crit_damage()
    # 期望伤害
    expected_damage = attr.calculate_expected_damage()

    attr.add_effect("r伤害", f"期望伤害:{crit_damage:,.0f}; 暴击伤害:{expected_damage:,.0f}")

    logger.debug(f"{role_name}- 属性值: {attr}")
    return crit_damage, expected_damage


def calc_damage_a(attr: DamageAttribute, role: RoleDetailData, isGroup: bool = False) -> (str, str):
    # 设置角色伤害类型
    attr.set_char_damage(attack_damage)
    # 设置角色模板  "temp_atk", "temp_life", "temp_def"
    attr.set_char_template('temp_atk')

    role_name = role.role.roleName
    # 获取角色详情
    char_result: WavesCharResult = get_char_detail2(role)

    skill_type: SkillType = "共鸣回路"
    # 获取角色技能等级
    skillLevel = role.get_skill_level(skill_type)
    # 技能技能倍率
    skill_multi = skill_damage_calc(char_result.skillTrees, SkillTreeMap[skill_type], "3", skillLevel)
    title = f"a第一段"
    msg = f"技能倍率{skill_multi}"
    attr.add_skill_multi(skill_multi, title, msg)

    # 设置角色施放技能
    damage_func = [cast_liberation, cast_attack]
    phase_damage(attr, role, damage_func, isGroup)

    # 设置角色等级
    attr.set_character_level(role.role.level)

    # 设置角色固有技能
    role_breach = role.role.breach
    if role_breach and role_breach >= 3:
        pass

    # 设置角色技能施放是不是也有加成 eg：守岸人

    # 设置声骸属性
    attr.set_phantom_dmg_bonus()

    # 设置命座
    chain_num = role.get_chain_num()
    if chain_num >= 3:
        title = f"{role_name}-三命"
        msg = f"共鸣解放狮子奋迅持续期间，凌阳的普攻伤害加成提升20%"
        attr.add_dmg_bonus(0.2, title, msg)

    # 声骸
    echo_damage(attr, isGroup)

    # 武器
    weapon_damage(attr, role.weaponData, damage_func, isGroup)

    # 暴击伤害
    crit_damage = attr.calculate_crit_damage()
    # 期望伤害
    expected_damage = attr.calculate_expected_damage()

    attr.add_effect("a第一段伤害", f"期望伤害:{crit_damage:,.0f}; 暴击伤害:{expected_damage:,.0f}")

    logger.debug(f"{role_name}- 属性值: {attr}")
    return crit_damage, expected_damage


def calc_damage_ea(attr: DamageAttribute, role: RoleDetailData, isGroup: bool = False) -> (str, str):
    # 设置角色伤害类型
    attr.set_char_damage(attack_damage)
    # 设置角色模板  "temp_atk", "temp_life", "temp_def"
    attr.set_char_template('temp_atk')

    role_name = role.role.roleName
    # 获取角色详情
    char_result: WavesCharResult = get_char_detail2(role)

    skill_type: SkillType = "共鸣回路"
    # 获取角色技能等级
    skillLevel = role.get_skill_level(skill_type)
    # 技能技能倍率
    skill_multi = skill_damage_calc(char_result.skillTrees, SkillTreeMap[skill_type], "3", skillLevel)
    skill_multi = f"({skill_multi})*2"
    title = f"a第一段"
    msg = f"技能倍率{skill_multi}"
    attr.add_skill_multi(skill_multi, title, msg)

    skill_multi = skill_damage_calc(char_result.skillTrees, SkillTreeMap[skill_type], "4", skillLevel)
    skill_multi = f"({skill_multi})*2"
    title = f"a第二段"
    msg = f"技能倍率{skill_multi}"
    attr.add_skill_multi(skill_multi, title, msg)

    # 设置角色施放技能
    damage_func = [cast_liberation, cast_attack, cast_skill]
    phase_damage(attr, role, damage_func, isGroup)

    # 设置角色等级
    attr.set_character_level(role.role.level)

    # 设置角色固有技能
    role_breach = role.role.breach
    if role_breach and role_breach >= 3:
        pass

    # 设置角色技能施放是不是也有加成 eg：守岸人

    # 设置声骸属性
    attr.set_phantom_dmg_bonus()

    # 设置命座
    chain_num = role.get_chain_num()
    if chain_num >= 3:
        title = f"{role_name}-三命"
        msg = f"共鸣解放狮子奋迅持续期间，凌阳的普攻伤害加成提升20%"
        attr.add_dmg_bonus(0.2, title, msg)

    if chain_num >= 6:
        title = f"{role_name}-六命"
        msg = f"奋迅持续期间，施放共鸣技能，下一次普攻伤害加成提升100%"
        attr.add_dmg_bonus(1, title, msg)

    # 声骸
    echo_damage(attr, isGroup)

    # 武器
    weapon_damage(attr, role.weaponData, damage_func, isGroup)

    # 暴击伤害
    crit_damage = attr.calculate_crit_damage()
    # 期望伤害
    expected_damage = attr.calculate_expected_damage()

    attr.add_effect("4a总伤害", f"期望伤害:{crit_damage:,.0f}; 暴击伤害:{expected_damage:,.0f}")

    logger.debug(f"{role_name}- 属性值: {attr}")
    return crit_damage, expected_damage


def calc_damage_e(attr: DamageAttribute, role: RoleDetailData, isGroup: bool = False) -> (str, str):
    # 设置角色伤害类型
    attr.set_char_damage(skill_damage)
    # 设置角色模板  "temp_atk", "temp_life", "temp_def"
    attr.set_char_template('temp_atk')

    role_name = role.role.roleName
    # 获取角色详情
    char_result: WavesCharResult = get_char_detail2(role)

    skill_type: SkillType = "共鸣回路"
    # 获取角色技能等级
    skillLevel = role.get_skill_level(skill_type)
    # 技能技能倍率
    skill_multi = skill_damage_calc(char_result.skillTrees, SkillTreeMap[skill_type], "5", skillLevel)
    skill_multi = f"({skill_multi})*5"
    title = f"e"
    msg = f"技能倍率{skill_multi}"
    attr.add_skill_multi(skill_multi, title, msg)

    # 设置角色施放技能
    damage_func = [cast_liberation, cast_attack, cast_skill]
    phase_damage(attr, role, damage_func, isGroup)

    # 设置角色等级
    attr.set_character_level(role.role.level)

    # 设置角色固有技能
    role_breach = role.role.breach
    if role_breach and role_breach >= 3:
        title = f"{role_name}-固有技能-勤修苦练"
        msg = f"在行狮状态下，每次施放普攻后，伤害为共鸣回路的150%。"
        attr.add_skill_ratio(1.5, title, msg)

    # 设置角色技能施放是不是也有加成 eg：守岸人

    # 设置声骸属性
    attr.set_phantom_dmg_bonus()

    # 设置命座
    chain_num = role.get_chain_num()
    if chain_num >= 3:
        title = f"{role_name}-三命"
        msg = f"共鸣解放狮子奋迅持续期间，共鸣技能伤害加成提升10%"
        attr.add_dmg_bonus(0.1, title, msg)

    # 声骸
    echo_damage(attr, isGroup)

    # 武器
    weapon_damage(attr, role.weaponData, damage_func, isGroup)

    # 暴击伤害
    crit_damage = attr.calculate_crit_damage()
    # 期望伤害
    expected_damage = attr.calculate_expected_damage()

    attr.add_effect("5e总伤害", f"期望伤害:{crit_damage:,.0f}; 暴击伤害:{expected_damage:,.0f}")

    logger.debug(f"{role_name}- 属性值: {attr}")
    return crit_damage, expected_damage


damage_detail = [
    {
        "title": "r5ae总伤",
        "func": lambda attr, role: calc_damage(attr, role),
    }
]

rank = damage_detail[0]
