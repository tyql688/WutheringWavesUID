# 赞妮
from typing import Literal

from ...api.model import RoleDetailData
from .buff import feibi_buff, shouanren_buff
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
    skill_damage,
    cast_liberation,
    liberation_damage,
    skill_damage_calc,
)


def calc_damage_1(
    attr: DamageAttribute, role: RoleDetailData, isGroup: bool = False
) -> tuple[str, str]:
    attr.set_env_spectro_deepen()
    # 设置角色伤害类型
    attr.set_char_damage(skill_damage)
    # 设置角色模板  "temp_atk", "temp_life", "temp_def"
    attr.set_char_template("temp_atk")

    role_name = role.role.roleName
    # 获取角色详情
    char_result: WavesCharResult = get_char_detail2(role)

    skill_type: SkillType = "共鸣技能"
    # 获取角色技能等级
    skillLevel = role.get_skill_level(skill_type)
    # 技能技能倍率
    skill_multi = skill_damage_calc(
        char_result.skillTrees, SkillTreeMap[skill_type], "3", skillLevel
    )
    title = "集中压制伤害"
    msg = f"技能倍率{skill_multi}"
    attr.add_skill_multi(skill_multi, title, msg)

    # 设置角色施放技能
    damage_func = [cast_attack, cast_skill]
    phase_damage(attr, role, damage_func, isGroup)

    title = "斩棘"
    msg = f"自身直接造成的【光噪效应】伤害加深20%"
    attr.add_dmg_deepen(0.2, title, msg)

    # 设置角色等级
    attr.set_character_level(role.role.level)

    # 设置角色固有技能
    role_breach = role.role.breach
    if role_breach is not None and role_breach >= 3:
        if isGroup:
            title = "固有技能"
            msg = "施放变奏技能即刻执行时，衍射伤害加成提升12%"
            attr.add_dmg_bonus(0.12, title, msg)

    # 设置角色技能施放是不是也有加成 eg：守岸人

    # 设置声骸属性
    attr.set_phantom_dmg_bonus()

    # 设置共鸣链
    chain_num = role.get_chain_num()
    if chain_num >= 1:
        title = f"{role_name}-一链"
        msg = f"施放集中压制时，衍射伤害加成提升50%"
        attr.add_dmg_bonus(0.5, title, msg)

    if chain_num >= 2:
        title = f"{role_name}-二链"
        msg = f"集中压制倍率提升80%。"
        attr.add_skill_ratio(0.8, title, msg)
        msg = f"暴击提升20%。"
        attr.add_crit_rate(0.2, title, msg)

    if chain_num >= 4 and isGroup:
        title = f"{role_name}-四链"
        msg = f"施放变奏技能时，队伍中的角色攻击提升20%"
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
) -> tuple[str, str]:
    attr.set_env_spectro_deepen()
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
        char_result.skillTrees, SkillTreeMap[skill_type], "3", skillLevel
    )
    title = "终夜伤害"
    msg = f"技能倍率{skill_multi}"
    attr.add_skill_multi(skill_multi, title, msg)

    # 每点【焰光】增加倍率
    yanguang_multi = skill_damage_calc(
        char_result.skillTrees, SkillTreeMap[skill_type], "4", skillLevel
    )
    title = "【焰光】增加倍率*40层"
    msg = f"{yanguang_multi}*40"
    attr.add_effect(title, msg)

    title = "斩棘"
    msg = f"自身直接造成的【光噪效应】伤害加深20%"
    attr.add_dmg_deepen(0.2, title, msg)

    # 设置角色施放技能
    damage_func = [cast_attack, cast_skill, cast_liberation, cast_hit]
    phase_damage(attr, role, damage_func, isGroup)

    # 设置角色等级
    attr.set_character_level(role.role.level)

    # 设置角色固有技能
    role_breach = role.role.breach
    if role_breach is not None and role_breach >= 3:
        if isGroup:
            title = "固有技能"
            msg = "施放变奏技能即刻执行时，衍射伤害加成提升12%"
            attr.add_dmg_bonus(0.12, title, msg)

    # 设置角色技能施放是不是也有加成 eg：守岸人
    # 施放解放

    # 设置声骸属性
    attr.set_phantom_dmg_bonus()

    # 设置共鸣链
    chain_num = role.get_chain_num()
    if chain_num >= 1:
        title = f"{role_name}-一链"
        msg = f"施放集中压制时，衍射伤害加成提升50%"
        attr.add_dmg_bonus(0.5, title, msg)

    if chain_num >= 2:
        title = f"{role_name}-二链"
        msg = f"暴击提升20%。"
        attr.add_crit_rate(0.2, title, msg)

    if chain_num >= 4 and isGroup:
        title = f"{role_name}-四链"
        msg = f"施放变奏技能时，队伍中的角色攻击提升20%"
        attr.add_atk_percent(0.2, title, msg)

    if chain_num >= 6:
        title = f"{role_name}-六链"
        msg = f"【焰光】额外增加倍率提升40%"
        attr.add_skill_multi(f"{yanguang_multi}*1.4*40", title, msg)
        msg = "终夜倍率提升40%"
        attr.add_skill_ratio(0.4, title, msg)
    else:
        attr.add_skill_multi(f"{yanguang_multi}*40")

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
    other_type: Literal["破晓", "将明", "闪裂"] = "破晓",
) -> tuple[str, str]:
    attr.set_env_spectro_deepen()
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
    if other_type == "破晓":
        skillParamId = "1"
    elif other_type == "将明":
        skillParamId = "2"
    elif other_type == "闪裂":
        skillParamId = "5"
    skill_multi = skill_damage_calc(
        char_result.skillTrees, SkillTreeMap[skill_type], skillParamId, skillLevel
    )
    title = f"{other_type}伤害"
    msg = f"技能倍率{skill_multi}"
    attr.add_skill_multi(skill_multi, title, msg)

    title = "斩棘"
    msg = f"自身直接造成的【光噪效应】伤害加深20%"
    attr.add_dmg_deepen(0.2, title, msg)

    # 设置角色施放技能
    damage_func = [cast_attack, cast_skill, cast_liberation]
    phase_damage(attr, role, damage_func, isGroup)

    # 设置角色等级
    attr.set_character_level(role.role.level)

    # 设置角色固有技能
    role_breach = role.role.breach
    if role_breach is not None and role_breach >= 3:
        if isGroup:
            title = "固有技能"
            msg = "施放变奏技能即刻执行时，衍射伤害加成提升12%"
            attr.add_dmg_bonus(0.12, title, msg)

    # 设置角色技能施放是不是也有加成 eg：守岸人

    # 设置声骸属性
    attr.set_phantom_dmg_bonus()

    # 设置共鸣链
    chain_num = role.get_chain_num()
    if chain_num >= 1:
        title = f"{role_name}-一链"
        msg = f"施放集中压制时，衍射伤害加成提升50%"
        attr.add_dmg_bonus(0.5, title, msg)

    if chain_num >= 2:
        title = f"{role_name}-二链"
        msg = f"暴击提升20%。"
        attr.add_crit_rate(0.2, title, msg)

    if chain_num >= 4 and isGroup:
        title = f"{role_name}-四链"
        msg = f"施放变奏技能时，队伍中的角色攻击提升20%"
        attr.add_atk_percent(0.2, title, msg)

    if chain_num >= 6:
        title = f"{role_name}-六链"
        msg = f"{other_type}倍率提升40%"
        attr.add_skill_ratio(0.4, title, msg)

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
    title = "重燃伤害"
    msg = f"技能倍率{skill_multi}"
    attr.add_skill_multi(skill_multi, title, msg)

    # 设置角色施放技能
    damage_func = [cast_attack, cast_skill, cast_liberation]
    phase_damage(attr, role, damage_func, isGroup)

    # 设置角色等级
    attr.set_character_level(role.role.level)

    # 设置角色固有技能
    role_breach = role.role.breach
    if role_breach is not None and role_breach >= 3:
        if isGroup:
            title = "固有技能"
            msg = "施放变奏技能即刻执行时，衍射伤害加成提升12%"
            attr.add_dmg_bonus(0.12, title, msg)

    # 设置角色技能施放是不是也有加成 eg：守岸人

    # 设置声骸属性
    attr.set_phantom_dmg_bonus()

    # 设置共鸣链
    chain_num = role.get_chain_num()
    if chain_num >= 1:
        title = f"{role_name}-一链"
        msg = f"施放集中压制时，衍射伤害加成提升50%"
        attr.add_dmg_bonus(0.5, title, msg)

    if chain_num >= 2:
        title = f"{role_name}-二链"
        msg = f"暴击提升20%。"
        attr.add_crit_rate(0.2, title, msg)

    if chain_num >= 4 and isGroup:
        title = f"{role_name}-四链"
        msg = f"施放变奏技能时，队伍中的角色攻击提升20%"
        attr.add_atk_percent(0.2, title, msg)

    if chain_num >= 5:
        title = f"{role_name}-五链"
        msg = f"重燃倍率提升120%。"
        attr.add_skill_ratio(1.2, title, msg)

    # 声骸
    echo_damage(attr, isGroup)

    # 武器
    weapon_damage(attr, role.weaponData, damage_func, isGroup)

    # 暴击伤害
    crit_damage = f"{attr.calculate_crit_damage():,.0f}"
    # 期望伤害
    expected_damage = f"{attr.calculate_expected_damage():,.0f}"
    return crit_damage, expected_damage


def calc_damage_5(
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
        char_result.skillTrees, SkillTreeMap[skill_type], "2", skillLevel
    )
    sm = skill_multi.split("+")
    skill_multi = calc_percent_expression(sm[1])
    title = "终绝将至之刻2段伤害"
    msg = f"技能倍率{skill_multi*100:.2f}%"
    attr.add_skill_multi(skill_multi, title, msg)

    # 设置角色施放技能
    damage_func = [cast_attack, cast_skill, cast_liberation]
    phase_damage(attr, role, damage_func, isGroup)

    # 设置角色等级
    attr.set_character_level(role.role.level)

    # 设置角色固有技能
    role_breach = role.role.breach
    if role_breach is not None and role_breach >= 3:
        if isGroup:
            title = "固有技能"
            msg = "施放变奏技能即刻执行时，衍射伤害加成提升12%"
            attr.add_dmg_bonus(0.12, title, msg)

    # 设置角色技能施放是不是也有加成 eg：守岸人

    # 设置声骸属性
    attr.set_phantom_dmg_bonus()

    # 设置共鸣链
    chain_num = role.get_chain_num()
    if chain_num >= 1:
        title = f"{role_name}-一链"
        msg = f"施放集中压制时，衍射伤害加成提升50%"
        attr.add_dmg_bonus(0.5, title, msg)

    if chain_num >= 2:
        title = f"{role_name}-二链"
        msg = f"暴击提升20%。"
        attr.add_crit_rate(0.2, title, msg)

    if chain_num >= 3:
        title = f"{role_name}-三链"
        msg = f"消耗150层【焰光】，终绝将至之刻2段的倍率增加1200%。"
        attr.add_skill_multi(12, title, msg)

    if chain_num >= 4 and isGroup:
        title = f"{role_name}-四链"
        msg = f"施放变奏技能时，队伍中的角色攻击提升20%"
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


def calc_damage_10(
    attr: DamageAttribute, role: RoleDetailData, isGroup: bool = True
) -> tuple[str, str]:
    attr.set_env_spectro_deepen()
    attr.set_char_damage(hit_damage)
    attr.set_char_template("temp_atk")

    # 菲比buff
    feibi_buff(attr, 0, 1, isGroup)

    return calc_damage_2(attr, role, isGroup)


def calc_damage_11(
    attr: DamageAttribute, role: RoleDetailData, isGroup: bool = True
) -> tuple[str, str]:
    attr.set_env_spectro_deepen()
    attr.set_char_damage(hit_damage)
    attr.set_char_template("temp_atk")
    # 守岸人buff
    shouanren_buff(attr, 0, 1, isGroup)

    # 菲比buff
    feibi_buff(attr, 0, 1, isGroup)

    return calc_damage_2(attr, role, isGroup)


def calc_damage_12(
    attr: DamageAttribute, role: RoleDetailData, isGroup: bool = True
) -> tuple[str, str]:
    attr.set_env_spectro_deepen()
    attr.set_char_damage(hit_damage)
    attr.set_char_template("temp_atk")
    # 守岸人buff
    shouanren_buff(attr, 6, 5, isGroup)

    # 菲比buff
    feibi_buff(attr, 6, 5, isGroup)

    return calc_damage_2(attr, role, isGroup)


damage_detail = [
    {
        "title": "集中压制伤害",
        "func": lambda attr, role: calc_damage_1(attr, role),
    },
    {
        "title": "终夜伤害",
        "func": lambda attr, role: calc_damage_2(attr, role),
    },
    {
        "title": "重燃伤害",
        "func": lambda attr, role: calc_damage_4(attr, role),
    },
    {
        "title": "终绝将至之刻2段伤害",
        "func": lambda attr, role: calc_damage_5(attr, role),
    },
    {
        "title": "01菲比/终夜伤害",
        "func": lambda attr, role: calc_damage_10(attr, role),
    },
    {
        "title": "01守/01菲比/终夜伤害",
        "func": lambda attr, role: calc_damage_11(attr, role),
    },
    {
        "title": "65守/65菲比/终夜伤害",
        "func": lambda attr, role: calc_damage_12(attr, role),
    },
]

rank = damage_detail[4]
