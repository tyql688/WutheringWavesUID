# 漂泊者·气动
from ...api.model import RoleDetailData
from ...damage.damage import DamageAttribute
from .damage import echo_damage, phase_damage, weapon_damage
from ...ascension.char import WavesCharResult, get_char_detail2
from ...damage.utils import (
    SkillType,
    SkillTreeMap,
    cast_skill,
    heal_bonus,
    cast_healing,
    skill_damage,
    cast_liberation,
    liberation_damage,
    skill_damage_calc,
)


def calc_damage_1(
    attr: DamageAttribute,
    role: RoleDetailData,
    isGroup: bool = False,
    type_num: int = 1,
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
        char_result.skillTrees, SkillTreeMap[skill_type], f"{type_num}", skillLevel
    )

    if type_num == 1:
        title = "抃风儛润第一段伤害"
    elif type_num == 2:
        title = "抃风儛润第二段伤害"

    msg = f"技能倍率{skill_multi}"
    attr.add_skill_multi(skill_multi, title, msg)

    # 设置角色施放技能
    damage_func = [cast_skill, cast_liberation, cast_healing]
    phase_damage(attr, role, damage_func, isGroup)

    # 设置角色等级
    attr.set_character_level(role.role.level)

    # 设置角色固有技能
    role_breach = role.role.breach
    if role_breach and role_breach >= 3:
        if isGroup:
            title = f"{role_name}-固有技能"
            msg = "变奏入场，攻击提升20%，"
            attr.add_atk_percent(0.2, title, msg)

    # 设置角色技能施放是不是也有加成 eg：守岸人

    # 设置声骸属性
    attr.set_phantom_dmg_bonus()

    # 设置共鸣链
    chain_num = role.get_chain_num()

    if chain_num >= 3:
        title = f"{role_name}-三链"
        msg = "气动伤害加成提升15%。"
        attr.add_dmg_bonus(0.15, title, msg)

    if chain_num >= 4:
        title = f"{role_name}-四链"
        msg = "施放抃风儛润时，共鸣技能伤害加成提升15%"
        attr.add_dmg_bonus(0.15, title, msg)

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
    type_num: int = 1,
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
    if type_num == 1:
        skill_multi = skill_damage_calc(
            char_result.skillTrees, SkillTreeMap[skill_type], "4", skillLevel
        )
    elif type_num == 2:
        skill_multi = skill_damage_calc(
            char_result.skillTrees, SkillTreeMap[skill_type], "5", skillLevel
        )
    if type_num == 1:
        title = "缥缈无相第一段伤害"
    elif type_num == 2:
        title = "缥缈无相第二段伤害"

    msg = f"技能倍率{skill_multi}"
    attr.add_skill_multi(skill_multi, title, msg)

    # 设置角色施放技能
    damage_func = [cast_skill, cast_liberation, cast_healing]
    phase_damage(attr, role, damage_func, isGroup)

    # 设置角色等级
    attr.set_character_level(role.role.level)

    # 设置角色固有技能
    role_breach = role.role.breach
    if role_breach and role_breach >= 3:
        if isGroup:
            title = f"{role_name}-固有技能"
            msg = "变奏入场，攻击提升20%，"
            attr.add_atk_percent(0.2, title, msg)

    # 设置角色技能施放是不是也有加成 eg：守岸人

    # 设置声骸属性
    attr.set_phantom_dmg_bonus()

    # 设置共鸣链
    chain_num = role.get_chain_num()

    if chain_num >= 3:
        title = f"{role_name}-三链"
        msg = "气动伤害加成提升15%。"
        attr.add_dmg_bonus(0.15, title, msg)

    if chain_num >= 6:
        title = f"{role_name}-六链"
        msg = "共鸣技能缥缈无相伤害倍率提升30%"
        attr.add_skill_ratio(0.3, title, msg)

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
    attr: DamageAttribute, role: RoleDetailData, isGroup: bool = False
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
    # 技能技能倍率
    skill_multi = skill_damage_calc(
        char_result.skillTrees, SkillTreeMap[skill_type], "1", skillLevel
    )
    title = "万象归墟-r伤害"
    msg = f"技能倍率{skill_multi}"
    attr.add_skill_multi(skill_multi, title, msg)

    # 设置角色施放技能
    damage_func = [cast_skill, cast_liberation, cast_healing]
    phase_damage(attr, role, damage_func, isGroup)

    # 设置角色等级
    attr.set_character_level(role.role.level)

    # 设置角色固有技能
    role_breach = role.role.breach
    if role_breach and role_breach >= 3:
        if isGroup:
            title = f"{role_name}-固有技能"
            msg = "变奏入场，攻击提升20%，"
            attr.add_atk_percent(0.2, title, msg)

    # 设置角色技能施放是不是也有加成 eg：守岸人

    # 设置声骸属性
    attr.set_phantom_dmg_bonus()

    # 设置共鸣链
    chain_num = role.get_chain_num()

    if chain_num >= 3:
        title = f"{role_name}-三链"
        msg = "气动伤害加成提升15%。"
        attr.add_dmg_bonus(0.15, title, msg)

    if chain_num >= 5:
        title = f"{role_name}-五链"
        msg = "共鸣解放万象归墟伤害倍率提升20%"
        attr.add_skill_ratio(0.2, title, msg)

    # 声骸
    echo_damage(attr, isGroup)

    # 武器
    weapon_damage(attr, role.weaponData, damage_func, isGroup)

    # 暴击伤害
    crit_damage = f"{attr.calculate_crit_damage():,.0f}"
    # 期望伤害
    expected_damage = f"{attr.calculate_expected_damage():,.0f}"
    return crit_damage, expected_damage


def calc_damage_4(
    attr: DamageAttribute, role: RoleDetailData, isGroup: bool = False
) -> tuple[str, str]:
    # 设置角色伤害类型
    attr.set_char_damage(heal_bonus)
    # 设置角色模板  "temp_atk", "temp_life", "temp_def"
    attr.set_char_template("temp_atk")

    role_name = role.role.roleName
    # 获取角色详情
    char_result: WavesCharResult = get_char_detail2(role)

    skill_type: SkillType = "共鸣解放"
    # 技能等级
    skillLevel = role.get_skill_level(skill_type)
    # 技能倍率
    skill_multi = skill_damage_calc(
        char_result.skillTrees, SkillTreeMap[skill_type], "2", skillLevel
    )
    title = "万象归墟-治疗量"
    msg = f"技能倍率{skill_multi}"
    attr.add_healing_skill_multi(skill_multi, title, msg)

    damage_func = [cast_skill, cast_liberation, cast_healing]

    # 设置角色等级
    attr.set_character_level(role.role.level)

    # 设置角色固有技能
    role_breach = role.role.breach
    if role_breach and role_breach >= 3:
        title = f"{role_name}-固有技能"
        msg = "共鸣解放万象归墟治疗量提升20%"
        attr.add_dmg_bonus(0.2, title, msg)

        if isGroup:
            title = f"{role_name}-固有技能"
            msg = "变奏入场，攻击提升20%，"
            attr.add_atk_percent(0.2, title, msg)

    attr.set_phantom_dmg_bonus(needShuxing=False)

    chain_num = role.get_chain_num()

    echo_damage(attr, isGroup)

    weapon_damage(attr, role.weaponData, damage_func, isGroup)

    healing_bonus = attr.calculate_healing(attr.effect_attack)

    crit_damage = f"{healing_bonus:,.0f}"
    return None, crit_damage


damage_detail = [
    {
        "title": "抃风儛润第一段伤害",
        "func": lambda attr, role: calc_damage_1(attr, role, type_num=1),
    },
    {
        "title": "抃风儛润第二段伤害",
        "func": lambda attr, role: calc_damage_1(attr, role, type_num=2),
    },
    {
        "title": "缥缈无相第一段伤害",
        "func": lambda attr, role: calc_damage_2(attr, role, type_num=1),
    },
    {
        "title": "缥缈无相第二段伤害",
        "func": lambda attr, role: calc_damage_2(attr, role, type_num=2),
    },
    {
        "title": "万象归墟-r伤害",
        "func": lambda attr, role: calc_damage_3(attr, role),
    },
    {
        "title": "万象归墟-治疗量",
        "func": lambda attr, role: calc_damage_4(attr, role),
    },
]

rank = damage_detail[3]
