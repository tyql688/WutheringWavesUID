# 千咲

from ...api.model import RoleDetailData
from ...ascension.char import WavesCharResult, get_char_detail
from ...damage.damage import DamageAttribute
from ...damage.utils import (
    SkillTreeMap,
    SkillType,
    cast_attack,
    cast_liberation,
    cast_skill,
    cast_variation,
    heal_bonus,
    liberation_damage,
    skill_damage_calc,
)
from .buff import shouanren_buff
from .damage import echo_damage, phase_damage, weapon_damage


def calc_damage_1(
    attr: DamageAttribute, role: RoleDetailData, isGroup: bool = False
) -> tuple[str, str]:
    """
    即刻·归无伤害
    """
    attr.set_char_damage(liberation_damage)
    attr.set_char_template("temp_atk")
    # 设置虚湮效应
    attr.set_env_havoc_bane()

    role_name = role.role.roleName
    role_id = role.role.roleId
    role_level = role.role.level
    role_breach = role.role.breach
    # 获取角色详情
    char_result: WavesCharResult = get_char_detail(role_id, role_level, role_breach)

    skill_type: SkillType = "共鸣解放"
    # 获取角色技能等级
    skillLevel = role.get_skill_level(skill_type)
    # 技能倍率 即刻·归无 1741.49%
    skill_multi = skill_damage_calc(
        char_result.skillTrees, SkillTreeMap[skill_type], "20", skillLevel
    )
    title = "即刻·归无伤害"
    msg = f"技能倍率{skill_multi}"
    attr.add_skill_multi(skill_multi, title, msg)

    # 设置角色施放技能
    damage_func = [cast_attack, cast_skill, cast_variation, cast_liberation]
    phase_damage(attr, role, damage_func, isGroup)

    # 设置角色等级
    attr.set_character_level(role_level)

    # 共鸣回路-虚湮之线：对拥有虚无绞痕的目标造成伤害时，可无视其18%防御
    title = "共鸣回路-虚湮之线"
    msg = "对拥有虚无绞痕的目标造成伤害时，可无视其18%防御"
    attr.add_defense_reduction(0.18, title, msg)

    # 设置角色固有技能
    if role_breach is not None and role_breach >= 3:
        title = "固有技能-终点在此处"
        msg = "施放共鸣解放后，虚湮伤害加成提升20%"
        attr.add_dmg_bonus(0.2, title, msg)

    # 设置声骸属性
    attr.set_phantom_dmg_bonus()

    # 设置共鸣链
    chain_num = role.get_chain_num()
    if chain_num >= 1:
        title = f"{role_name}-一链"
        msg = "千咲附加虚无绞痕时，自身攻击提升30%"
        attr.add_atk_percent(0.3, title, msg)

    if chain_num >= 2:
        title = f"{role_name}-二链"
        msg = "造成伤害无视目标10%湮灭伤害抗性"
        attr.add_resistance_ignore(0.1, title, msg)
        if isGroup:
            title = f"{role_name}-二链"
            msg = "队伍中的角色处于虚湮之线状态时，全属性伤害加成提升50%"
            attr.add_dmg_bonus(0.5, title, msg)

    # 三链：锯环系列技能倍率提升，不适用于即刻·归无
    # 四链：虚无绞痕机制变化，不影响伤害数值

    if chain_num >= 5:
        title = f"{role_name}-五链"
        msg = "共鸣解放即刻·归无的伤害加成提升100%"
        attr.add_dmg_bonus(1.0, title, msg)

    if chain_num >= 6:
        title = f"{role_name}-六链"
        msg = "拥有虚无绞痕·终焉的目标受到千咲伤害提升40%"
        attr.add_dmg_bonus(0.4, title, msg)

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
    """
    即刻·归无治疗量
    """
    attr.set_char_damage(heal_bonus)
    attr.set_char_template("temp_atk")

    role_name = role.role.roleName
    role_id = role.role.roleId
    role_level = role.role.level
    role_breach = role.role.breach
    # 获取角色详情
    char_result: WavesCharResult = get_char_detail(role_id, role_level, role_breach)

    skill_type: SkillType = "共鸣解放"
    # 获取角色技能等级
    skillLevel = role.get_skill_level(skill_type)
    # 治疗倍率 即刻·归无 214.61% + 4854
    skill_multi = skill_damage_calc(
        char_result.skillTrees, SkillTreeMap[skill_type], "21", skillLevel
    )
    title = "即刻·归无治疗量"
    msg = f"技能倍率{skill_multi}"
    attr.add_healing_skill_multi(skill_multi, title, msg)

    # 设置角色施放技能
    damage_func = [cast_attack, cast_skill, cast_variation, cast_liberation]

    # 设置角色等级
    attr.set_character_level(role_level)

    # 设置角色固有技能
    if role_breach is not None and role_breach >= 3:
        title = "固有技能-终点在此处"
        msg = "施放共鸣解放后，治疗效果加成提升20%"
        attr.add_dmg_bonus(0.2, title, msg)

    # 设置声骸属性
    attr.set_phantom_dmg_bonus(needShuxing=False)

    # 设置共鸣链
    chain_num = role.get_chain_num()
    if chain_num >= 1:
        title = f"{role_name}-一链"
        msg = "千咲附加虚无绞痕时，自身攻击提升30%"
        attr.add_atk_percent(0.3, title, msg)

    # 五链只提升伤害加成，不影响治疗量

    # 声骸
    echo_damage(attr, isGroup)

    # 武器
    weapon_damage(attr, role.weaponData, damage_func, isGroup)

    # 治疗量
    healing_bonus = attr.calculate_healing(attr.effect_attack)
    crit_damage = f"{healing_bonus:,.0f}"
    return None, crit_damage


def calc_damage_3(
    attr: DamageAttribute, role: RoleDetailData, isGroup: bool = False
) -> tuple[str, str]:
    """
    电锯模式长按总伤（锯环·疾攻第2段长按+第3段长按+锯环·终结）
    """
    attr.set_char_damage(liberation_damage)
    attr.set_char_template("temp_atk")
    # 设置虚湮效应
    attr.set_env_havoc_bane()

    role_name = role.role.roleName
    role_id = role.role.roleId
    role_level = role.role.level
    role_breach = role.role.breach
    # 获取角色详情
    char_result: WavesCharResult = get_char_detail(role_id, role_level, role_breach)

    skill_type: SkillType = "共鸣回路"
    # 获取角色技能等级
    skillLevel = role.get_skill_level(skill_type)

    # 锯环·疾攻第2段长按倍率 19.42%*10
    skill_multi_2 = skill_damage_calc(
        char_result.skillTrees, SkillTreeMap[skill_type], "28-2", skillLevel
    )
    # 锯环·疾攻第3段长按倍率 29.16%*6
    skill_multi_3 = skill_damage_calc(
        char_result.skillTrees, SkillTreeMap[skill_type], "29-2", skillLevel
    )
    # 锯环·终结基础倍率 94.05%+376.17%
    skill_multi_final = skill_damage_calc(
        char_result.skillTrees, SkillTreeMap[skill_type], "30", skillLevel
    )
    # 每点【锯环残响】增加倍率 4.72%
    skill_multi_per_echo = skill_damage_calc(
        char_result.skillTrees, SkillTreeMap[skill_type], "31", skillLevel
    )

    # 假设消耗100点【锯环残响】（满值），增加锯环·终结倍率
    echo_consumed = 100

    # 总技能倍率 = 第2段长按 + 第3段长按 + 锯环·终结（含残响加成）
    total_multi = skill_multi_2 + skill_multi_3 + skill_multi_final + (skill_multi_per_echo * echo_consumed)

    title = "电锯模式长按总伤"
    msg = f"技能倍率{total_multi}（第2段长按{skill_multi_2}+第3段长按{skill_multi_3}+锯环·终结{skill_multi_final}+残响加成{skill_multi_per_echo}*{echo_consumed}）"
    attr.add_skill_multi(total_multi, title, msg)

    # 设置角色施放技能
    damage_func = [cast_attack, cast_skill, cast_variation, cast_liberation]
    phase_damage(attr, role, damage_func, isGroup)

    # 设置角色等级
    attr.set_character_level(role_level)

    # 共鸣回路-虚湮之线：对拥有虚无绞痕的目标造成伤害时，可无视其18%防御
    title = "共鸣回路-虚湮之线"
    msg = "对拥有虚无绞痕的目标造成伤害时，可无视其18%防御"
    attr.add_defense_reduction(0.18, title, msg)

    # 设置角色固有技能
    if role_breach is not None and role_breach >= 3:
        title = "固有技能-终点在此处"
        msg = "施放共鸣解放后，虚湮伤害加成提升20%"
        attr.add_dmg_bonus(0.2, title, msg)

    # 设置声骸属性
    attr.set_phantom_dmg_bonus()

    # 设置共鸣链
    chain_num = role.get_chain_num()
    if chain_num >= 1:
        title = f"{role_name}-一链"
        msg = "千咲附加虚无绞痕时，自身攻击提升30%"
        attr.add_atk_percent(0.3, title, msg)

    if chain_num >= 2:
        title = f"{role_name}-二链"
        msg = "造成伤害无视目标10%湮灭伤害抗性"
        attr.add_resistance_ignore(0.1, title, msg)
        if isGroup:
            title = f"{role_name}-二链"
            msg = "队伍中的角色处于虚湮之线状态时，全属性伤害加成提升50%"
            attr.add_dmg_bonus(0.5, title, msg)

    if chain_num >= 3:
        title = f"{role_name}-三链"
        msg = "锯环·疾攻、锯环·终结的伤害倍率提升120%"
        attr.add_skill_ratio(1.2, title, msg)

        # 三链增加锯环·终结残响倍率增加效果
        title = f"{role_name}-三链"
        msg = f"消耗【锯环残响】提供的锯环·终结倍率增加效果提升120%（额外+{skill_multi_per_echo * echo_consumed * 1.2}）"
        attr.add_skill_multi(skill_multi_per_echo * echo_consumed * 1.2, title, msg)

    # 五链：不适用于锯环系列技能

    if chain_num >= 6:
        title = f"{role_name}-六链"
        msg = "拥有虚无绞痕·终焉的目标受到千咲伤害提升40%"
        attr.add_dmg_bonus(0.4, title, msg)

    # 万缕·汇终状态（施放共鸣解放后15秒内）
    title = "共鸣解放-万缕·汇终"
    msg = "锯环·疾攻、锯环·终结伤害倍率提升120%"
    attr.add_skill_ratio(1.2, title, msg)

    # 万缕·汇终增加锯环·终结残响倍率增加效果
    title = "共鸣解放-万缕·汇终"
    msg = f"消耗【锯环残响】提供的锯环·终结倍率增加效果提升120%（额外+{skill_multi_per_echo * echo_consumed * 1.2}）"
    attr.add_skill_multi(skill_multi_per_echo * echo_consumed * 1.2, title, msg)

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
    attr: DamageAttribute, role: RoleDetailData, isGroup: bool = True
) -> tuple[str, str]:
    """
    65守/即刻·归无伤害
    """
    attr.set_char_damage(liberation_damage)
    attr.set_char_template("temp_atk")
    # 守岸人buff
    shouanren_buff(attr, 6, 5, isGroup)

    return calc_damage_1(attr, role, isGroup)


damage_detail = [
    {
        "title": "即刻·归无伤害",
        "func": lambda attr, role: calc_damage_1(attr, role),
    },
    {
        "title": "即刻·归无治疗量",
        "func": lambda attr, role: calc_damage_2(attr, role),
    },
    {
        "title": "电锯模式长按总伤",
        "func": lambda attr, role: calc_damage_3(attr, role),
    },
    {
        "title": "65守/即刻·归无伤害",
        "func": lambda attr, role: calc_damage_4(attr, role),
    },
]

rank = damage_detail[0]
