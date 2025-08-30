# 奥古斯塔

from typing import Tuple

from ...api.model import RoleDetailData
from .damage import echo_damage, phase_damage, weapon_damage
from ...ascension.char import WavesCharResult, get_char_detail2
from ...damage.damage import DamageAttribute, calc_percent_expression
from ...damage.utils import (
    SkillType,
    SkillTreeMap,
    cast_hit,
    cast_skill,
    hit_damage,
    cast_attack,
    cast_liberation,
    skill_damage_calc,
)


def chain_damage(
    attr: DamageAttribute,
    role: RoleDetailData,
    isGroup: bool = False,
):
    role_name = role.role.roleName
    # 设置共鸣链
    chain_num = role.get_chain_num()
    if chain_num >= 6:
        # 4层以众愿为冕 - 15爆伤，15导电，20暴击
        title = f"{role_name}-六链-以众愿为冕"
        msg = "暴击伤害15%*4+导电伤害加成提升15%*4+暴击率20%*4"
        attr.add_crit_dmg(0.15 * 4)
        attr.add_dmg_bonus(0.15 * 4)
        attr.add_crit_rate(0.2 * 4)
        attr.add_effect(title, msg)

        # 暴击高于100%时，每多出1%暴击，奥古斯塔暴击伤害提升2%，最高可提升100%暴击伤害
        crit_rate = attr.crit_rate
        if crit_rate > 1:
            crit_rate = crit_rate - 1
            crit_rate_bonus = min(max(crit_rate / 0.01, 0), 50)
            add_crit_dmg = crit_rate_bonus * 2 * 0.01
            title = f"{role_name}-二链"
            msg = f"爆伤提升{add_crit_dmg*100:.2f}%"
            attr.add_crit_dmg(add_crit_dmg, title, msg)

        # 暴击高于150%时，每多出1%暴击，奥古斯塔暴击伤害提升2%，最高可提升50%暴击伤害
        crit_rate = attr.crit_rate
        if crit_rate > 1.5:
            crit_rate = crit_rate - 1.5
            crit_rate_bonus = min(max(crit_rate / 0.01, 0), 25)
            add_crit_dmg = crit_rate_bonus * 2 * 0.01
            title = f"{role_name}-六链"
            msg = f"爆伤提升{add_crit_dmg*100:.2f}%"
            attr.add_crit_dmg(add_crit_dmg, title, msg)

    elif chain_num >= 2:
        # 2层以众愿为冕 - 15爆伤，15导电，20暴击
        title = f"{role_name}-二链-以众愿为冕"
        msg = "暴击伤害15%*2+导电伤害加成提升15%*2+暴击率20%*2"
        attr.add_crit_dmg(0.15 * 2)
        attr.add_dmg_bonus(0.15 * 2)
        attr.add_crit_rate(0.2 * 2)
        attr.add_effect(title, msg)

        # 暴击高于100%时，每多出1%暴击，奥古斯塔暴击伤害提升2%，最高可提升100%暴击伤害
        crit_rate = attr.crit_rate
        if crit_rate > 1:
            crit_rate = crit_rate - 1
            crit_rate_bonus = min(max(crit_rate / 0.01, 0), 50)
            add_crit_dmg = crit_rate_bonus * 2 * 0.01
            title = f"{role_name}-二链"
            msg = f"爆伤提升{add_crit_dmg*100:.2f}%"
            attr.add_crit_dmg(add_crit_dmg, title, msg)

    elif chain_num >= 1:
        # 固有技能·炽盛决意会补充至上限，单人第一波能吃到。？
        title = f"{role_name}-一链-以众愿为冕"
        msg = "暴击伤害15%*2+导电伤害加成提升15%*2"
        attr.add_crit_dmg(0.15 * 2)
        attr.add_dmg_bonus(0.15 * 2)
        attr.add_effect(title, msg)
    else:
        title = "延奏技能-以众愿为冕"
        msg = "导电伤害加成提升15%"
        attr.add_dmg_bonus(0.15)
        attr.add_effect(title, msg)

    if chain_num >= 3:
        title = f"{role_name}-三链"
        msg = "伤害倍率提升25%"
        attr.add_skill_ratio(0.25, title, msg)

    if chain_num >= 4 and isGroup:
        title = f"{role_name}-四链"
        msg = "队伍中的角色的攻击提升20%"
        attr.add_atk_percent(0.2, title, msg)


def calc_damage_1(
    attr: DamageAttribute,
    role: RoleDetailData,
    isGroup: bool = False,
    isSingle: bool = True,
) -> Tuple[str, str]:
    # 设置角色固有技能
    role_breach = role.role.breach
    if role_breach and role_breach >= 3:
        # 设置触发护盾
        attr.set_trigger_shield()

    # 设置角色伤害类型
    attr.set_char_damage(hit_damage)
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
        char_result.skillTrees, SkillTreeMap[skill_type], "25", skillLevel
    )
    if isSingle:
        sm = skill_multi.split("+")
        s2 = calc_percent_expression(sm[-1])
        skill_multi = f"{s2*100:.2f}%"

    title = "共鸣技能·不败恒阳·落袭伤害"
    msg = f"技能倍率{skill_multi}"
    attr.add_skill_multi(skill_multi, title, msg)

    # 设置角色施放技能
    damage_func = [
        cast_attack,
        cast_skill,
        cast_hit,
        cast_liberation,
    ]
    phase_damage(attr, role, damage_func, isGroup)

    # 设置角色等级
    attr.set_character_level(role.role.level)

    # 设置角色技能施放是不是也有加成 eg：守岸人

    # 设置声骸属性
    attr.set_phantom_dmg_bonus()

    # 设置共鸣链
    chain_damage(attr, role, isGroup)

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
) -> Tuple[str, str]:
    # 设置角色固有技能
    role_breach = role.role.breach
    if role_breach and role_breach >= 3:
        # 设置触发护盾
        attr.set_trigger_shield()

    # 设置角色伤害类型
    attr.set_char_damage(hit_damage)
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
        char_result.skillTrees, SkillTreeMap[skill_type], "31", skillLevel
    )

    title = "赫日威临·烈阳伤害"
    msg = f"技能倍率{skill_multi}"
    attr.add_skill_multi(skill_multi, title, msg)

    # 设置角色施放技能
    damage_func = [
        cast_attack,
        cast_skill,
        cast_hit,
        cast_liberation,
    ]
    phase_damage(attr, role, damage_func, isGroup)

    # 设置角色等级
    attr.set_character_level(role.role.level)

    # 设置角色技能施放是不是也有加成 eg：守岸人

    # 设置声骸属性
    attr.set_phantom_dmg_bonus()

    # 设置共鸣链
    chain_damage(attr, role, isGroup)

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
    isSingle: bool = True,
) -> Tuple[str, str]:
    # 设置角色固有技能
    role_breach = role.role.breach
    if role_breach and role_breach >= 3:
        # 设置触发护盾
        attr.set_trigger_shield()

    # 设置角色伤害类型
    attr.set_char_damage(hit_damage)
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
        char_result.skillTrees, SkillTreeMap[skill_type], "32", skillLevel
    )

    if isSingle:
        title = "赫日威临·不朽者之肃"
        sm = skill_multi.split("+")
        s2 = calc_percent_expression(sm[1])
        skill_multi = f"{s2*100:.2f}%"
    else:
        title = "赫日威临·不朽者之肃总伤"

    msg = f"技能倍率{skill_multi}"
    attr.add_skill_multi(skill_multi, title, msg)

    # 设置角色施放技能
    damage_func = [
        cast_attack,
        cast_skill,
        cast_hit,
        cast_liberation,
    ]
    phase_damage(attr, role, damage_func, isGroup)

    # 设置角色等级
    attr.set_character_level(role.role.level)

    # 设置角色技能施放是不是也有加成 eg：守岸人

    # 设置声骸属性
    attr.set_phantom_dmg_bonus()

    # 设置共鸣链
    chain_damage(attr, role, isGroup)

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
        "title": "落袭尾刀",
        "func": lambda attr, role: calc_damage_1(attr, role),
    },
    {
        "title": "赫日威临·烈阳单段",
        "func": lambda attr, role: calc_damage_2(attr, role),
    },
    {
        "title": "赫日威临·不朽者之肃",
        "func": lambda attr, role: calc_damage_3(attr, role),
    },
    {
        "title": "赫日威临·不朽者之肃总伤",
        "func": lambda attr, role: calc_damage_3(attr, role, isSingle=False),
    },
]

rank = damage_detail[0]
