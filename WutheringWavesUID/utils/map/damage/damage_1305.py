# 相里要
from .damage import weapon_damage, echo_damage, phase_damage
from ...api.model import RoleDetailData
from ...ascension.char import get_char_detail, WavesCharResult
from ...damage.damage import DamageAttribute
from ...damage.utils import (
    skill_damage_calc,
    cast_skill,
    cast_liberation,
    liberation_damage,
    cast_hit,
)


def calc_damage_1(
    attr: DamageAttribute, role: RoleDetailData, isGroup: bool = False
) -> (str, str):
    """
    万方法则
    """
    attr.set_char_damage(liberation_damage)
    attr.set_char_template("temp_atk")

    role_name = role.role.roleName
    role_id = role.role.roleId
    role_level = role.role.level
    role_breach = role.role.breach
    char_result: WavesCharResult = get_char_detail(role_id, role_level, role_breach)

    # 万方法则 技能倍率
    skillLevel = role.get_skill_level("共鸣回路")
    # 技能倍率
    skill_multi = skill_damage_calc(char_result.skillTrees, "7", "2", skillLevel)
    title = "万方法则"
    msg = f"技能倍率{skill_multi}"
    attr.add_skill_multi(skill_multi, title, msg)

    # 设置角色等级
    attr.set_character_level(role_level)

    damage_func = [cast_liberation, cast_skill, cast_hit]
    phase_damage(attr, role, damage_func, isGroup)

    if role_breach and role_breach >= 3:
        title = f"{role_name}-固有技能-睿知"
        msg = f"施放共鸣技能时，导电伤害加成提升5%*4"
        attr.add_dmg_bonus(0.20, title, msg)

    attr.set_phantom_dmg_bonus()

    chain_num = role.get_chain_num()
    if chain_num >= 2:
        title = f"{role_name}-二链"
        msg = "施放共鸣技能或共鸣解放思维矩阵时，自身暴击伤害提升30%。"
        attr.add_crit_dmg(0.3, title, msg)

    if chain_num >= 3:
        title = f"{role_name}-三链"
        msg = "施放共鸣解放思维矩阵后，后续5次共鸣技能伤害提升63%。"
        attr.add_dmg_bonus(0.63, title, msg)

    if chain_num >= 4:
        title = f"{role_name}-四链"
        msg = "施放共鸣解放思维矩阵时，全队共鸣解放伤害加成提升25%。"
        attr.add_dmg_bonus(0.25, title, msg)

    if chain_num >= 6:
        title = f"{role_name}-六链"
        msg = "共鸣技能万方法则伤害倍率提升76%。"
        attr.add_skill_ratio(0.76, title, msg)

    # 声骸技能
    echo_damage(attr, isGroup)

    # 武器谐振
    weapon_damage(attr, role.weaponData, damage_func, isGroup)

    # 暴击伤害
    crit_damage = f"{attr.calculate_crit_damage():,.0f}"
    # 期望伤害
    expected_damage = f"{attr.calculate_expected_damage():,.0f}"
    return crit_damage, expected_damage


def calc_damage_2(
    attr: DamageAttribute, role: RoleDetailData, isGroup: bool = False
) -> (str, str):
    """
    思维矩阵
    """
    attr.set_char_damage(liberation_damage)
    attr.set_char_template("temp_atk")

    role_name = role.role.roleName
    role_id = role.role.roleId
    role_level = role.role.level
    role_breach = role.role.breach
    char_result: WavesCharResult = get_char_detail(role_id, role_level, role_breach)

    # 思维矩阵 技能倍率
    skillLevel = role.get_skill_level("共鸣解放")
    # 技能倍率
    skill_multi = skill_damage_calc(char_result.skillTrees, "3", "1", skillLevel)
    title = "万方法则"
    msg = f"技能倍率{skill_multi}"
    attr.add_skill_multi(skill_multi, title, msg)

    # 设置角色等级
    attr.set_character_level(role_level)

    damage_func = [cast_liberation, cast_skill, cast_hit]
    phase_damage(attr, role, damage_func, isGroup)

    if role_breach and role_breach >= 3:
        title = f"{role_name}-固有技能-睿知"
        msg = f"施放共鸣技能时，导电伤害加成提升5%*4"
        attr.add_dmg_bonus(0.20, title, msg)

    attr.set_phantom_dmg_bonus()

    chain_num = role.get_chain_num()
    if chain_num >= 2:
        title = f"{role_name}-二链"
        msg = "施放共鸣技能或共鸣解放思维矩阵时，自身暴击伤害提升30%。"
        attr.add_crit_dmg(0.3, title, msg)

    if chain_num >= 4:
        title = f"{role_name}-四链"
        msg = "施放共鸣解放思维矩阵时，全队共鸣解放伤害加成提升25%。"
        attr.add_dmg_bonus(0.25, title, msg)

    if chain_num >= 5:
        title = f"{role_name}-五链"
        msg = "共鸣解放思维矩阵伤害倍率提升100%。"
        attr.add_skill_ratio(1, title, msg)

    # 声骸技能
    echo_damage(attr, isGroup)

    # 武器谐振
    weapon_damage(attr, role.weaponData, damage_func, isGroup)

    # 暴击伤害
    crit_damage = f"{attr.calculate_crit_damage():,.0f}"
    # 期望伤害
    expected_damage = f"{attr.calculate_expected_damage():,.0f}"
    return crit_damage, expected_damage


damage_detail = [
    {
        "title": "万方法则",
        "func": lambda attr, role: calc_damage_1(attr, role),
    },
    {
        "title": "思维矩阵",
        "func": lambda attr, role: calc_damage_2(attr, role),
    },
]

rank = damage_detail[0]
