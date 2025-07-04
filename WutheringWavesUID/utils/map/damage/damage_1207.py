# 露帕
from typing import Literal

from ...api.model import RoleDetailData
from ...ascension.char import WavesCharResult, get_char_detail2
from ...damage.damage import DamageAttribute, calc_percent_expression
from ...damage.utils import (
    SkillTreeMap,
    SkillType,
    cast_attack,
    cast_hit,
    cast_liberation,
    cast_skill,
    liberation_damage,
    skill_damage_calc,
)
from .buff import changli_buff, shouanren_buff
from .damage import echo_damage, phase_damage, weapon_damage


def get_molten_num(
    attr: DamageAttribute,
):
    """
    获取热熔人数，队伍人数
    """
    fix_num = 1
    for char_id in attr.teammate_char_ids:
        if int(char_id) // 100 == 12:
            fix_num += 1
    return fix_num, len(attr.teammate_char_ids) + 1


def calc_damage_2(
    attr: DamageAttribute,
    role: RoleDetailData,
    isGroup: bool = False,
    skill_name: Literal["r1", "r2"] = "r1",
) -> tuple[str, str]:
    # 设置角色伤害类型
    attr.set_char_damage(liberation_damage)
    # 设置角色模板  "temp_atk", "temp_life", "temp_def"
    attr.set_char_template("temp_atk")

    role_name = role.role.roleName
    # 获取角色详情
    char_result: WavesCharResult = get_char_detail2(role)

    skill_type: SkillType = "共鸣解放"
    # 获取角色技能等级
    skillLevel = role.get_skill_level(skill_type)
    if skill_name == "r1":
        param_id = "1"
        title = "荣光欢酣于火"
    else:
        param_id = "2"
        title = "破敌"
    # 技能技能倍率
    skill_multi = skill_damage_calc(
        char_result.skillTrees, SkillTreeMap[skill_type], param_id, skillLevel
    )

    msg = f"技能倍率{skill_multi}"
    attr.add_skill_multi(skill_multi, title, msg)

    title = "燃旗-共鸣回路"
    msg = "攻击提升12%"
    attr.add_atk_percent(0.12, title, msg)

    molten_num, team_num = get_molten_num(attr)
    chain_num = role.get_chain_num()
    if skill_name == "r2":
        if isGroup:
            title = "追猎-共鸣解放"
            if molten_num >= 3 or chain_num >= 3:
                msg = "热熔提升(10+10)%"
                attr.add_dmg_bonus(0.2, title, msg)
            else:
                msg = "热熔提升10%"
                attr.add_dmg_bonus(0.1, title, msg)

            msg = f"攻击力提升(6*{team_num})%"
            attr.add_atk_percent(0.06 * molten_num, title, msg)
        else:
            title = "追猎-共鸣解放"
            if chain_num >= 3:
                msg = "热熔提升(10+10)%"
                attr.add_dmg_bonus(0.2, title, msg)

                msg = "攻击力提升6%"
                attr.add_atk_percent(0.06, title, msg)
            else:
                msg = "攻击力提升6%, 热熔提升10%"
                attr.add_effect(title, msg)
                attr.add_atk_percent(0.06)
                attr.add_dmg_bonus(0.1)

    # 设置角色施放技能
    damage_func = [cast_attack, cast_hit, cast_skill, cast_liberation]
    phase_damage(attr, role, damage_func, isGroup)

    # 设置角色等级
    attr.set_character_level(role.role.level)

    role_breach = role.role.breach
    if role_breach and role_breach >= 3:
        if chain_num >= 3:
            title = f"{role_name}-荣光效果-三链"
            msg = "角色攻击时无视15%热熔抗性"
            attr.add_enemy_resistance(-0.15, title, msg)
        else:
            # 共鸣解放·荣光
            # 施放共鸣解放荣光欢酣于火时，额外获得荣光效果，35秒内：
            # 队伍中的角色攻击时无视3%热熔抗性，并且队伍中每有一名除露帕外的热熔属性角色，无视热熔抗性效果增加3%，上限为9%，当队伍中的热熔属性角色达到3名时，无视热熔抗性的效果额外增加6%。
            title = f"{role_name}-荣光效果"
            msg = f"角色攻击时无视3*{molten_num}%热熔抗性"
            attr.add_enemy_resistance(-0.03 * molten_num, title, msg)

            if molten_num >= 3:
                msg = "角色攻击时无视6%热熔抗性"
                attr.add_enemy_resistance(-0.06, title, msg)

    # 设置角色技能施放是不是也有加成 eg：守岸人

    # 设置声骸属性
    attr.set_phantom_dmg_bonus()

    # 设置共鸣链
    if chain_num >= 1:
        title = f"{role_name}-一链"
        msg = "施放共鸣解放时，暴击提升20%"
        attr.add_crit_rate(0.2, title, msg)

    if chain_num >= 2:
        title = f"{role_name}-二链"
        msg = "施放共鸣解放,重击,空中攻击时，热熔伤害加成提升20%*2"
        attr.add_dmg_bonus(0.2 * 2, title, msg)

    if chain_num >= 5 and isGroup:
        title = f"{role_name}-五链"
        msg = "变奏入场时，共鸣解放伤害加成提升15%"
        attr.add_dmg_bonus(0.15, title, msg)

    if chain_num >= 6 and skill_name == "r1":
        title = f"{role_name}-六链"
        msg = "共鸣解放荣光欢酣于火,忽视目标30%防御"
        attr.add_defense_reduction(0.3, title, msg)

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
) -> tuple[str, str]:
    # 设置角色伤害类型
    attr.set_char_damage(liberation_damage)
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
        char_result.skillTrees, SkillTreeMap[skill_type], "2", skillLevel
    )

    if isSingle:
        sm = skill_multi.split("+")
        s2 = calc_percent_expression(sm[-1])
        skill_multi = f"{s2*100:.2f}%"

    title = "狼舞的决意·极"
    msg = f"技能倍率{skill_multi}"
    attr.add_skill_multi(skill_multi, title, msg)

    title = "燃旗-共鸣回路"
    msg = "攻击提升12%"
    attr.add_atk_percent(0.12, title, msg)

    molten_num, team_num = get_molten_num(attr)
    chain_num = role.get_chain_num()
    if isGroup:
        title = "追猎-共鸣解放"
        if molten_num >= 3 or chain_num >= 3:
            msg = "热熔提升(10+10)%"
            attr.add_dmg_bonus(0.2, title, msg)
        else:
            msg = "热熔提升10%"
            attr.add_dmg_bonus(0.1, title, msg)

        msg = f"攻击力提升(6*{team_num})%"
        attr.add_atk_percent(0.06 * molten_num, title, msg)
    else:
        title = "追猎-共鸣解放"
        if chain_num >= 3:
            msg = "热熔提升(10+10)%"
            attr.add_dmg_bonus(0.2, title, msg)

            msg = "攻击力提升6%"
            attr.add_atk_percent(0.06, title, msg)
        else:
            msg = "攻击力提升6%, 热熔提升10%"
            attr.add_effect(title, msg)
            attr.add_atk_percent(0.06)
            attr.add_dmg_bonus(0.1)

    # 设置角色施放技能
    damage_func = [cast_attack, cast_hit, cast_skill, cast_liberation]
    phase_damage(attr, role, damage_func, isGroup)

    # 设置角色等级
    attr.set_character_level(role.role.level)

    # 设置角色固有技能
    role_breach = role.role.breach
    if role_breach and role_breach >= 3:
        if chain_num >= 3:
            title = f"{role_name}-荣光效果-三链"
            msg = "角色攻击时无视15%热熔抗性"
            attr.add_enemy_resistance(-0.15, title, msg)
        else:
            # 共鸣解放·荣光
            # 施放共鸣解放荣光欢酣于火时，额外获得荣光效果，35秒内：
            # 队伍中的角色攻击时无视3%热熔抗性，并且队伍中每有一名除露帕外的热熔属性角色，无视热熔抗性效果增加3%，上限为9%，当队伍中的热熔属性角色达到3名时，无视热熔抗性的效果额外增加6%。
            title = f"{role_name}-荣光效果"
            msg = f"角色攻击时无视3*{molten_num}%热熔抗性"
            attr.add_enemy_resistance(-0.03 * molten_num, title, msg)

            if molten_num >= 3:
                msg = "角色攻击时无视6%热熔抗性"
                attr.add_enemy_resistance(-0.06, title, msg)

    # 设置角色技能施放是不是也有加成 eg：守岸人

    # 设置声骸属性
    attr.set_phantom_dmg_bonus()

    # 设置共鸣链
    if chain_num >= 1:
        title = f"{role_name}-一链"
        msg = "施放共鸣解放时，暴击提升20%"
        attr.add_crit_rate(0.2, title, msg)

    if chain_num >= 2:
        title = f"{role_name}-二链"
        msg = "施放共鸣解放,重击,空中攻击时，热熔伤害加成提升20%*2"
        attr.add_dmg_bonus(0.2 * 2, title, msg)

    if chain_num >= 4:
        title = f"{role_name}-四链"
        msg = "狼舞的决意·极的伤害倍率提升125%"
        attr.add_skill_ratio(1.25, title, msg)

    if chain_num >= 5 and isGroup:
        title = f"{role_name}-五链"
        msg = "变奏入场时，共鸣解放伤害加成提升15%"
        attr.add_dmg_bonus(0.15, title, msg)

    if chain_num >= 6:
        title = f"{role_name}-六链"
        msg = "狼舞的决意·极,忽视目标30%防御"
        attr.add_defense_reduction(0.3, title, msg)

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
) -> tuple[str, str]:
    attr.set_char_damage(liberation_damage)
    attr.set_char_template("temp_atk")
    # 守岸人buff
    shouanren_buff(attr, 0, 1, isGroup)

    # 长离buff
    changli_buff(attr, 0, 1, isGroup)

    return calc_damage_3(attr, role, isGroup)


damage_detail = [
    {
        "title": "荣光欢酣于火",
        "func": lambda attr, role: calc_damage_2(attr, role, skill_name="r1"),
    },
    {
        "title": "狼舞·极尾刀",
        "func": lambda attr, role: calc_damage_3(attr, role, isSingle=True),
    },
    {
        "title": "狼舞·极总伤",
        "func": lambda attr, role: calc_damage_3(attr, role, isSingle=False),
    },
]

rank = damage_detail[1]
