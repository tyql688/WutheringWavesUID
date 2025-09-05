# 尤诺


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
    liberation_damage,
    skill_damage_calc,
)
from .damage import echo_damage, phase_damage, weapon_damage


def calc_damage_1(
    attr: DamageAttribute, role: RoleDetailData, isGroup: bool = False
) -> tuple[str, str]:
    attr.set_trigger_shield()
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
        char_result.skillTrees, SkillTreeMap[skill_type], "8", skillLevel
    )
    title = "共鸣技能·越限的弦引"
    msg = f"技能倍率{skill_multi}"
    attr.add_skill_multi(skill_multi, title, msg)

    # 设置角色施放技能
    damage_func = [cast_attack, cast_skill, cast_hit, cast_liberation]
    phase_damage(attr, role, damage_func, isGroup)

    # 设置角色等级
    attr.set_character_level(role.role.level)

    # 设置角色固有技能
    role_breach = role.role.breach

    # 设置角色技能施放是不是也有加成 eg：守岸人

    # 10层苍白死光的祝颂
    title = "苍白死光的祝颂"
    msg = "角色全伤害加深4%*10"
    attr.add_dmg_deepen(0.04 * 10, title, msg)

    # 设置声骸属性
    attr.set_phantom_dmg_bonus()

    # 设置共鸣链
    chain_num = role.get_chain_num()
    if chain_num >= 1:
        title = f"{role_name}-一链"
        msg = "尤诺处于月相流转状态时，攻击提升40%"
        attr.add_atk_percent(0.4, title, msg)

    if chain_num >= 2:
        title = f"{role_name}-二链"
        msg = "苍白死光的祝颂叠加至10层时额外获得40%全伤害加深"
        attr.add_dmg_deepen(0.4, title, msg)

    if chain_num >= 3:
        title = f"{role_name}-三链"
        msg = "尤诺处于月相流转状态时，共鸣技能·越限的弦引造成的伤害加深65%"
        attr.add_dmg_deepen(0.65, title, msg)

    if chain_num >= 5:
        title = f"{role_name}-五链"
        msg = "共鸣解放伤害加成提升20%。"
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


def calc_damage_2(
    attr: DamageAttribute, role: RoleDetailData, isGroup: bool = False
) -> tuple[str, str]:
    attr.set_trigger_shield()
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
        char_result.skillTrees, SkillTreeMap[skill_type], "19", skillLevel
    )
    title = "重击·至臻的完满"
    msg = f"技能倍率{skill_multi}"
    attr.add_skill_multi(skill_multi, title, msg)

    # 设置角色施放技能
    damage_func = [cast_attack, cast_skill, cast_hit, cast_liberation]
    phase_damage(attr, role, damage_func, isGroup)

    # 设置角色等级
    attr.set_character_level(role.role.level)

    # 设置角色固有技能
    role_breach = role.role.breach

    # 设置角色技能施放是不是也有加成 eg：守岸人

    # 10层苍白死光的祝颂
    title = "苍白死光的祝颂"
    msg = "角色全伤害加深4%*10"
    attr.add_dmg_deepen(0.04 * 10, title, msg)

    # 设置声骸属性
    attr.set_phantom_dmg_bonus()

    # 设置共鸣链
    chain_num = role.get_chain_num()
    if chain_num >= 1:
        title = f"{role_name}-一链"
        msg = "尤诺处于月相流转状态时，攻击提升40%"
        attr.add_atk_percent(0.4, title, msg)

    if chain_num >= 2:
        title = f"{role_name}-二链"
        msg = "苍白死光的祝颂叠加至10层时额外获得40%全伤害加深"
        attr.add_dmg_deepen(0.4, title, msg)

    if chain_num >= 5:
        title = f"{role_name}-五链"
        msg = "共鸣解放伤害加成提升20%。"
        attr.add_dmg_bonus(0.2, title, msg)

    if chain_num >= 6:
        title = f"{role_name}-六链"
        msg = "重击·至臻的完满伤害倍率增加1600%"
        attr.add_skill_multi(16, title, msg)

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
        "title": "共鸣技能·越限的弦引",
        "func": lambda attr, role: calc_damage_1(attr, role),
    },
    {
        "title": "重击·至臻的完满",
        "func": lambda attr, role: calc_damage_2(attr, role),
    },
]

rank = damage_detail[0]
