# 釉瑚
from typing import List, Optional, Union

from ...api.model import RoleDetailData
from ...ascension.char import WavesCharResult, get_char_detail2
from ...damage.damage import DamageAttribute
from ...damage.utils import (
    SkillTreeMap,
    SkillType,
    cast_attack,
    cast_hit,
    cast_liberation,
    cast_skill,
    heal_bonus,
    skill_damage,
    skill_damage_calc,
)
from .damage import echo_damage, phase_damage, weapon_damage


def skill_effect(attr, role_name, skill_type, isChain):
    if "联珠" in skill_type:
        if isChain:
            title = f"{role_name}-二链-联珠"
        else:
            title = f"{role_name}-联珠"
        msg = "拥有三个相同的【吉兆】时。诗中物造成的伤害提升175%"
        attr.add_dmg_bonus(1.75, title, msg)
    elif "对偶" in skill_type:
        if isChain:
            title = f"{role_name}-二链-对偶"
        else:
            title = f"{role_name}-对偶"
        msg = "拥有一对相同的【吉兆】时。诗中物造成的伤害提升70%"
        attr.add_dmg_bonus(0.7, title, msg)


def calc_damage_1(
    attr: DamageAttribute,
    role: RoleDetailData,
    isGroup: bool = False,
    skill_name: Union[str, List[str]] = "",
) -> tuple[str, str]:
    # 设置角色伤害类型
    attr.set_char_damage(skill_damage)
    # 设置角色模板  "temp_atk", "temp_life", "temp_def"
    attr.set_char_template("temp_atk")

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
    title = "诗中物"
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
        if isGroup:
            title = f"{role_name}-固有技能"
            msg = "施放变奏技能遂心匣时，釉瑚的冷凝伤害加成提升15%"
            attr.add_dmg_bonus(0.15, title, msg)

    skill_effect(attr, role_name, skill_name, False)

    # 设置角色技能施放是不是也有加成 eg：守岸人

    # 设置声骸属性
    attr.set_phantom_dmg_bonus()

    # 设置共鸣链
    chain_num = role.get_chain_num()
    if chain_num >= 2:
        skill_effect(attr, role_name, skill_name, True)

    if chain_num >= 3:
        title = f"{role_name}-三链"
        msg = "釉瑚的攻击提升20%。"
        attr.add_atk_percent(0.2, title, msg)

    if chain_num >= 5:
        if isGroup:
            title = f"{role_name}-五链"
            msg = "施放变奏技能遂心匣时，釉瑚的暴击提升15%"
            attr.add_crit_rate(0.15, title, msg)

    if chain_num >= 6:
        title = f"{role_name}-六链"
        msg = "4层霁青效果，暴击伤害提升15%*4"
        attr.add_crit_dmg(0.15 * 4, title, msg)

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
    attr: DamageAttribute,
    role: RoleDetailData,
    isGroup: bool = False,
    skill_name: Union[str, List[str]] = "",
) -> tuple[Optional[str], str]:
    damage_func = [cast_attack, cast_skill, cast_hit, cast_liberation]
    attr.set_char_damage(heal_bonus)
    attr.set_char_template("temp_atk")

    role_name = role.role.roleName
    # 获取角色详情
    char_result: WavesCharResult = get_char_detail2(role)

    skill_type: SkillType = "共鸣回路"
    # 获取角色技能等级
    skillLevel = role.get_skill_level(skill_type)

    if "双关" in skill_name:
        # 技能技能倍率
        skill_multi = skill_damage_calc(
            char_result.skillTrees, SkillTreeMap[skill_type], "3", skillLevel
        )
        title = "双关额外治疗量"
        msg = f"技能倍率{skill_multi}"
    else:
        # 技能技能倍率
        skill_multi = skill_damage_calc(
            char_result.skillTrees, SkillTreeMap[skill_type], "2", skillLevel
        )
        title = "诗中物治疗量"
        msg = f"技能倍率{skill_multi}"
    attr.add_healing_skill_multi(skill_multi, title, msg)

    # 设置角色等级
    attr.set_character_level(role.role.level)

    attr.set_phantom_dmg_bonus(needShuxing=False)

    # chain_num = role.get_chain_num()

    echo_damage(attr, isGroup)

    weapon_damage(attr, role.weaponData, damage_func, isGroup)

    healing_bonus = attr.calculate_healing(attr.effect_attack)

    crit_damage = f"{healing_bonus:,.0f}"
    return None, crit_damage


def calc_damage_3(
    attr: DamageAttribute, role: RoleDetailData, isGroup: bool = False
) -> tuple[Optional[str], str]:
    damage_func = [cast_attack, cast_skill, cast_hit, cast_liberation]
    attr.set_char_damage(heal_bonus)
    attr.set_char_template("temp_atk")

    role_name = role.role.roleName
    # 获取角色详情
    char_result: WavesCharResult = get_char_detail2(role)

    skill_type: SkillType = "共鸣技能"
    # 获取角色技能等级
    skillLevel = role.get_skill_level(skill_type)
    # 技能技能倍率
    skill_multi = skill_damage_calc(
        char_result.skillTrees, SkillTreeMap[skill_type], "2", skillLevel
    )
    title = "匣中问祯治疗量"
    msg = f"技能倍率{skill_multi}"
    attr.add_healing_skill_multi(skill_multi, title, msg)

    # 设置角色等级
    attr.set_character_level(role.role.level)

    attr.set_phantom_dmg_bonus(needShuxing=False)

    # chain_num = role.get_chain_num()

    echo_damage(attr, isGroup)

    weapon_damage(attr, role.weaponData, damage_func, isGroup)

    healing_bonus = attr.calculate_healing(attr.effect_attack)

    crit_damage = f"{healing_bonus:,.0f}"
    return None, crit_damage


damage_detail = [
    {
        "title": "对偶伤害",
        "func": lambda attr, role: calc_damage_1(attr, role, skill_name="对偶"),
    },
    {
        "title": "联珠伤害",
        "func": lambda attr, role: calc_damage_1(attr, role, skill_name="联珠"),
    },
    {
        "title": "双关治疗量",
        "func": lambda attr, role: calc_damage_2(attr, role, skill_name="双关"),
    },
    {
        "title": "诗中物治疗量",
        "func": lambda attr, role: calc_damage_2(attr, role, skill_name="诗中物"),
    },
    {
        "title": "匣中问祯治疗量",
        "func": lambda attr, role: calc_damage_3(attr, role),
    },
]

rank = damage_detail[1]
