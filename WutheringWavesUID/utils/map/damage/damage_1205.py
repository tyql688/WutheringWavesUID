# 长离
from .buff import shouanren_buff, sanhua_buff
from .damage import weapon_damage, echo_damage, phase_damage
from ...api.model import RoleDetailData
from ...ascension.char import get_char_detail, WavesCharResult
from ...damage.damage import DamageAttribute
from ...damage.utils import skill_damage_calc, skill_damage, liberation_damage, \
    cast_skill, hit_damage, cast_liberation


def calc_chain(attr: DamageAttribute, role: RoleDetailData, isGroup: bool = False):
    role_name = role.role.roleName
    chain_num = role.get_chain_num()
    if chain_num >= 1 and attr.char_damage in [skill_damage, hit_damage]:
        # 1命
        title = f"{role_name}-一命"
        msg = f"施放共鸣技能赫羽三相或重击焚身以火, 伤害提升10%"
        attr.add_dmg_bonus(0.1, title, msg)

    if chain_num >= 2:
        # 2命
        title = f"{role_name}-二命"
        msg = f"获得【离火】时，长离的暴击提升25%"
        attr.add_crit_rate(0.25, title, msg)

    if chain_num >= 3 and attr.char_damage in [liberation_damage]:
        # 3命
        title = f"{role_name}-三命"
        msg = "共鸣解放离火照丹心造成的伤害提升80%。"
        attr.add_dmg_bonus(0.8, title, msg)

    if chain_num >= 4 and isGroup:
        # 4命 变奏入场
        title = f"{role_name}-四命"
        msg = f"施放变奏技能后，队伍中的角色攻击提升20%"
        attr.add_atk_percent(0.2, title, msg)

    if chain_num >= 5 and attr.char_damage in [skill_damage]:
        # 5命
        title = f"{role_name}-五命"
        msg = "重击焚身以火倍率提升50%，造成的伤害提升50%。"
        attr.add_skill_ratio(0.5)
        attr.add_dmg_bonus(0.5)
        attr.add_effect(title, msg)

    if chain_num >= 6:
        # 6命
        title = f"{role_name}-六命"
        msg = "忽视目标40%防御"
        attr.add_defense_reduction(0.4, title, msg)


def calc_damage_0(attr: DamageAttribute, role: RoleDetailData, isGroup: bool = False) -> (str, str):
    """
    焚身以火
    """
    attr.set_char_damage(skill_damage)

    role_name = role.role.roleName
    role_id = role.role.roleId
    role_level = role.role.level
    role_breach = role.role.breach
    char_result: WavesCharResult = get_char_detail(role_id, role_level, role_breach)

    # 焚身以火 技能倍率
    skillLevel = role.skillList[4].level - 1
    # 技能倍率
    skill_multi = skill_damage_calc(char_result.skillTrees, "7", "1", skillLevel)
    title = f"{role_name}-焚身以火"
    msg = f"技能倍率{skill_multi}"
    attr.add_skill_multi(skill_multi, title, msg)

    # 设置角色等级
    attr.set_character_level(role_level)

    damage_func = [cast_skill]
    phase_damage(attr, role, damage_func, isGroup)

    if role_breach and role_breach >= 3:
        # 固2(散势) 0.2
        title = f"{role_name}-固有技能-散势"
        msg = f"长离的热熔伤害加成提升20%，攻击造成伤害时忽视目标15%防御"
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


def calc_damage_1(attr: DamageAttribute, role: RoleDetailData, isGroup: bool = False) -> (str, str):
    """
    离火照丹心
    """
    attr.set_char_damage(liberation_damage)

    role_name = role.role.roleName
    role_id = role.role.roleId
    role_level = role.role.level
    role_breach = role.role.breach
    char_result: WavesCharResult = get_char_detail(role_id, role_level, role_breach)

    # 离火照丹心 技能倍率
    skillLevel = role.skillList[2].level - 1
    # 技能倍率
    skill_multi = skill_damage_calc(char_result.skillTrees, "3", "1", skillLevel)
    title = f"{role_name}-离火照丹心技能倍率"
    msg = f"{skill_multi}"
    attr.add_skill_multi(skill_multi, title, msg)

    damage_func = [cast_skill, cast_liberation]
    phase_damage(attr, role, damage_func, isGroup)

    # 设置角色等级
    attr.set_character_level(role_level)

    if role_breach and role_breach >= 3:
        # 固2(散势) 0.2
        title = f"{role_name}-固有技能-散势"
        msg = f"长离的热熔伤害加成提升20%，攻击造成伤害时忽视目标15%防御"
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


def calc_damage_2(attr: DamageAttribute, role: RoleDetailData, isGroup: bool = True) -> (str, str):
    attr.set_char_damage(skill_damage)

    # 守岸人buff
    shouanren_buff(attr, 0, 1, isGroup)

    # 散华buff
    sanhua_buff(attr, 6, 1, isGroup)

    return calc_damage_0(attr, role, isGroup)


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
        "title": "0+1守6散焚身以火",
        "func": lambda attr, role: calc_damage_2(attr, role),
    }
]
