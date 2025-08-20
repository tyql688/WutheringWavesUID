# 长离
import copy

from ...api.model import RoleDetailData
from ...ascension.char import WavesCharResult, get_char_detail2
from ...damage.damage import DamageAttribute
from ...damage.utils import (
    SkillTreeMap,
    SkillType,
    add_comma_separated_numbers,
    cast_attack,
    cast_liberation,
    cast_skill,
    hit_damage,
    liberation_damage,
    skill_damage,
    skill_damage_calc,
)
from .buff import bulante_buff, shouanren_buff, lupa_buff
from .damage import echo_damage, phase_damage, weapon_damage


def calc_chain(attr: DamageAttribute, role: RoleDetailData, isGroup: bool = False):
    role_name = role.role.roleName
    chain_num = role.get_chain_num()
    if chain_num >= 1 and attr.char_damage in [skill_damage, hit_damage]:
        # 1命
        title = f"{role_name}-一链"
        msg = "施放共鸣技能赫羽三相或重击焚身以火, 伤害提升10%"
        attr.add_dmg_bonus(0.1, title, msg)

    if chain_num >= 2:
        # 2命
        title = f"{role_name}-二链"
        msg = "获得【离火】时，长离的暴击提升25%"
        attr.add_crit_rate(0.25, title, msg)

    if chain_num >= 3 and attr.char_damage in [liberation_damage]:
        # 3命
        title = f"{role_name}-三链"
        msg = "共鸣解放离火照丹心造成的伤害提升80%。"
        attr.add_dmg_bonus(0.8, title, msg)

    if chain_num >= 4 and isGroup:
        # 4命 变奏入场
        title = f"{role_name}-四链"
        msg = "施放变奏技能后，队伍中的角色攻击提升20%"
        attr.add_atk_percent(0.2, title, msg)

    if chain_num >= 5 and attr.char_damage in [skill_damage]:
        # 5命
        title = f"{role_name}-五链"
        msg = "重击焚身以火倍率提升50%，造成的伤害提升50%。"
        attr.add_skill_ratio(0.5)
        attr.add_dmg_bonus(0.5)
        attr.add_effect(title, msg)

    if chain_num >= 6:
        # 6命
        title = f"{role_name}-六链"
        msg = "忽视目标40%防御"
        attr.add_defense_reduction(0.4, title, msg)


def calc_damage_0(
    attr: DamageAttribute,
    role: RoleDetailData,
    isGroup: bool = False,
    is_lianzhao: bool = False,
) -> tuple[str, str]:
    """
    焚身以火
    """
    attr.set_char_damage(skill_damage)
    attr.set_char_template("temp_atk")

    # 获取角色详情
    role_name = role.role.roleName
    char_result: WavesCharResult = get_char_detail2(role)

    skill_type: SkillType = "共鸣回路"
    # 获取角色技能等级
    skillLevel = role.get_skill_level(skill_type)
    # 技能技能倍率
    skill_multi = skill_damage_calc(
        char_result.skillTrees, SkillTreeMap[skill_type], "1", skillLevel
    )

    title = "焚身以火"
    msg = f"技能倍率{skill_multi}"
    attr.add_skill_multi(skill_multi, title, msg)

    # 设置角色等级
    attr.set_character_level(role.role.level)

    if is_lianzhao:
        damage_func = [cast_skill, cast_attack, cast_liberation]
    else:
        damage_func = [cast_skill, cast_attack]
    phase_damage(attr, role, damage_func, isGroup)

    role_breach = role.role.breach
    if role_breach and role_breach >= 3:
        # 固2(散势) 0.2
        title = f"{role_name}-固有技能-散势"
        msg = "长离的热熔伤害加成提升20%，攻击造成伤害时忽视目标15%防御"
        attr.add_dmg_bonus(0.2)
        attr.add_defense_reduction(0.15)
        attr.add_effect(title, msg)

    attr.set_phantom_dmg_bonus()

    if is_lianzhao:
        # 连招计算
        title = f"{role_name}-焰羽"
        msg = "10秒内施放重击焚身以火时攻击提升25%"
        attr.add_atk_percent(0.25, title, msg)

    # 命座计算
    calc_chain(attr, role, isGroup)
    # 声骸计算
    echo_damage(attr, isGroup)
    # 武器计算
    weapon_damage(attr, role.weaponData, damage_func, isGroup)

    # 暴击伤害
    crit_damage = f"{attr.calculate_crit_damage():,.0f}"
    # 期望伤害
    expected_damage = f"{attr.calculate_expected_damage():,.0f}"
    return crit_damage, expected_damage


def calc_damage_1(
    attr: DamageAttribute, role: RoleDetailData, isGroup: bool = False
) -> tuple[str, str]:
    """
    离火照丹心
    """
    attr.set_char_damage(liberation_damage)
    attr.set_char_template("temp_atk")

    # 获取角色详情
    role_name = role.role.roleName
    char_result: WavesCharResult = get_char_detail2(role)

    # 离火照丹心 技能倍率
    skill_type: SkillType = "共鸣解放"
    # 获取角色技能等级
    skillLevel = role.get_skill_level(skill_type)
    # 技能技能倍率
    skill_multi = skill_damage_calc(
        char_result.skillTrees, SkillTreeMap[skill_type], "1", skillLevel
    )

    title = "离火照丹心"
    msg = f"技能倍率{skill_multi}"
    attr.add_skill_multi(skill_multi, title, msg)

    damage_func = [cast_attack, cast_skill, cast_liberation]
    phase_damage(attr, role, damage_func, isGroup)

    # 设置角色等级
    attr.set_character_level(role.role.level)

    role_breach = role.role.breach
    if role_breach and role_breach >= 3:
        # 固2(散势) 0.2
        title = f"{role_name}-固有技能-散势"
        msg = "长离的热熔伤害加成提升20%，攻击造成伤害时忽视目标15%防御"
        attr.add_dmg_bonus(0.2)
        attr.add_defense_reduction(0.15)
        attr.add_effect(title, msg)

    attr.set_phantom_dmg_bonus()

    # 命座计算
    calc_chain(attr, role, isGroup)
    # 声骸计算
    echo_damage(attr, isGroup)
    # 武器计算
    weapon_damage(attr, role.weaponData, damage_func, isGroup)

    # 暴击伤害
    crit_damage = f"{attr.calculate_crit_damage():,.0f}"
    # 期望伤害
    expected_damage = f"{attr.calculate_expected_damage():,.0f}"
    return crit_damage, expected_damage


def calc_damage_2(
    attr: DamageAttribute, role: RoleDetailData, isGroup: bool = False
) -> tuple[str, str]:
    attr1 = copy.deepcopy(attr)
    crit_damage1, expected_damage1 = calc_damage_0(attr1, role, isGroup)
    attr1.add_effect("焚身以火暴击伤害", f"{crit_damage1}")
    attr1.add_effect("焚身以火期望伤害", f"{expected_damage1}")

    attr2 = copy.deepcopy(attr)
    crit_damage2, expected_damage2 = calc_damage_1(attr2, role, isGroup)
    attr2.add_effect("离火照丹心暴击伤害", f"{crit_damage2}")
    attr2.add_effect("离火照丹心期望伤害", f"{expected_damage2}")

    attr3 = copy.deepcopy(attr)
    crit_damage3, expected_damage3 = calc_damage_0(attr3, role, isGroup, True)
    attr3.add_effect("焚身以火暴击伤害", f"{crit_damage3}")
    attr3.add_effect("焚身以火期望伤害", f"{expected_damage3}")

    crit_damage = add_comma_separated_numbers(crit_damage1, crit_damage2, crit_damage3)
    expected_damage = add_comma_separated_numbers(
        expected_damage1, expected_damage2, expected_damage3
    )

    attr.add_effect(" ", " ")
    attr.effect.extend(attr1.effect[2:])
    attr.add_effect(" ", " ")
    attr.effect.extend(attr2.effect[2:])
    attr.add_effect(" ", " ")
    attr.effect.extend(attr3.effect[2:])
    return crit_damage, expected_damage


def calc_damage_10(
    attr: DamageAttribute, role: RoleDetailData, isGroup: bool = True
) -> tuple[str, str]:
    attr.set_char_damage(liberation_damage)
    attr.set_char_template("temp_atk")

    # 守岸人buff
    shouanren_buff(attr, 0, 1, isGroup)

    # 船长buff
    bulante_buff(attr, 0, 1, isGroup)

    return calc_damage_1(attr, role, isGroup)


def calc_damage_11(
    attr: DamageAttribute, role: RoleDetailData, isGroup: bool = True
) -> tuple[str, str]:
    attr.set_char_damage(liberation_damage)
    attr.set_char_template("temp_atk")

    # 守岸人buff
    shouanren_buff(attr, 6, 5, isGroup)

    # 船长buff
    bulante_buff(attr, 0, 1, isGroup)

    return calc_damage_1(attr, role, isGroup)


def calc_damage_12(
    attr: DamageAttribute, role: RoleDetailData, isGroup: bool = True
) -> tuple[str, str]:
    attr.set_char_damage(skill_damage)
    attr.set_char_template("temp_atk")

    # 守岸人buff
    shouanren_buff(attr, 0, 1, isGroup)

    # 船长buff
    bulante_buff(attr, 0, 1, isGroup)

    return calc_damage_0(attr, role, isGroup)


def calc_damage_13(
    attr: DamageAttribute, role: RoleDetailData, isGroup: bool = True
) -> tuple[str, str]:
    attr.set_char_damage(skill_damage)
    attr.set_char_template("temp_atk")

    # 守岸人buff
    shouanren_buff(attr, 6, 5, isGroup)

    # 船长buff
    bulante_buff(attr, 0, 1, isGroup)

    return calc_damage_0(attr, role, isGroup)


def calc_damage_14(
    attr: DamageAttribute, role: RoleDetailData, isGroup: bool = True
) -> tuple[str, str]:
    attr.set_char_damage(skill_damage)
    attr.set_char_template("temp_atk")

    # 守岸人buff
    shouanren_buff(attr, 0, 1, isGroup)

    # 露帕buff
    lupa_buff(attr, 0, 1, isGroup)

    # 露帕解放火队人数buff
    title = "露帕-追猎-共鸣解放"
    msg = "热熔提升10%"
    attr.add_dmg_bonus(0.1, title, msg)

    return calc_damage_0(attr, role, isGroup)


def calc_damage_15(
    attr: DamageAttribute, role: RoleDetailData, isGroup: bool = True
) -> tuple[str, str]:
    attr.set_char_damage(liberation_damage)
    attr.set_char_template("temp_atk")

    # 守岸人buff
    shouanren_buff(attr, 0, 1, isGroup)

    # 露帕buff
    lupa_buff(attr, 6, 5, isGroup)

    # 露帕解放火队人数buff
    title = "露帕-追猎-共鸣解放"
    msg = "热熔提升(10+10)%"
    attr.add_dmg_bonus(0.2, title, msg)

    return calc_damage_0(attr, role, isGroup)


def calc_damage_16(
    attr: DamageAttribute, role: RoleDetailData, isGroup: bool = True
) -> tuple[str, str]:
    attr.set_char_damage(liberation_damage)
    attr.set_char_template("temp_atk")

    # 守岸人buff
    shouanren_buff(attr, 0, 1, isGroup)

    # 露帕buff
    lupa_buff(attr, 0, 1, isGroup)

    # 露帕解放火队人数buff
    title = "露帕-追猎-共鸣解放"
    msg = "热熔提升10%"
    attr.add_dmg_bonus(0.1, title, msg)

    return calc_damage_1(attr, role, isGroup)


def calc_damage_17(
    attr: DamageAttribute, role: RoleDetailData, isGroup: bool = True
) -> tuple[str, str]:
    attr.set_char_damage(liberation_damage)
    attr.set_char_template("temp_atk")

    # 守岸人buff
    shouanren_buff(attr, 0, 1, isGroup)

    # 露帕buff
    lupa_buff(attr, 6, 5, isGroup)

    # 露帕解放火队人数buff
    title = "露帕-追猎-共鸣解放"
    msg = "热熔提升(10+10)%"
    attr.add_dmg_bonus(0.2, title, msg)

    return calc_damage_1(attr, role, isGroup)


damage_detail = [
    {
        "title": "焚身以火",
        "func": lambda attr, role: calc_damage_0(attr, role),
    },
    {
        "title": "离火照丹心",
        "func": lambda attr, role: calc_damage_1(attr, role),
    },
    {
        "title": "zrz总伤",
        "func": lambda attr, role: calc_damage_2(attr, role),
    },
    {
        "title": "0+1守/0船/焚身以火",
        "func": lambda attr, role: calc_damage_12(attr, role),
    },
    # {
    #     "title": "6+5守/0船/焚身以火",
    #     "func": lambda attr, role: calc_damage_13(attr, role),
    # },
    {
        "title": "0+1守/0+1露/焚身以火",
        "func": lambda attr, role: calc_damage_14(attr, role),
    },
    {
        "title": "0+1守/6+5露/焚身以火",
        "func": lambda attr, role: calc_damage_15(attr, role),
    },
    {
        "title": "0+1守/0船/离火照丹心",
        "func": lambda attr, role: calc_damage_10(attr, role),
    },
    # {
    #     "title": "6+5守/0船/离火照丹心",
    #     "func": lambda attr, role: calc_damage_11(attr, role),
    # },
    {
        "title": "0+1守/0+1露/离火照丹心",
        "func": lambda attr, role: calc_damage_16(attr, role),
    },
    {
        "title": "0+1守/6+5露/离火照丹心",
        "func": lambda attr, role: calc_damage_17(attr, role),
    },
]

rank = damage_detail[2]
