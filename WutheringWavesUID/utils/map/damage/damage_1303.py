# 渊武

from .damage import echo_damage, weapon_damage, phase_damage
from ...api.model import RoleDetailData
from ...ascension.char import WavesCharResult, get_char_detail2
from ...damage.damage import DamageAttribute
from ...damage.utils import (
    skill_damage_calc,
    SkillType,
    SkillTreeMap,
    skill_damage,
    cast_skill,
    cast_attack,
    liberation_damage,
)


def calc_damage_1(
    attr: DamageAttribute, role: RoleDetailData, isGroup: bool = False
) -> (str, str):
    # 设置角色伤害类型
    attr.set_char_damage(skill_damage)
    # 设置角色模板  "temp_atk", "temp_life", "temp_def"
    attr.set_char_template("temp_def")

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
    title = f"雷之楔协同攻击"
    msg = f"技能倍率{skill_multi}"
    attr.add_skill_multi(skill_multi, title, msg)

    # 设置角色施放技能
    damage_func = [cast_attack, cast_skill]
    phase_damage(attr, role, damage_func, isGroup)

    # 设置角色等级
    attr.set_character_level(role.role.level)

    # 设置角色固有技能
    role_breach = role.role.breach

    # 设置角色技能施放是不是也有加成 eg：守岸人

    # 设置声骸属性
    attr.set_phantom_dmg_bonus()

    # 设置共鸣链
    chain_num = role.get_chain_num()
    if chain_num >= 3:
        title = f"{role_name}-三链"
        msg = f"雷之楔的协同攻击命中目标时，基于渊武20%防御额外提升伤害"
        attr.add_skill_multi(0.2, title, msg)

    if chain_num >= 6:
        title = f"{role_name}-六链"
        msg = f"处在雷之楔范围内的所有角色将持续获得效果：防御提升32%"
        attr.add_def_percent(0.32, title, msg)

    # 声骸
    echo_damage(attr, isGroup)

    # 武器
    weapon_damage(attr, role.weaponData, damage_func, isGroup)

    effect_value = attr.effect_def

    # 暴击伤害
    crit_damage = f"{attr.calculate_crit_damage(effect_value):,.0f}"
    # 期望伤害
    expected_damage = f"{attr.calculate_expected_damage(effect_value):,.0f}"
    return crit_damage, expected_damage


def calc_damage_2(
    attr: DamageAttribute, role: RoleDetailData, isGroup: bool = False
) -> (str, str):
    # 设置角色伤害类型
    attr.set_char_damage(liberation_damage)
    # 设置角色模板  "temp_atk", "temp_life", "temp_def"
    attr.set_char_template("temp_def")

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
    title = f"寂土重明"
    msg = f"技能倍率{skill_multi}"
    attr.add_skill_multi(skill_multi, title, msg)

    # 设置角色施放技能
    damage_func = [cast_attack, cast_skill]
    phase_damage(attr, role, damage_func, isGroup)

    # 设置角色等级
    attr.set_character_level(role.role.level)

    # 设置角色固有技能
    role_breach = role.role.breach

    # 设置角色技能施放是不是也有加成 eg：守岸人

    # 设置声骸属性
    attr.set_phantom_dmg_bonus()

    # 设置共鸣链
    chain_num = role.get_chain_num()

    if chain_num >= 6:
        title = f"{role_name}-六链"
        msg = f"共鸣技能雷之楔在场时，渊武的共鸣解放伤害加成提升50%"
        attr.add_dmg_bonus(0.5, title, msg)

    # 声骸
    echo_damage(attr, isGroup)

    # 武器
    weapon_damage(attr, role.weaponData, damage_func, isGroup)

    effect_value = attr.effect_def

    # 暴击伤害
    crit_damage = f"{attr.calculate_crit_damage(effect_value):,.0f}"
    # 期望伤害
    expected_damage = f"{attr.calculate_expected_damage(effect_value):,.0f}"
    return crit_damage, expected_damage


damage_detail = [
    {
        "title": "雷之楔协同攻击伤害",
        "func": lambda attr, role: calc_damage_1(attr, role),
    },
    {
        "title": "寂土重明伤害",
        "func": lambda attr, role: calc_damage_2(attr, role),
    },
]

rank = damage_detail[0]
