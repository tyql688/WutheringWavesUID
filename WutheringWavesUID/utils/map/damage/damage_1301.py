# 卡卡罗
from typing import Literal

from ...api.model import RoleDetailData
from ...ascension.char import WavesCharResult, get_char_detail2
from ...damage.damage import DamageAttribute, calc_percent_expression
from ...damage.utils import (
    SkillTreeMap,
    SkillType,
    attack_damage,
    cast_attack,
    cast_hit,
    cast_liberation,
    cast_skill,
    liberation_damage,
    skill_damage,
    skill_damage_calc,
)
from .buff import shouanren_buff, yinlin_buff
from .damage import echo_damage, phase_damage, weapon_damage


def calc_damage_1(
    attr: DamageAttribute, role: RoleDetailData, isGroup: bool = False
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
    title = "死告"
    msg = f"技能倍率{skill_multi}"
    attr.add_skill_multi(skill_multi, title, msg)

    # 设置角色施放技能
    damage_func = [cast_skill, cast_attack, cast_hit, cast_liberation]
    phase_damage(attr, role, damage_func, isGroup)

    # 设置角色等级
    attr.set_character_level(role.role.level)

    # 设置角色固有技能
    role_breach = role.role.breach
    if role_breach and role_breach >= 3:
        title = f"{role_name}-固有技能-喋血觉悟"
        msg = "施放重击「仁慈」时，卡卡罗的共鸣解放伤害加成提升10%"
        attr.add_dmg_bonus(0.1, title, msg)

    # 设置角色技能施放是不是也有加成 eg：守岸人

    # 设置声骸属性
    attr.set_phantom_dmg_bonus()

    # 设置共鸣链
    chain_num = role.get_chain_num()
    if chain_num >= 3:
        title = f"{role_name}-三链"
        msg = "共鸣解放杀戮武装状态持续期间，导电伤害加成提升25%"
        attr.add_dmg_bonus(0.25, title, msg)

    if chain_num >= 4:
        title = f"{role_name}-四链"
        msg = "施放延奏技能掠影奇袭时，队伍中的角色导电伤害加成提升20%"
        attr.add_dmg_bonus(0.2, title, msg)

    if chain_num >= 6:
        title = f"{role_name}-六链"
        msg = "召唤2个猎杀影进行协同攻击，造成卡卡罗100.00%*2攻击的导电伤害"
        attr.add_skill_multi(2, title, msg)

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
    title = "幻影蚀刻伤害"
    msg = f"技能倍率{skill_multi}"
    attr.add_skill_multi(skill_multi, title, msg)

    # 设置角色施放技能
    damage_func = [cast_skill, cast_attack, cast_hit, cast_liberation]
    phase_damage(attr, role, damage_func, isGroup)

    # 设置角色等级
    attr.set_character_level(role.role.level)

    # 设置角色固有技能
    role_breach = role.role.breach
    if role_breach and role_breach >= 3:
        title = f"{role_name}-固有技能-喋血觉悟"
        msg = "施放重击「仁慈」时，卡卡罗的共鸣解放伤害加成提升10%"
        attr.add_dmg_bonus(0.1, title, msg)

    # 设置角色技能施放是不是也有加成 eg：守岸人

    # 设置声骸属性
    attr.set_phantom_dmg_bonus()

    # 设置共鸣链
    chain_num = role.get_chain_num()
    if chain_num >= 4:
        title = f"{role_name}-四链"
        msg = "施放延奏技能掠影奇袭时，队伍中的角色导电伤害加成提升20%"
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


def calc_damage_3(
    attr: DamageAttribute,
    role: RoleDetailData,
    isGroup: bool = False,
    skill_type_name: Literal[
        "猎犬剑技第一段", "猎犬剑技第二段", "猎犬剑技第三段"
    ] = "猎犬剑技第一段",
) -> tuple[str, str]:
    # 设置角色伤害类型
    attr.set_char_damage(attack_damage)
    # 设置角色模板  "temp_atk", "temp_life", "temp_def"
    attr.set_char_template("temp_atk")

    title = "备注"
    msg = "默认aa闪"

    attr.add_effect(title, msg)

    role_name = role.role.roleName
    # 获取角色详情
    char_result: WavesCharResult = get_char_detail2(role)

    skill_type: SkillType = "共鸣解放"
    # 获取角色技能等级
    skillLevel = role.get_skill_level(skill_type)
    # 技能技能倍率
    if skill_type_name == "猎犬剑技第一段":
        param = "3"
    elif skill_type_name == "猎犬剑技第二段":
        param = "4"
    elif skill_type_name == "猎犬剑技第三段":
        param = "5"
    skill_multi = skill_damage_calc(
        char_result.skillTrees, SkillTreeMap[skill_type], param, skillLevel
    )

    title = f"{skill_type_name}伤害"
    if skill_type_name == "猎犬剑技第二段":
        sm = skill_multi.split("+")
        skill_multi = calc_percent_expression(sm[1])
        msg = f"技能倍率{skill_multi*100:.2f}%"
    else:
        msg = f"技能倍率{skill_multi}"

    attr.add_skill_multi(skill_multi, title, msg)

    # 设置角色施放技能
    damage_func = [cast_skill, cast_hit, cast_liberation]
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
        msg = "共鸣解放杀戮武装状态持续期间，导电伤害加成提升25%"
        attr.add_dmg_bonus(0.25, title, msg)

    if chain_num >= 4:
        title = f"{role_name}-四链"
        msg = "施放延奏技能掠影奇袭时，队伍中的角色导电伤害加成提升20%"
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


def calc_damage_4(
    attr: DamageAttribute,
    role: RoleDetailData,
    isGroup: bool = False,
    skill_type_name: Literal[
        "灭杀指令第一段", "灭杀指令第二段", "灭杀指令第三段"
    ] = "灭杀指令第一段",
) -> tuple[str, str]:
    # 设置角色伤害类型
    attr.set_char_damage(skill_damage)
    # 设置角色模板  "temp_atk", "temp_life", "temp_def"
    attr.set_char_template("temp_atk")

    title = "备注"
    msg = "默认为施放共鸣解放的技能伤害，默认吃变奏，吃4链加成"
    attr.add_effect(title, msg)

    role_name = role.role.roleName
    # 获取角色详情
    char_result: WavesCharResult = get_char_detail2(role)

    skill_type: SkillType = "共鸣技能"
    # 获取角色技能等级
    skillLevel = role.get_skill_level(skill_type)
    # 技能技能倍率
    if skill_type_name == "灭杀指令第一段":
        param = "1"
    elif skill_type_name == "灭杀指令第二段":
        param = "2"
    elif skill_type_name == "灭杀指令第三段":
        param = "3"
    skill_multi = skill_damage_calc(
        char_result.skillTrees, SkillTreeMap[skill_type], param, skillLevel
    )
    title = f"{skill_type_name}伤害"
    msg = f"技能倍率{skill_multi}"
    attr.add_skill_multi(skill_multi, title, msg)

    # 设置角色施放技能
    damage_func = [cast_skill, cast_hit, cast_liberation]
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
    if chain_num >= 2:
        title = f"{role_name}-二链"
        msg = "施放变奏技能后，共鸣技能伤害加成提升30%，持续15秒。"
        attr.add_dmg_bonus(0.3, title, msg)

    if chain_num >= 3:
        title = f"{role_name}-三链"
        msg = "共鸣解放杀戮武装状态持续期间，导电伤害加成提升25%"
        attr.add_dmg_bonus(0.25, title, msg)

    if chain_num >= 4:
        title = f"{role_name}-四链"
        msg = "施放延奏技能掠影奇袭时，队伍中的角色导电伤害加成提升20%"
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


def calc_damage_10(
    attr: DamageAttribute, role: RoleDetailData, isGroup: bool = True
) -> tuple[str, str]:
    attr.set_char_damage(liberation_damage)
    attr.set_char_template("temp_atk")
    # 守岸人buff
    shouanren_buff(attr, 0, 1, isGroup)

    # 吟霖buff
    yinlin_buff(attr, 0, 1, isGroup)

    return calc_damage_1(attr, role, isGroup)


damage_detail = [
    {
        "title": "死告伤害",
        "func": lambda attr, role: calc_damage_1(attr, role),
    },
    {
        "title": "幻影蚀刻伤害",
        "func": lambda attr, role: calc_damage_2(attr, role),
    },
    {
        "title": "猎犬剑技第一段",
        "func": lambda attr, role: calc_damage_3(
            attr, role, skill_type_name="猎犬剑技第一段"
        ),
    },
    {
        "title": "猎犬剑技第二段",
        "func": lambda attr, role: calc_damage_3(
            attr, role, skill_type_name="猎犬剑技第二段"
        ),
    },
    {
        "title": "灭杀指令第一段",
        "func": lambda attr, role: calc_damage_4(
            attr, role, skill_type_name="灭杀指令第一段"
        ),
    },
    {
        "title": "灭杀指令第二段",
        "func": lambda attr, role: calc_damage_4(
            attr, role, skill_type_name="灭杀指令第二段"
        ),
    },
    {
        "title": "灭杀指令第三段",
        "func": lambda attr, role: calc_damage_4(
            attr, role, skill_type_name="灭杀指令第三段"
        ),
    },
    {
        "title": "0+1守/0+1吟霖/死告伤害",
        "func": lambda attr, role: calc_damage_10(attr, role),
    },
]

rank = damage_detail[0]
