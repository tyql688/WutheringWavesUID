# 千咲

from ...api.model import RoleDetailData
from ...ascension.char import WavesCharResult, get_char_detail
from ...damage.damage import DamageAttribute
from ...damage.utils import (
    SkillTreeMap,
    SkillType,
    cast_attack,
    cast_liberation,
    cast_skill,
    cast_variation,
    heal_bonus,
    liberation_damage,
    skill_damage_calc,
)
from .buff import shouanren_buff
from .damage import echo_damage, phase_damage, weapon_damage


def calc_damage_1(
    attr: DamageAttribute, role: RoleDetailData, isGroup: bool = False
) -> tuple[str, str]:
    """
    即刻·归无伤害
    """
    attr.set_char_damage(liberation_damage)
    attr.set_char_template("temp_atk")
    # 设置虚湮效应
    attr.set_env_havoc_bane()

    role_name = role.role.roleName
    role_id = role.role.roleId
    role_level = role.role.level
    role_breach = role.role.breach
    # 获取角色详情
    char_result: WavesCharResult = get_char_detail(role_id, role_level, role_breach)

    skill_type: SkillType = "共鸣解放"
    # 获取角色技能等级
    skillLevel = role.get_skill_level(skill_type)
    # 技能倍率 即刻·归无 1741.49%
    skill_multi = skill_damage_calc(
        char_result.skillTrees, SkillTreeMap[skill_type], "20", skillLevel
    )
    title = "即刻·归无伤害"
    msg = f"技能倍率{skill_multi}"
    attr.add_skill_multi(skill_multi, title, msg)

    # 设置角色施放技能
    damage_func = [cast_attack, cast_skill, cast_variation, cast_liberation]
    phase_damage(attr, role, damage_func, isGroup)

    # 设置角色等级
    attr.set_character_level(role_level)

    # 设置角色固有技能
    if role_breach is not None and role_breach >= 3:
        title = "固有技能-终点在此处"
        msg = "施放共鸣解放后，虚湮伤害加成提升20%"
        attr.add_dmg_bonus(0.2, title, msg)

    # 设置声骸属性
    attr.set_phantom_dmg_bonus()

    # 设置共鸣链
    chain_num = role.get_chain_num()
    if chain_num >= 3:
        title = f"{role_name}-三链"
        msg = "即刻·归无倍率提升80%"
        attr.add_skill_ratio(0.8, title, msg)

    if chain_num >= 4 and isGroup:
        title = f"{role_name}-四链"
        msg = "施放共鸣解放后，队伍中的角色攻击提升20%"
        attr.add_atk_percent(0.2, title, msg)

    if chain_num >= 6:
        title = f"{role_name}-六链"
        msg = "即刻·归无暴击伤害提升50%"
        attr.add_crit_dmg(0.5, title, msg)

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
) -> tuple[str, str]:
    """
    即刻·归无治疗量
    """
    attr.set_char_damage(heal_bonus)
    attr.set_char_template("temp_atk")

    role_name = role.role.roleName
    role_id = role.role.roleId
    role_level = role.role.level
    role_breach = role.role.breach
    # 获取角色详情
    char_result: WavesCharResult = get_char_detail(role_id, role_level, role_breach)

    skill_type: SkillType = "共鸣解放"
    # 获取角色技能等级
    skillLevel = role.get_skill_level(skill_type)
    # 治疗倍率 即刻·归无 214.61% + 4854
    skill_multi = skill_damage_calc(
        char_result.skillTrees, SkillTreeMap[skill_type], "21", skillLevel
    )
    title = "即刻·归无治疗量"
    msg = f"技能倍率{skill_multi}"
    attr.add_healing_skill_multi(skill_multi, title, msg)

    # 设置角色施放技能
    damage_func = [cast_attack, cast_skill, cast_variation, cast_liberation]

    # 设置角色等级
    attr.set_character_level(role_level)

    # 设置角色固有技能
    if role_breach is not None and role_breach >= 3:
        title = "固有技能-终点在此处"
        msg = "施放共鸣解放后，治疗效果加成提升20%"
        attr.add_dmg_bonus(0.2, title, msg)

    # 设置声骸属性
    attr.set_phantom_dmg_bonus(needShuxing=False)

    # 设置共鸣链
    chain_num = role.get_chain_num()
    if chain_num >= 5:
        title = f"{role_name}-五链"
        msg = "即刻·归无治疗效果提升30%"
        attr.add_dmg_bonus(0.3, title, msg)

    # 声骸
    echo_damage(attr, isGroup)

    # 武器
    weapon_damage(attr, role.weaponData, damage_func, isGroup)

    # 治疗量
    healing_bonus = attr.calculate_healing(attr.effect_attack)
    crit_damage = f"{healing_bonus:,.0f}"
    return None, crit_damage


def calc_damage_3(
    attr: DamageAttribute, role: RoleDetailData, isGroup: bool = True
) -> tuple[str, str]:
    """
    65守/即刻·归无伤害
    """
    attr.set_char_damage(liberation_damage)
    attr.set_char_template("temp_atk")
    # 守岸人buff
    shouanren_buff(attr, 6, 5, isGroup)

    return calc_damage_1(attr, role, isGroup)


damage_detail = [
    {
        "title": "即刻·归无伤害",
        "func": lambda attr, role: calc_damage_1(attr, role),
    },
    {
        "title": "即刻·归无治疗量",
        "func": lambda attr, role: calc_damage_2(attr, role),
    },
    {
        "title": "65守/即刻·归无伤害",
        "func": lambda attr, role: calc_damage_3(attr, role),
    },
]

rank = damage_detail[0]
