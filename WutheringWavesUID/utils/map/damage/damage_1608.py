# 弗洛洛


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
    skill_damage,
    skill_damage_calc,
)
from .damage import echo_damage, phase_damage, weapon_damage


def calc_aftersound_num(role: RoleDetailData, isGroup: bool = False) -> int:
    """获取第二轮余响值"""
    chain_num = role.get_chain_num()

    if isGroup:
        aftersound_num = 10 + 2 * (4 + 1 + 2)
    else:
        aftersound_num = 10

    if chain_num >= 2:
        aftersound_num += 14 * 2
    if chain_num >= 6:
        aftersound_num = 124  # 2轮6链咋都满了

    return aftersound_num


def calc_aftersound_crit_dmg(aftersound_num: int):
    """计算余响提升暴击伤害"""
    aftersound_num = max(aftersound_num, 10)
    aftersound_num = min(aftersound_num, 124)

    if aftersound_num <= 24:
        crit_dmg = aftersound_num * 2.5
    else:
        crit_dmg = aftersound_num - 24 + 24 * 2.5

    return crit_dmg / 100


def calc_damage_1(
    attr: DamageAttribute,
    role: RoleDetailData,
    isGroup: bool = False,
    isSingle: bool = True,
) -> tuple[str, str]:
    # 设置角色伤害类型
    attr.set_char_damage(skill_damage)
    # 设置角色模板  "temp_atk", "temp_life", "temp_def"
    attr.set_char_template("temp_atk")

    role_name = role.role.roleName
    # 获取角色详情
    char_result: WavesCharResult = get_char_detail2(role)

    skill_type: SkillType = "常态攻击"
    # 获取角色技能等级
    skillLevel = role.get_skill_level(skill_type)
    # 技能技能倍率
    skill_multi = skill_damage_calc(
        char_result.skillTrees, SkillTreeMap[skill_type], "5", skillLevel
    )

    aftersound_percent = 1
    if isSingle:
        sm = skill_multi.split("+")
        s2 = calc_percent_expression(sm[-1])

        aftersound_percent = round(s2 / calc_percent_expression(skill_multi), 5)

        skill_multi = f"{s2*100:.2f}%"

    title = "谱曲终末"
    msg = f"技能倍率{skill_multi}"
    attr.add_skill_multi(skill_multi, title, msg)

    # 余响层数
    aftersound_num = calc_aftersound_num(role, isGroup)

    # 技能技能倍率
    aftersound_skill_multi = skill_damage_calc(
        char_result.skillTrees, SkillTreeMap[skill_type], "6", skillLevel
    )
    aftersound_num_multi = min(aftersound_num, 24)

    aftersound_skill_multi = (
        f"{aftersound_skill_multi}*{aftersound_num_multi}*{aftersound_percent}"
    )
    title = f"{role_name}-余响"
    msg = f"{aftersound_num_multi}层余响-余响倍率{aftersound_skill_multi}"
    attr.add_skill_multi(aftersound_skill_multi, title, msg)

    # 设置角色施放技能
    damage_func = [cast_attack, cast_skill, cast_hit, cast_liberation]
    phase_damage(attr, role, damage_func, isGroup)

    # 设置角色等级
    attr.set_character_level(role.role.level)

    # 设置角色固有技能
    role_breach = role.role.breach
    if role_breach and role_breach >= 3:
        crit_dmg = calc_aftersound_crit_dmg(aftersound_num)
        crit_dmg_str = f"{crit_dmg*100:.2f}%"
        title = f"{role_name}-固有技能-八重奏"
        msg = f"{aftersound_num}层余响-暴击伤害提升{crit_dmg_str}"
        attr.add_crit_dmg(crit_dmg, title, msg)

    # 设置角色技能施放是不是也有加成 eg：守岸人

    # 设置声骸属性
    attr.set_phantom_dmg_bonus()

    # 设置共鸣链
    chain_num = role.get_chain_num()
    if chain_num >= 2:
        title = f"{role_name}-二链"
        msg = "谱曲终末伤害倍率提升75%，余响对谱曲终末的倍率增加效果提升75%。"
        attr.add_skill_ratio(0.75, title, msg)

    if chain_num >= 4:
        title = f"{role_name}-四链"
        msg = "施放声骸技能时，队伍中的角色全属性伤害加成提升20%"
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
        "title": "2轮/谱曲终末尾刀",
        "func": lambda attr, role: calc_damage_1(attr, role),
    }
]

rank = damage_detail[0]
