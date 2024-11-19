# 长离
from .buff import shouanren_buff, sanhua_buff
from ...api.model import RoleDetailData
from ...ascension.char import get_char_detail, WavesCharResult
from ...damage.abstract import WavesWeaponRegister, WavesEchoRegister
from ...damage.damage import DamageAttribute
from ...damage.utils import skill_damage, SONATA_MOLTEN, check_if_ph_5


def calc_damage_0(attr: DamageAttribute, role: RoleDetailData, isGroup: bool = False) -> (str, str):
    """
    焚身以火
    """
    damage_func = "skill_damage"

    role_name = role.role.roleName
    role_id = role.role.roleId
    role_level = role.role.level
    role_breach = role.role.breach
    char_result: WavesCharResult = get_char_detail(role_id, role_level, role_breach)

    # 焚身以火 技能倍率
    skillLevel = role.skillList[4].level - 1
    # 技能倍率
    skill_multi = skill_damage(char_result.skillTrees, "7", "1", skillLevel)
    title = f"{role_name}-焚身以火"
    msg = f"技能倍率{skill_multi}"
    attr.add_skill_multi(skill_multi, title, msg)

    # 设置角色等级
    attr.set_character_level(role_level)

    for ph_detail in attr.ph_detail:
        if check_if_ph_5(ph_detail.ph_name, ph_detail.ph_num, SONATA_MOLTEN):
            # 热熔声骸五件套
            title = f"{role_name}-熔山裂谷"
            msg = f"使用共鸣技能时，热熔伤害提升30%"
            attr.add_dmg_bonus(0.3, title, msg)

    if role_breach >= 3:
        # 固2(散势) 0.2
        title = f"{role_name}-固有技能-散势"
        msg = f"长离的热熔伤害加成提升20%，攻击造成伤害时忽视目标15%防御"
        attr.add_dmg_bonus(0.2)
        attr.add_defense_reduction(0.15)
        attr.add_effect(title, msg)

    if attr.dmg_bonus_phantom and attr.dmg_bonus_phantom.skill_damage:
        # 共鸣技能伤害 ->  来自声骸
        attr.add_dmg_bonus(attr.dmg_bonus_phantom.skill_damage)

    chain_num = role.get_chain_num()
    if chain_num >= 1:
        # 1命
        title = f"{role_name}-一命"
        msg = f"伤害提升10%"
        attr.add_dmg_bonus(0.1, title, msg)

    if chain_num >= 2:
        # 2命
        title = f"{role_name}-二命"
        msg = f"获得【离火】时，长离的暴击提升25%"
        attr.add_crit_rate(0.25, title, msg)

    if chain_num >= 4 and isGroup:
        # 4命 变奏入场
        title = f"{role_name}-四命"
        msg = f"施放变奏技能后，队伍中的角色攻击提升20%"
        attr.add_atk_percent(0.2, title, msg)

    if chain_num >= 5:
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

    # 声骸技能
    echo_clz = WavesEchoRegister.find_class(attr.echo_id)
    if echo_clz:
        e = echo_clz()
        e.do_echo(damage_func, attr, isGroup)

    # 武器谐振
    weapon_clz = WavesWeaponRegister.find_class(role.weaponData.weapon.weaponId)
    if weapon_clz:
        weapon_data = role.weaponData
        w = weapon_clz(weapon_data.weapon.weaponId,
                       weapon_data.level,
                       weapon_data.breach,
                       weapon_data.resonLevel)
        w.do_action(damage_func, attr, isGroup)

    # 暴击伤害
    crit_damage = f"{attr.calculate_crit_damage():,.0f}"
    # 期望伤害
    expected_damage = f"{attr.calculate_expected_damage():,.0f}"
    return crit_damage, expected_damage


def calc_damage_1(attr: DamageAttribute, role: RoleDetailData, isGroup: bool = False) -> (str, str):
    """
    离火照丹心
    """
    damage_func = "liberation_damage"

    role_name = role.role.roleName
    role_id = role.role.roleId
    role_level = role.role.level
    role_breach = role.role.breach
    char_result: WavesCharResult = get_char_detail(role_id, role_level, role_breach)

    # 离火照丹心 技能倍率
    skillLevel = role.skillList[2].level - 1
    # 技能倍率
    skill_multi = skill_damage(char_result.skillTrees, "3", "1", skillLevel)
    title = f"{role_name}-离火照丹心技能倍率"
    msg = f"{skill_multi}"
    attr.add_skill_multi(skill_multi, title, msg)

    for ph_detail in attr.ph_detail:
        if check_if_ph_5(ph_detail.ph_name, ph_detail.ph_num, SONATA_MOLTEN):
            # 热熔声骸五件套
            title = f"{role_name}-熔山裂谷"
            msg = f"使用共鸣技能时，热熔伤害提升30%"
            attr.add_dmg_bonus(0.3, title, msg)

    # 设置角色等级
    attr.set_character_level(role_level)

    if role_breach >= 3:
        # 固2(散势) 0.2
        title = f"{role_name}-固有技能-散势"
        msg = f"长离的热熔伤害加成提升20%，攻击造成伤害时忽视目标15%防御"
        attr.add_dmg_bonus(0.2)
        attr.add_defense_reduction(0.15)
        attr.add_effect(title, msg)

    if attr.dmg_bonus_phantom and attr.dmg_bonus_phantom.liberation_damage:
        # 共鸣解放伤害 ->  来自声骸
        attr.add_dmg_bonus(attr.dmg_bonus_phantom.liberation_damage)

    chain_num = role.get_chain_num()
    if chain_num >= 2:
        # 2命
        title = f"{role_name}-二命"
        msg = f"获得【离火】时，长离的暴击提升25%"
        attr.add_crit_rate(0.25, title, msg)

    if chain_num >= 3:
        # 3命
        title = f"{role_name}-三命"
        msg = "共鸣解放离火照丹心造成的伤害提升80%。"
        attr.add_dmg_bonus(0.8, title, msg)

    if chain_num >= 4 and isGroup:
        # 4命
        title = f"{role_name}-四命"
        msg = f"施放变奏技能后，队伍中的角色攻击提升20%"
        attr.add_atk_percent(0.2, title, msg)

    if chain_num >= 6:
        # 6命
        title = f"{role_name}-六命"
        msg = "忽视目标40%防御"
        attr.add_defense_reduction(0.4, title, msg)

    # 声骸技能
    echo_clz = WavesEchoRegister.find_class(attr.echo_id)
    if echo_clz:
        e = echo_clz()
        e.do_echo(damage_func, attr, isGroup)

    # 武器谐振
    weapon_clz = WavesWeaponRegister.find_class(role.weaponData.weapon.weaponId)
    if weapon_clz:
        weapon_data = role.weaponData
        w = weapon_clz(weapon_data.weapon.weaponId,
                       weapon_data.level,
                       weapon_data.breach,
                       weapon_data.resonLevel)
        w.do_action(damage_func, attr, isGroup)

    # 暴击伤害
    crit_damage = f"{attr.calculate_crit_damage():,.0f}"
    # 期望伤害
    expected_damage = f"{attr.calculate_expected_damage():,.0f}"
    return crit_damage, expected_damage


def calc_damage_2(attr: DamageAttribute, role: RoleDetailData, isGroup: bool = True) -> (str, str):
    damage_func = "skill_damage"

    # 守岸人buff
    shouanren_buff(attr, 0, 1, isGroup, damage_func)

    # 散华buff
    sanhua_buff(attr, 6, 1, isGroup, damage_func)

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
