# 嘉贝莉娜
from typing import Literal

from ...api.model import RoleDetailData
from ...ascension.char import WavesCharResult, get_char_detail2
from ...damage.damage import DamageAttribute
from ...damage.utils import (
    SkillTreeMap,
    SkillType,
    cast_attack,
    cast_hit,
    cast_liberation,
    cast_phantom,
    cast_skill,
    hit_damage,
    phantom_damage,
    skill_damage_calc,
)
from .damage import echo_damage, phase_damage, weapon_damage


def calc_damage_1(
    attr: DamageAttribute,
    role: RoleDetailData,
    isGroup: bool = False,
    size: Literal[1, 2, 3, 4, 5] = 1,
    char_damage: Literal["hit_damage", "phantom_damage"] = hit_damage,
) -> tuple[str, str]:
    # 设置角色伤害类型
    attr.set_char_damage(char_damage)
    # 设置角色模板  "temp_atk", "temp_life", "temp_def"
    attr.set_char_template("temp_atk")

    role_name = role.role.roleName
    # 获取角色详情
    char_result: WavesCharResult = get_char_detail2(role)

    skill_type: SkillType = "共鸣回路"
    # 获取角色技能等级
    skillLevel = role.get_skill_level(skill_type)
    # 技能技能倍率
    skillParamId = f"{size+16}"
    skill_multi = skill_damage_calc(
        char_result.skillTrees, SkillTreeMap[skill_type], skillParamId, skillLevel
    )
    title = f"普攻·炽天猎杀第{size}段"
    msg = f"技能倍率{skill_multi}"
    attr.add_skill_multi(skill_multi, title, msg)

    # 设置角色施放技能
    damage_func = [cast_attack, cast_skill, cast_hit, cast_liberation, cast_phantom]
    phase_damage(attr, role, damage_func, isGroup)

    # 设置角色等级
    attr.set_character_level(role.role.level)

    # 设置角色固有技能
    role_breach = role.role.breach
    if role_breach and role_breach >= 3:
        title = "固有技能-誓猎"
        msg = "死运既定，伤害加深5*4%"
        attr.add_dmg_deepen(0.05 * 4, title, msg)

    # 设置角色技能施放是不是也有加成 eg：守岸人

    # 共鸣解放 伤害倍率
    title = "共鸣解放-炼净"
    msg = "伤害倍率提升85%"
    attr.add_skill_ratio_in_skill_description(0.85, title, msg)

    # 设置声骸属性
    attr.set_phantom_dmg_bonus()

    # 设置共鸣链
    chain_num = role.get_chain_num()
    if chain_num >= 1:
        title = f"{role_name}-一链"
        msg = "40点余火，提升80%暴击伤害"
        attr.add_crit_dmg(0.8, title, msg)

    if chain_num >= 2:
        title = f"{role_name}-二链"
        msg = "内燃烧提供的攻击加成提升350%。"
        attr.add_atk_percent(0.2 * (1 + 3.5), title, msg)
    else:
        # 内燃烧 buff
        title = "内燃烧"
        msg = "嘉贝莉娜的攻击提升20%"
        attr.add_atk_percent(0.2, title, msg)

    if chain_num >= 4:
        title = f"{role_name}-四链"
        msg = "施放声骸技能时，全属性伤害加成提升20%"
        attr.add_dmg_bonus(0.2, title, msg)

    if chain_num >= 6:
        title = f"{role_name}-六链"
        msg = "伤害倍率提升60%"
        attr.add_skill_ratio(0.6, title, msg)

        msg = "永恒位格余火提供35%热熔伤害加深"
        attr.add_dmg_deepen(0.35, title, msg)

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
    size: Literal[1, 2, 3] = 1,
    char_damage: Literal["hit_damage", "phantom_damage"] = hit_damage,
) -> tuple[str, str]:
    # 设置角色伤害类型
    attr.set_char_damage(char_damage)
    # 设置角色模板  "temp_atk", "temp_life", "temp_def"
    attr.set_char_template("temp_atk")

    role_name = role.role.roleName
    # 获取角色详情
    char_result: WavesCharResult = get_char_detail2(role)

    skill_type: SkillType = "共鸣回路"
    # 获取角色技能等级
    skillLevel = role.get_skill_level(skill_type)
    # 技能技能倍率
    skillParamId = f"{size+21}"
    skill_multi = skill_damage_calc(
        char_result.skillTrees, SkillTreeMap[skill_type], skillParamId, skillLevel
    )
    title = f"重击·炼羽裁决第{size}段"
    msg = f"技能倍率{skill_multi}"
    attr.add_skill_multi(skill_multi, title, msg)

    # 设置角色施放技能
    damage_func = [cast_attack, cast_skill, cast_hit, cast_liberation, cast_phantom]
    phase_damage(attr, role, damage_func, isGroup)

    # 设置角色等级
    attr.set_character_level(role.role.level)

    # 设置角色固有技能
    role_breach = role.role.breach
    if role_breach and role_breach >= 3:
        title = "固有技能-誓猎"
        msg = "死运既定，伤害加深5*4%"
        attr.add_dmg_deepen(0.05 * 4, title, msg)

    # 设置角色技能施放是不是也有加成 eg：守岸人

    # 共鸣解放 伤害倍率
    title = "共鸣解放-炼净"
    msg = "伤害倍率提升85%"
    attr.add_skill_ratio_in_skill_description(0.85, title, msg)

    # 设置声骸属性
    attr.set_phantom_dmg_bonus()

    # 设置共鸣链
    chain_num = role.get_chain_num()
    if chain_num >= 1:
        title = f"{role_name}-一链"
        msg = "40点余火，提升80%暴击伤害"
        attr.add_crit_dmg(0.8, title, msg)

    if chain_num >= 2:
        title = f"{role_name}-二链"
        msg = "内燃烧提供的攻击加成提升350%。"
        attr.add_atk_percent(0.2 * (1 + 3.5), title, msg)
    else:
        # 内燃烧 buff
        title = "内燃烧"
        msg = "嘉贝莉娜的攻击提升20%"
        attr.add_atk_percent(0.2, title, msg)

    if chain_num >= 4:
        title = f"{role_name}-四链"
        msg = "施放声骸技能时，全属性伤害加成提升20%"
        attr.add_dmg_bonus(0.2, title, msg)

    if chain_num >= 6:
        title = f"{role_name}-六链"
        msg = "伤害倍率提升60%"
        attr.add_skill_ratio(0.6, title, msg)

        msg = "永恒位格余火提供35%热熔伤害加深"
        attr.add_dmg_deepen(0.35, title, msg)

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
    attr: DamageAttribute,
    role: RoleDetailData,
    isGroup: bool = False,
) -> tuple[str, str]:
    # 设置角色伤害类型
    attr.set_char_damage(phantom_damage)
    # 设置角色模板  "temp_atk", "temp_life", "temp_def"
    attr.set_char_template("temp_atk")

    role_name = role.role.roleName
    # 获取角色详情
    char_result: WavesCharResult = get_char_detail2(role)

    skill_type: SkillType = "共鸣解放"
    # 获取角色技能等级
    skillLevel = role.get_skill_level(skill_type)
    # 技能技能倍率
    skill_multi = skill_damage_calc(
        char_result.skillTrees, SkillTreeMap[skill_type], "16", skillLevel
    )
    title = "共鸣解放·炼净伤害"
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
        title = "固有技能-誓猎"
        msg = "死运既定，伤害加深5*4%"
        attr.add_dmg_deepen(0.05 * 4, title, msg)

    # 设置角色技能施放是不是也有加成 eg：守岸人

    # 设置声骸属性
    attr.set_phantom_dmg_bonus()

    # 设置共鸣链
    chain_num = role.get_chain_num()
    if chain_num >= 2:
        title = f"{role_name}-二链"
        msg = "内燃烧提供的攻击加成提升350%。"
        attr.add_atk_percent(0.2 * (1 + 3.5), title, msg)
    else:
        # 内燃烧 buff
        title = "内燃烧"
        msg = "嘉贝莉娜的攻击提升20%"
        attr.add_atk_percent(0.2, title, msg)

    if chain_num >= 3:
        title = f"{role_name}-三链"
        msg = "共鸣解放的伤害倍率提升130%。"
        attr.add_skill_ratio(1.3, title, msg)

    if chain_num >= 4:
        title = f"{role_name}-四链"
        msg = "施放声骸技能时，全属性伤害加成提升20%"
        attr.add_dmg_bonus(0.2, title, msg)

    # 声骸
    echo_damage(attr, isGroup)

    # 武器
    weapon_damage(attr, role.weaponData, damage_func, isGroup)

    # 暴击伤害
    crit_damage = f"{attr.calculate_crit_damage():,.0f}"
    # 期望伤害
    expected_damage = f"{attr.calculate_expected_damage():,.0f}"
    return crit_damage, expected_damage


damage_detail = [
    {
        "title": "普攻·炽天猎杀第3段",
        "func": lambda attr, role: calc_damage_1(attr, role, size=3),
    },
    {
        "title": "普攻·炽天猎杀第5段",
        "func": lambda attr, role: calc_damage_1(
            attr, role, size=5, char_damage=phantom_damage
        ),
    },
    {
        "title": "重击·炼羽裁决第3段",
        "func": lambda attr, role: calc_damage_2(
            attr, role, size=3, char_damage=phantom_damage
        ),
    },
    {
        "title": "共鸣解放·炼净",
        "func": lambda attr, role: calc_damage_3(attr, role),
    },
]

rank = damage_detail[1]
