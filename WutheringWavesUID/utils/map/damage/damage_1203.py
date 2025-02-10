# 安可
from .buff import shouanren_buff, guangzhu_buff
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
    skill_damage,
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

    skill_type: SkillType = "共鸣解放"
    # 获取角色技能等级
    skillLevel = role.get_skill_level(skill_type)
    # 技能技能倍率
    skill_multi = skill_damage_calc(
        char_result.skillTrees, SkillTreeMap[skill_type], "1", skillLevel
    )
    title = f"黑咩·胡闹第一段伤害"
    msg = f"技能倍率{skill_multi}"
    attr.add_skill_multi(skill_multi, title, msg)

    skill_multi = skill_damage_calc(
        char_result.skillTrees, SkillTreeMap[skill_type], "2", skillLevel
    )
    title = f"黑咩·胡闹第二段伤害"
    msg = f"技能倍率{skill_multi}"
    attr.add_skill_multi(skill_multi, title, msg)

    skill_multi = skill_damage_calc(
        char_result.skillTrees, SkillTreeMap[skill_type], "3", skillLevel
    )
    title = f"黑咩·胡闹第三段伤害"
    msg = f"技能倍率{skill_multi}"
    attr.add_skill_multi(skill_multi, title, msg)

    skill_multi = skill_damage_calc(
        char_result.skillTrees, SkillTreeMap[skill_type], "4", skillLevel
    )
    title = f"黑咩·胡闹第四段伤害"
    msg = f"技能倍率{skill_multi}"
    attr.add_skill_multi(skill_multi, title, msg)

    # 设置角色施放技能
    damage_func = [cast_skill, cast_liberation, cast_attack]
    phase_damage(attr, role, damage_func, isGroup)

    # 设置角色等级
    attr.set_character_level(role.role.level)

    # 设置角色固有技能
    role_breach = role.role.breach
    if role_breach and role_breach >= 3:
        title = f"{role_name}-固有技能-咩咩加油歌"
        msg = f"施放热力羊咩或黑咩·狂热时，安可的热熔伤害加成提升10%"
        attr.add_dmg_bonus(0.1, title, msg)

        title = f"{role_name}-固有技能-生气的黑咩"
        msg = f"黑咩大暴走期间，安可的生命高于70%时，伤害提升10%。"
        attr.add_dmg_bonus(0.1, title, msg)

    # 设置角色技能施放是不是也有加成 eg：守岸人

    # 设置声骸属性
    attr.set_phantom_dmg_bonus()

    # 设置共鸣链
    chain_num = role.get_chain_num()
    if chain_num >= 1:
        title = f"{role_name}-一链"
        msg = f"热熔伤害加成额外提升3%，可叠加4层"
        attr.add_dmg_bonus(0.12, title, msg)

    if chain_num >= 6:
        title = f"{role_name}-六链"
        msg = "黑咩大暴走期间，每次造成伤害叠加1层【迷失羔羊】，增加5%*5攻击"
        attr.add_atk_percent(0.25, title, msg)

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
    attr.set_char_damage(skill_damage)
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
        char_result.skillTrees, SkillTreeMap[skill_type], "6", skillLevel
    )
    title = f"黑咩·狂热"
    msg = f"技能倍率{skill_multi}"
    attr.add_skill_multi(skill_multi, title, msg)

    # 设置角色施放技能
    damage_func = [cast_skill, cast_liberation, cast_hit]
    phase_damage(attr, role, damage_func, isGroup)

    # 设置角色等级
    attr.set_character_level(role.role.level)

    # 设置角色固有技能
    role_breach = role.role.breach
    if role_breach and role_breach >= 3:
        title = f"{role_name}-固有技能-咩咩加油歌"
        msg = f"施放热力羊咩或黑咩·狂热时，安可的热熔伤害加成提升10%"
        attr.add_dmg_bonus(0.1, title, msg)

        title = f"{role_name}-固有技能-生气的黑咩"
        msg = f"黑咩大暴走期间，安可的生命高于70%时，伤害提升10%。"
        attr.add_dmg_bonus(0.1, title, msg)

    # 设置角色技能施放是不是也有加成 eg：守岸人

    # 设置声骸属性
    attr.set_phantom_dmg_bonus()

    # 设置共鸣链
    chain_num = role.get_chain_num()
    if chain_num >= 1:
        title = f"{role_name}-一链"
        msg = f"热熔伤害加成额外提升3%，可叠加4层"
        attr.add_dmg_bonus(0.12, title, msg)

    if chain_num >= 5:
        title = f"{role_name}-五链"
        msg = "共鸣技能伤害加成提升35%。"
        attr.add_dmg_bonus(0.35, title, msg)

    if chain_num >= 6:
        title = f"{role_name}-六链"
        msg = "黑咩大暴走期间，每次造成伤害叠加1层【迷失羔羊】，增加5%*5攻击"
        attr.add_atk_percent(0.25, title, msg)

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
) -> (str, str):
    attr.set_char_damage(attack_damage)
    attr.set_char_template("temp_atk")
    # 守岸人buff
    shouanren_buff(attr, 0, 1, isGroup)

    # 光主buff
    guangzhu_buff(attr, 6, 1, isGroup)

    return calc_damage_1(attr, role, isGroup)


damage_detail = [
    {
        "title": "黑咩·胡闹四段总伤",
        "func": lambda attr, role: calc_damage_1(attr, role),
    },
    {
        "title": "黑咩·狂热伤害",
        "func": lambda attr, role: calc_damage_2(attr, role),
    },
    # {
    #     "title": "0守/6光/黑咩·胡闹四段总伤",
    #     "func": lambda attr, role: calc_damage_10(attr, role),
    # },
]

rank = damage_detail[0]
