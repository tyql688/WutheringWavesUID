# 灯灯
from .damage import echo_damage, weapon_damage, phase_damage
from ...api.model import RoleDetailData
from ...ascension.char import WavesCharResult, get_char_detail2
from ...damage.damage import DamageAttribute
from ...damage.utils import (
    skill_damage_calc,
    SkillType,
    SkillTreeMap,
    cast_skill,
    cast_attack,
    cast_liberation,
    attack_damage,
    liberation_damage,
    cast_hit,
)


def calc_damage_1(
    attr: DamageAttribute, role: RoleDetailData, isGroup: bool = False
) -> (str, str):
    # 设置角色伤害类型
    attr.set_char_damage(attack_damage)
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
        char_result.skillTrees, SkillTreeMap[skill_type], "6", skillLevel
    )
    title = f"强化前扑伤害"
    msg = f"技能倍率{skill_multi}"
    attr.add_skill_multi(skill_multi, title, msg)

    # 设置角色施放技能
    damage_func = [cast_attack, cast_skill, cast_liberation, cast_hit]
    phase_damage(attr, role, damage_func, isGroup)

    # 设置角色等级
    attr.set_character_level(role.role.level)

    # 设置角色固有技能
    role_breach = role.role.breach
    if role_breach and role_breach >= 3:
        title = f"{role_name}-固有技能-寻路"
        msg = f"红灯模式期间，灯灯导电伤害加成提升10%。"
        attr.add_dmg_bonus(0.1, title, msg)

        title = f"{role_name}-固有技能-固伤"
        msg = f"施放强化前扑时，5秒内灯灯攻击力提升10%。"
        attr.add_atk_percent(0.1, title, msg)

    # 设置角色技能施放是不是也有加成 eg：守岸人

    # 设置声骸属性
    attr.set_phantom_dmg_bonus()

    # 设置共鸣链
    chain_num = role.get_chain_num()
    if chain_num >= 2:
        title = f"{role_name}-二链"
        msg = f"强化前扑攻击敌人时，无视对方20%的防御"
        attr.add_defense_reduction(0.2, title, msg)

    if chain_num >= 4:
        title = f"{role_name}-四链"
        msg = f"灯灯普攻伤害加成提升30%。"
        attr.add_dmg_bonus(0.3, title, msg)

    if chain_num >= 6:
        title = f"{role_name}-六链"
        msg = f"施放啾啾专送时，队伍中的角色的攻击提升20%"
        attr.add_atk_percent(0.2, title, msg)

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
) -> (str, str):
    # 设置角色伤害类型
    attr.set_char_damage(attack_damage)
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
        char_result.skillTrees, SkillTreeMap[skill_type], "7", skillLevel
    )
    title = f"强化后撤伤害"
    msg = f"技能倍率{skill_multi}"
    attr.add_skill_multi(skill_multi, title, msg)

    # 设置角色施放技能
    damage_func = [cast_attack, cast_skill, cast_liberation, cast_hit]
    phase_damage(attr, role, damage_func, isGroup)

    # 设置角色等级
    attr.set_character_level(role.role.level)

    # 设置角色固有技能
    role_breach = role.role.breach
    if role_breach and role_breach >= 3:
        title = f"{role_name}-固有技能-固伤"
        msg = f"施放强化后撤时，5秒内灯灯攻击力提升10%。"
        attr.add_atk_percent(0.1, title, msg)

    # 设置角色技能施放是不是也有加成 eg：守岸人

    # 设置声骸属性
    attr.set_phantom_dmg_bonus()

    # 设置共鸣链
    chain_num = role.get_chain_num()
    if chain_num >= 2:
        title = f"{role_name}-二链"
        msg = f"强化后撤攻击敌人时，无视对方20%的防御"
        attr.add_defense_reduction(0.2, title, msg)

    if chain_num >= 4:
        title = f"{role_name}-四链"
        msg = f"灯灯普攻伤害加成提升30%。"
        attr.add_dmg_bonus(0.3, title, msg)

    if chain_num >= 6:
        title = f"{role_name}-六链"
        msg = f"施放啾啾专送时，队伍中的角色的攻击提升20%"
        attr.add_atk_percent(0.2, title, msg)

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
) -> (str, str):
    # 设置角色伤害类型
    attr.set_char_damage(attack_damage)
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
    title = f"a1"
    msg = f"技能倍率{skill_multi}"
    attr.add_skill_multi(skill_multi, title, msg)

    skill_multi = skill_damage_calc(
        char_result.skillTrees, SkillTreeMap[skill_type], "3", skillLevel
    )
    title = f"a2"
    msg = f"技能倍率{skill_multi}"
    attr.add_skill_multi(skill_multi, title, msg)

    skill_multi = skill_damage_calc(
        char_result.skillTrees, SkillTreeMap[skill_type], "4", skillLevel
    )
    title = f"a3"
    msg = f"技能倍率{skill_multi}"
    attr.add_skill_multi(skill_multi, title, msg)

    # 设置角色施放技能
    damage_func = [cast_attack, cast_skill, cast_liberation, cast_hit]
    phase_damage(attr, role, damage_func, isGroup)

    # 设置角色等级
    attr.set_character_level(role.role.level)

    # 设置角色固有技能
    role_breach = role.role.breach
    if role_breach and role_breach >= 3:
        title = f"{role_name}-固有技能-寻路"
        msg = f"红灯模式期间，灯灯导电伤害加成提升10%。"
        attr.add_dmg_bonus(0.1, title, msg)

        title = f"{role_name}-固有技能-固伤"
        msg = f"施放强化前扑时，5秒内灯灯攻击力提升10%。"
        attr.add_atk_percent(0.1, title, msg)

    # 设置角色技能施放是不是也有加成 eg：守岸人

    # 设置声骸属性
    attr.set_phantom_dmg_bonus()

    # 设置共鸣链
    chain_num = role.get_chain_num()
    if chain_num >= 4:
        title = f"{role_name}-四链"
        msg = f"灯灯普攻伤害加成提升30%。"
        attr.add_dmg_bonus(0.3, title, msg)

    if chain_num >= 6:
        title = f"{role_name}-六链"
        msg = f"施放啾啾专送时，队伍中的角色的攻击提升20%"
        attr.add_atk_percent(0.2, title, msg)

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
) -> (str, str):
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
    title = f"啾啾专送"
    msg = f"技能倍率{skill_multi}"
    attr.add_skill_multi(skill_multi, title, msg)

    # 设置角色施放技能
    damage_func = [cast_attack, cast_skill, cast_liberation, cast_hit]
    phase_damage(attr, role, damage_func, isGroup)

    # 设置角色等级
    attr.set_character_level(role.role.level)

    # 设置角色固有技能
    role_breach = role.role.breach
    if role_breach and role_breach >= 3:
        title = f"{role_name}-固有技能-寻路"
        msg = f"红灯模式期间，灯灯导电伤害加成提升10%。"
        attr.add_dmg_bonus(0.1, title, msg)

        title = f"{role_name}-固有技能-固伤"
        msg = f"施放强化前扑时，5秒内灯灯攻击力提升10%。"
        attr.add_atk_percent(0.1, title, msg)

    # 设置角色技能施放是不是也有加成 eg：守岸人

    # 设置声骸属性
    attr.set_phantom_dmg_bonus()

    # 设置共鸣链
    chain_num = role.get_chain_num()
    if chain_num >= 3:
        title = f"{role_name}-三链"
        msg = f"啾啾专送造成的伤害提升30%。"
        attr.add_dmg_bonus(0.3, title, msg)

    if chain_num >= 6:
        title = f"{role_name}-六链"
        msg = f"施放啾啾专送时，队伍中的角色的攻击提升20%"
        attr.add_atk_percent(0.2, title, msg)

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
        "title": "强化前扑伤害",
        "func": lambda attr, role: calc_damage_1(attr, role),
    },
    {
        "title": "强化后撤伤害",
        "func": lambda attr, role: calc_damage_2(attr, role),
    },
    {
        "title": "红灯强化3a总伤",
        "func": lambda attr, role: calc_damage_3(attr, role),
    },
    {
        "title": "啾啾专送",
        "func": lambda attr, role: calc_damage_4(attr, role),
    },
]

rank = damage_detail[2]
